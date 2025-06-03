# Async Task Processing System with Flask, Celery, RabbitMQ & Pulumi-Driven AWS Deployment

## Project Overview
This section demonstrates how to deploy a *Flask-based asynchronous task processing system* using AWS EC2 ,creating a VPC and public subnetting via driven by Pulumi IaC.


##  Architecture Workflow Diagram:

<img src="asset/Cloud.svg" alt="Broker Diagram" width="1000">

***1. Create a Virtual Private Cloud (VPC):***

* Creates a private isolated network for the application.
* 10.0.0.0/16: IP range allowing 65,536 IPs.

* DNS support helps EC2 use names (not just IPs).

***2. Create a Public Subnet:***

* Subnet range: 10.0.1.0/24 (256 IPs).

* Allows EC2 instances to get public IPs with map_public_ip_on_launch=True. and deploying our project under these instance.
***3. Attach Internet Gateway (IGW):***
* Internet Gateway gives the VPC access to the internet.

* Required for apt install, Docker pulls, etc.

***4. Create a Route Table:***

* Defining that all external traffic (0.0.0.0/0) is routed through the Internet Gateway.

***5. Associate the Route Table to the Subnet:***

* Links the route table to your subnet.

* Enables public internet routing for EC2s in the subnet.

***6. Create a Security Group (Firewall Rules):***
* Allows traffic inbound to:

>>SSH (22) → For EC2 login

>>Flask (5000) → Web interface

>>RabbitMQ UI (15672)

>>Flower dashboard (5555)

>>RabbitMQ (5672) for Celery message passing

* Egress: All outbound traffic is allowed.

***7. Create a Key Pair:***
* Create or reads the existing public key from ~/.ssh/id_rsa.pub.
* Ensuresing can SSH into your EC2 instance securely.

***8. Launch an EC2 Instance:***

Fetching the latest Ubuntu AMI (Amazon Machine Image) from Canonical.	The generated SSH key (~/.ssh/id_rsa.pub) is uploaded to create a new EC2 Key Pair.EC2 instance is created with:
- VPC & Public Subnet association
- Security Group allowing ports 22, 5000, 5672, 15672, 5555
- Public IP to access it from browser or SSH
~~
>>* Entire asynchronous task processing system is deployed and run here.
>>*  Handles HTTP Requests and Communicates With Internet.
>>* Provides Secure Access and Stores Application Files Temporarily.



***10. Exporting Outputs for Easy Access:***

* When run pulumi up, we'll get:

>>EC2's Public IP

>>EC2's DNS

* Then Open:

>>http://<public_ip>:5000 → Flask UI

>>http://<public_ip>:15672 → RabbitMQ UI

>>http://<public_ip>:5555 → Flower


***This project uses Pulumi (IaC) tool to define, deploy, and manage cloud infrastructure ( EC2, VPC, S3, etc.) using  programming languages Python.Pulumi Resource Breakdown:***

| Pulumi Code                             | What It Does                                                                 |
|----------------------------------------|------------------------------------------------------------------------------|
| `aws.ec2.Vpc(...)`                     | Creates a **Virtual Private Cloud (VPC)** — an isolated network for all your resources. |
| `aws.ec2.Subnet(...)`                  | Defines a **Public Subnet** inside the VPC where your EC2 will live.     |
| `aws.ec2.InternetGateway(...)`         | Adds an **Internet Gateway** so instances can access the Internet.       |
| `aws.ec2.RouteTable(...)`              |  Adds a **route to 0.0.0.0/0** (i.e., full internet access) via the gateway. |
| `aws.ec2.SecurityGroup(...)`           |  Opens specific ports (22, 5000, 5672, 15672, 5555) — for **SSH, Flask, RabbitMQ, Flower**, etc. |
| `aws.ec2.Instance(...)`                |  Launches a **t2.micro EC2 instance** using Ubuntu. Pulls your app repo and starts containers via `docker-compose`. |
| `pulumi.export(...)`                   |  Outputs the **public IP & DNS** of the EC2 so you can access your app from a browser. |

thus instead of clicking buttons on the AWS console Pulumi  build the AWS environment using Python scripts where the Dockerized Flask-Celery app now runs on EC2 with full network access and monitoring.

