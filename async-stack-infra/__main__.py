import pulumi
import pulumi_aws as aws
import os
# 1. Create VPC
vpc = aws.ec2.Vpc("task-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": "task-vpc"})

#  2. Public Subnet
subnet = aws.ec2.Subnet("task-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    availability_zone="ap-southeast-1a",
    tags={"Name": "task-subnet"})

#  3. Internet Gateway
igw = aws.ec2.InternetGateway("task-igw",
    vpc_id=vpc.id,
    tags={"Name": "task-igw"})

#  4. Route Table
route_table = aws.ec2.RouteTable("task-rt",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0",
        "gateway_id": igw.id,
    }],
    tags={"Name": "task-rt"})

#  5. Associate Route Table to Subnet
aws.ec2.RouteTableAssociation("task-rt-assoc",
    subnet_id=subnet.id,
    route_table_id=route_table.id)

# 6. Security Group (allow SSH + web ports)
sec_group = aws.ec2.SecurityGroup("task-sg",
    vpc_id=vpc.id,
    description="Allow SSH, Flask, RabbitMQ, Flower",
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 5000, "to_port": 5000, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 15672, "to_port": 15672, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 5555, "to_port": 5555, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 5672, "to_port": 5672, "cidr_blocks": ["0.0.0.0/0"]}
    ],
    egress=[{
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"]
    }],
    tags={"Name": "task-secgroup"})

#  7. AMI (Ubuntu 22.04)
ami = aws.ec2.get_ami(most_recent=True,
                      owners=["099720109477"],
                      filters=[
                          {"name": "name", "values": ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]},
                      ])

# 8. EC2 Key Pair (use your existing PEM key if available)
key_pair = aws.ec2.KeyPair("task-key",
    public_key = open(os.path.expanduser("~/.ssh/id_rsa.pub")).read())

# 9. EC2 Instance
instance = aws.ec2.Instance("task-ec2",
    ami=ami.id,
    instance_type="t2.micro",
    subnet_id=subnet.id,
    vpc_security_group_ids=[sec_group.id],
    associate_public_ip_address=True,
    key_name=key_pair.key_name,
    user_data="""
    #!/bin/bash
    sudo apt update
    sudo apt install docker.io docker-compose git -y
    git clone https://github.com/YOUR_USERNAME/async-tasks.git /home/ubuntu/async-tasks
    cd /home/ubuntu/async-tasks
    sudo docker-compose up -d
    """,
    tags={"Name": "async-task-ec2"})

#  10. Export Public IP & DNS
pulumi.export("public_ip", instance.public_ip)
pulumi.export("public_dns", instance.public_dns)
