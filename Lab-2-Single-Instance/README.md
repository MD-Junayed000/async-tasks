# Async Task Processing System with Pulumi-Driven AWS Deployment

## Project Overview
This section demonstrates how to deploy a *Flask-based asynchronous task processing system* using AWS EC2 ,creating a VPC and public subnetting via driven by Pulumi IaC.


##  Architecture Workflow Diagram:

<img src="asset/Work.svg" alt="Broker Diagram" width="1000">

***1. Create a Virtual Private Cloud (VPC):***
The first step is setting up a VPC, which creates a private, isolated network environment for your infrastructure.

* CIDR block: 10.0.0.0/16 provides up to 65,536 private IP addresses.

* DNS hostnames and DNS resolution are enabled to allow internal name resolution across the VPC.

***2. Create a Public Subnet:***
A public subnet (10.0.0.0/24) is created inside the VPC. It supports up to 256 IP addresses and is configured with map_public_ip_on_launch = true, ensuring that EC2 instances get publicly routable IPs automatically. This subnet will host our application instance.

***3. Attach Internet Gateway (IGW):***
To allow communication between the VPC and the internet, an Internet Gateway is attached.

***4. Create a Route Table:***
Define a custom Route Table that routes all outbound internet traffic (0.0.0.0/0) through the Internet Gateway.

***5. Associate the Route Table to the Subnet:***
The route table is explicitly associated with the public subnet. This enables the subnet to act as a public-facing zone, meaning any EC2 instance inside can communicate over the internet.

***6. Create a Security Group (Firewall):***
A Security Group is created to allow only necessary inbound traffic:

* Port 22 – For SSH access to the EC2 instance

* Port 5000 – Flask web interface

* Port 15672 – RabbitMQ Admin UI

* Port 5672 – RabbitMQ message broker port used by Celery

* Port 5555 – Flower monitoring dashboard
All outbound traffic is permitted by default.

***7. Create a Key Pair:***
Pulumi checks for an existing SSH public key (e.g., ~/.ssh/id_rsa.pub) or creates a new one.
This key pair allows secure SSH access to the EC2 instance for administration and manual debugging.

***8. Launch an EC2 Instance:***
Pulumi fetches the latest Ubuntu AMI published by Canonical. An EC2 instance is launched with:

* Public IP for browser and SSH access

* Association with the VPC, public subnet, and security group

* SSH Key Pair attached

* All services—Flask, Celery, Redis, RabbitMQ, Flower—run inside Docker containers on this machine

This instance hosts the entire async task system, handling API requests, task queuing, execution, and monitoring.

***9. Expose Dockerized System to the Internet:***
The EC2 instance acts as a single-node host for the Dockerized stack:
Flask API receives tasks,Celery workers execute jobs,Redis stores results,RabbitMQ routes task queues,Flower offers real-time monitoring.

Each service is mapped to its respective port and made accessible via the EC2's public IP.




***10. Exporting Outputs for Easy Access:***
When pulumi up is executed, Pulumi prints the outputs:

* EC2 Public IP (e.g., http://18.XXX.XXX.XX)

* EC2 Public DNS (e.g., ec2-XX-XX-XX.compute.amazonaws.com)

These URLs allow:

* http://<public_ip>:5000 → Flask UI

* http://<public_ip>:15672 → RabbitMQ Admin Panel

* http://<public_ip>:5555 → Flower Monitoring Dashboard


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

##  Step-by-Step Setup (Local + AWS EC2 Deployment) : 


###  1. Prerequisites (on your machine)
Make sure you’ve:

AWS CLI installed 

Pulumi CLI installed 

Docker installed and working

~~ At First from the lab generate the Credentials get the access ID and Secret keys
![Screenshot 2025-06-03 232530](https://github.com/user-attachments/assets/4968a08b-e35a-4795-8de5-531493a8dccc)


~~ AWS Configuration from the terminal:
```bash

aws configure # Use credentials from Poridhi Lab or IAM keys

```
<div align="center">
  <img src="https://github.com/user-attachments/assets/3464361a-f40e-460a-afb0-2d421a528f6e" alt="Screenshot 2025-06-03 232610" width="700">
</div>


### 📁 2.Initialize Pulumi Project
```bash
mkdir async-task-infra
cd async-task-infra
pulumi new aws-python

```
For First-time login need to generate tokens:

<div align="center">
  <img src="https://github.com/user-attachments/assets/4e6dccad-d64e-4506-b02e-e59564b47a58" alt="image">
</div>



**Respond to prompts:**

* Project name: async-task-infra

* Stack: dev (can create your new stack with name of desired)

* AWS region: ap-southeast-1 



![Screenshot 2025-06-03 232744](https://github.com/user-attachments/assets/34455207-428d-4fea-a2d2-64f1aec124ed)



## 3. Create Python Virtual Environment

On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.
-  1. Update your package index
```bash

sudo apt update
```
- 2. Install Python 3 and pip
```bash

sudo apt install -y python3 python3-pip
```
- 3. Install venv module for Python 3
```bash

sudo apt install -y python3-venv
```
>>If you're on Ubuntu 22.04 or later, these commands will work out of the box.

Then create a virtual environment:
```bash

python3 -m venv venv
```
- on Windows
```bash
venv\Scripts\activate    
```
- OR # on Linux/Mac
```bash
source venv/bin/activate  
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
) ## for working in windows :public_key = open(os.path.expanduser("~/.ssh/id_rsa.pub")).read()

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
    git clone https://github.com/MD-Junayed000/async-tasks.git
    cd async-tasks
    cd Lab-1-Async-Tasks/Async-tasks ### SEE LAB-1
    sudo docker-compose up -d
    """,
    tags={"Name": "async-task-ec2"})

#  10. Export Public IP & DNS
pulumi.export("public_ip", instance.public_ip)
pulumi.export("public_dns", instance.public_dns)

```
## 5. Generating a valid SSH key and fixing the path.
***🔧 Step 1: Generate a Key Pair***

In the terminal (still in /root/code/):
```bash
ssh-keygen -t rsa -b 2048 -f /root/code/id_rsa -N ""
```
This creates:

* ✅ /root/code/id_rsa → private key

* ✅ /root/code/id_rsa.pub → public key

***Step 2: Confirm the file exists***
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
you should see a output like this:
![image](https://github.com/user-attachments/assets/e0eb11b7-4fc1-44c0-b267-1d2407d82b66)

✅ You will get public_ip of the EC2 instance.

## 7. SSH Into EC2 and Set Up Dockerized Project
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
## 8. Access Your Flask App & Flower
* Flask UI: http://<public_ip>:5000 (demo ![image](https://github.com/user-attachments/assets/7c27d753-9b1b-4878-a346-f65df13deb57) )


* Flower: http://<public_ip>:5555

* RabbitMQ: http://<public_ip>:15672 (guest/guest)

## 9. Postman API Testing
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


## Cleanup AWS
```bash
pulumi destroy --yes  # Destroys everything
```



## Summary
This project showcases a full *production-style async task pipeline* with modular design, reliable messaging, and full automation via *Pulumi Infrastructure-as-Code*.