This Setup can be verified by the created resources such as VPC, Subnet, EC2 instance using AWS console.
![overall#](https://github.com/user-attachments/assets/ae14c00e-886a-4a9e-a880-7496e8d93576)

![image](https://github.com/user-attachments/assets/d96e5039-681e-45cb-b536-cb384d07d782)



## Folder Structure
async-stack-infra/
  ├── __main__.py (Pulumi infra code)
  ├── Pulumi.yaml
  ├── Pulumi.dev.yaml
  └── requirements.txt


## Features
- Submit 3 types of async tasks from Flask UI:
  - Send Email
  - Reverse Text
  - Sentiment Analysis
- Get instant task submission notification ✅ or ❌
- Task status + result query via UI or endpoint
- Dashboard to monitor task lifecycle in Flower
- Full AWS provisioning using Pulumi in Python

---

##  Step-by-Step Setup (Local + AWS EC2 Deployment) using the Poridhi.io AWS NEtworking Lab (Launch An Ec2 Instance In A Virtual Private Cloud (vpc): 


### ✅ 1. Prerequisites (on your machine)
Make sure you’ve:

AWS CLI installed 

Pulumi CLI installed 

Docker installed and working

~~ At First from the lab generate the Credentials get the access ID and Secret keys
![Screenshot 2025-06-03 232530](https://github.com/user-attachments/assets/4968a08b-e35a-4795-8de5-531493a8dccc)


~~AWS Configuration form the terminal:
```bash

aws configure # Use credentials from Poridhi Lab or IAM keys

```
![Screenshot 2025-06-03 232610](https://github.com/user-attachments/assets/3464361a-f40e-460a-afb0-2d421a528f6e)

### 📁 2.Initialize Pulumi Project
```bash
mkdir async-task-infra
cd async-task-infra
pulumi new aws-python

```
![Screenshot 2025-06-03 232744](https://github.com/user-attachments/assets/34455207-428d-4fea-a2d2-64f1aec124ed)

**Respond to prompts:**

* Project name: async-task-infra

* Stack: dev

* AWS region: ap-southeast-1


## 3. Create Python Virtual Environment
```bash

python -m venv venv
venv\Scripts\activate    # on Windows
# OR
source venv/bin/activate  # on Linux/Mac
```
Install required packages:
```bash
pip install pulumi pulumi_aws
# or
pip install -r requirements.txt
```
## 4. Define Infrastructure (__main__.py):

Replace __main__.py with this:
```bash

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
    public_key=open("/root/code/id_rsa.pub").read()
)

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

```
### 5. Generating a valid SSH key and fixing the path.
***🔧 Step 1: Generate a Key Pair***
In the terminal (still in /root/code/):
```bash
ssh-keygen -t rsa -b 2048 -f /root/code/id_rsa -N ""
```
- This creates:

-- ✅ /root/code/id_rsa → private key

-- ✅ /root/code/id_rsa.pub → public key

***🔧 Step 2: Confirm the file exists***
```bash
ls -l /root/code/id_rsa.pub
```
should see a line like:
```bash
-rw------- 1 root root 426 Jun 4 10:23 /root/code/id_rsa.pub

```
![Screenshot 2025-06-04 004053](https://github.com/user-attachments/assets/ed907d21-a57b-4606-963d-36e1fd280903)

## 6. Deploy Infrastructure
```bash

pulumi up --yes
```
✅ You will get public_ip of the EC2 instance.

## 6. SSH Into EC2 and Set Up Dockerized Project
```bash

ssh -i /root/code/id_rsa ubuntu@<public_ip>
```
🔒 Optional: Fix Permissions
If it still says “unprotected private key”, run:

```bash
chmod 400 /root/code/id_rsa
```
Then try again:
```bash
ssh -i /root/code/id_rsa ubuntu@<public_ip>
```

Then inside EC2:

```bash

# Install Docker
sudo apt update && sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu
```
then
```bash
git clone https://github.com/MD-Junayed000/async-tasks.git
cd async-tasks
cd Lab-1-Async-Tasks/Async-tasks
sudo docker-compose up -d
```
## 7. Access Your Flask App & Flower
* Flask UI: http://<public_ip>:5000

* Flower: http://<public_ip>:5555

* RabbitMQ: http://<public_ip>:15672 (guest/guest)

## 8. Postman API Testing
If want to expose APIs (/submit, /check_status/<id>),  can now use Postman to:

* Submit task via POST /submit

* Check task result via GET /check_status/<task_id>



# 🔄 Task Workflow (Internals)

User -> Flask UI -> Celery .delay() -> RabbitMQ (queue) -> Celery Worker -> Redis (result)
                                                  └-> Flower for Monitoring


- *Flask*: Handles UI/API + user interaction
- *Celery*: Picks task from queue, processes it
- *RabbitMQ*: Message Queue between Flask & Celery
- *Redis*: Tracks status & stores result



##  Debugging Tips
| Problem                        | Fix                                                      |
|-------------------------------|-----------------------------------------------------------|
| Task stuck in PENDING         | Check if Celery worker is running                         |
| Cannot access Flask on EC2    | Ensure Flask binds host='0.0.0.0' + Security Group open |
| Docker fails to start         | Run sudo docker-compose down -v && up --build -d       |
| SSH access denied             | Check key path and permissions chmod 400 id_rsa         |
|If Pulumi fails                | try pulumi destroy to clean up, then pulumi up again    |
---

## Cleanup AWS
```bash
cd async-stack-infra
pulumi destroy   # Destroys everything
```

---

## Future Enhancements
- Adding S3 for file upload task 
- Add auto-retry + failure queue 
- Persist task logs to S3 
- UI improvement with live polling  

---

---

## Summary
This project showcases a full *production-style async task pipeline* with modular design, reliable messaging, and full automation via *Pulumi Infrastructure-as-Code*.



## License

MIT License © 2025 [poridhi.io](https://poridhi.io)
