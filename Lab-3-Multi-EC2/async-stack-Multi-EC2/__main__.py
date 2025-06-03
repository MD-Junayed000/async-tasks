import pulumi
import pulumi_aws as aws
import os

# Ubuntu 22.04 AMI
ami = aws.ec2.get_ami(most_recent=True,
    owners=["099720109477"],
    filters=[{"name": "name", "values": ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]}]
)

# VPC & Networking
vpc = aws.ec2.Vpc("vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": "async-vpc"}
)

# Subnet
subnet = aws.ec2.Subnet("subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    tags={"Name": "async-subnet"}
)

# Internet Gateway
igw = aws.ec2.InternetGateway("igw",
    vpc_id=vpc.id,
    tags={"Name": "async-igw"}
)

# Route Table
route_table = aws.ec2.RouteTable("route-table",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0",
        "gateway_id": igw.id,
    }],
    tags={"Name": "async-rt"}
)

# Route Table Association
aws.ec2.RouteTableAssociation("route-table-assoc",
    subnet_id=subnet.id,
    route_table_id=route_table.id,
    opts=pulumi.ResourceOptions(additional_secret_outputs=["route_table_id"])
)


# Security Group
sec_group = aws.ec2.SecurityGroup("secgroup",
    vpc_id=vpc.id,
    description="Allow required ports",
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 5000, "to_port": 5000, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 5555, "to_port": 5555, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 5672, "to_port": 5672, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 15672, "to_port": 15672, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 6379, "to_port": 6379, "cidr_blocks": ["0.0.0.0/0"]},
    ],
    egress=[{"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]}],
    tags={"Name": "async-secgroup"}
)

# SSH Key
key_pair = aws.ec2.KeyPair("ssh-key", public_key=open(os.path.expanduser("~/.ssh/id_rsa.pub")).read())

# startup script
def make_script(service, rabbitmq_ip="", redis_ip=""):
    # Determine which additional profiles are needed
    extra_profiles = ""
    if service == "flask" or service == "flower" or service == "celery":
       extra_profiles = "--profile rabbitmq --profile redis"

    return f"""#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# Install Docker + Compose v2
apt update -y
apt install -y docker.io git curl
systemctl start docker
usermod -aG docker ubuntu
sleep 30

# Install Docker Compose v2
curl -L https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Setup project
cd /home/ubuntu
git clone https://github.com/MD-Junayed000/async-tasks.git
cd async-tasks

# Inject broker and redis IPs
sed -i 's|<BROKER_IP>|{rabbitmq_ip}|g' app/celeryconfig.py
sed -i 's|<REDIS_IP>|{redis_ip}|g' app/celeryconfig.py

# Logging everything
echo "==== STARTUP LOG for {service} ====" >> /home/ubuntu/startup.log
docker-compose {extra_profiles} --profile {service} build >> /home/ubuntu/startup.log 2>&1
docker-compose {extra_profiles} --profile {service} up -d >> /home/ubuntu/startup.log 2>&1
"""




#  EC2 instance function
def create_instance(name, script):
    return aws.ec2.Instance(name,
        ami=ami.id,
        instance_type="t2.micro",
        subnet_id=subnet.id,
        associate_public_ip_address=True, ### request a public IP address assigned by AWS during launch
        vpc_security_group_ids=[sec_group.id],
        key_name=key_pair.key_name,
        user_data=script,
        tags={"Name": name}
    )

# 1. RabbitMQ EC2
rabbitmq_script = make_script("rabbitmq")
rabbitmq = create_instance("rabbitmq-ec2", rabbitmq_script)

# 2. Redis EC2
redis_script = make_script("redis")
redis = create_instance("redis-ec2", redis_script)

# 3. Flask EC2
flask_script = pulumi.Output.all(rabbitmq.public_ip, redis.public_ip).apply(
    lambda ips: make_script("flask", ips[0], ips[1])
)
flask = create_instance("flask-ec2", flask_script)

# 4. Worker1 EC2
worker1_script = pulumi.Output.all(rabbitmq.public_ip, redis.public_ip).apply(
    lambda ips: make_script("celery", ips[0], ips[1])
)
worker1 = create_instance("worker1-ec2", worker1_script)

# 5. Worker2 EC2
worker2_script = pulumi.Output.all(rabbitmq.public_ip, redis.public_ip).apply(
    lambda ips: make_script("celery", ips[0], ips[1])
)
worker2 = create_instance("worker2-ec2", worker2_script)

# 6. Flower EC2
flower_script = pulumi.Output.all(rabbitmq.public_ip, redis.public_ip).apply(
    lambda ips: make_script("flower", ips[0], ips[1])
)
flower = create_instance("flower-ec2", flower_script)

# Outputs
pulumi.export("Flask Public IP", flask.public_ip)
pulumi.export("RabbitMQ IP", rabbitmq.public_ip)
pulumi.export("Redis IP", redis.public_ip)
pulumi.export("Worker1 IP", worker1.public_ip)
pulumi.export("Worker2 IP", worker2.public_ip)
pulumi.export("Flower IP", flower.public_ip)
