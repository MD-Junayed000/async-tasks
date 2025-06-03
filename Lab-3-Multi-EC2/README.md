#  Asynchronous Task Processing System using Flask, Celery, RabbitMQ, Redis, Flower & Pulumi-AWS Multi-EC2 Deployment

##  Project Overview
> Unlike monolithic deployments, this design runs each component in **separate EC2 instances** within a shared VPC , created and managed automatically using Pulumi:
- `flask-ec2`: Flask frontend/UI
- `rabbitmq-ec2`: Central message broker (Celery tasks get queued here)
- `redis-ec2`: Redis stores task results
- `worker1-ec2`, `worker2-ec2`: Celery workers (pull tasks from broker)
- `flower-ec2`: Task monitoring dashboard

All EC2s are Dockerized and orchestrated using `docker-compose` profiles.

---

##  Architecture Diagram

<img src="assets/Multi.svg" alt="Implementation Diagram" width="1000" >



## How the System is Structured

### 🧱 Infrastructure (via `async-stack-Multi-EC2/__main__.py`)

1. **VPC Creation (`10.0.0.0/16`)**
   - Isolated virtual network for all EC2 instances.
   - DNS support is enabled for name resolution.

2. **Subnet (`10.0.1.0/24`)**
   - Public subnet for launching EC2s with public IPs.
   - `map_public_ip_on_launch=True` to auto-assign public IP.

3. **Internet Gateway**
   - Allows EC2s to access the internet (e.g., apt, pip, git, Docker).

4. **Route Table**
   - Routes all internet-bound traffic (`0.0.0.0/0`) through the Internet Gateway.

5. **Security Group**
   - Allows:
     - SSH (22)
     - Flask (5000)
     - RabbitMQ: AMQP (5672), UI (15672)
     - Flower dashboard (5555)
     - Redis (6379)
   - Allows all outbound traffic.

6. **SSH Key Pair**
   - Reads `~/.ssh/id_rsa.pub` to create a key pair for secure login.

7. **Docker Startup Scripts per EC2**
   - Uses a `make_script()` function to:
     - Install Docker & Compose
     - Clone GitHub repo
    - Injects rabbitmq_ip and redis_ip into celeryconfig.py
    - Builds and runs only the necessary service using docker-compose --profile <service>
This allows:
•	flask EC2 to run only Flask
•	worker1 and worker2 to run Celery workers
•	flower EC2 to monitor everything
•	Each EC2 gets only what it needs — reducing overhead

8. **Six EC2 Instances Created**
   - `rabbitmq-ec2`
   - `redis-ec2`
   - `flask-ec2`
   - `worker1-ec2`
   - `worker2-ec2`
   - `flower-ec2`

**The setup should show like this in AWS console:**
![image](https://github.com/user-attachments/assets/cb4186f3-9521-40f3-87b2-c06be97af759)
![image](https://github.com/user-attachments/assets/20a03bca-2618-4709-b06b-5e694e7eb23b)


9.**Expose Public IPs for Access**
- Outputs the public IPs of all EC2s after deployment.
- Can directly visit:
  •	http://<flask-ip>:5000 → Flask UI
  •	http://<flower-ip>:5555 → Flower
  •	http://<rabbit-ip>:15672 → RabbitMQ dashboard


---

### 🐳 Docker Application (`async-tasks/docker-compose.yml`)

Each service has its own profile:

- `flask`: Flask app and task submission UI (port 5000)
- `rabbitmq`: Broker + management UI (5672, 15672)
- `redis`: Stores Celery task results (6379)
- `celery`: Worker consuming tasks (`-Q celery_see`)
- `flower`: Monitoring dashboard for Celery tasks (5555)

---

### 🔗 Celery Configuration (`async-tasks/app/celeryconfig.py`)

```python
# Multi-Instance Config
broker_url = 'amqp://guest:guest@<BROKER_IP>:5672//'
result_backend = 'redis://<REDIS_IP>:6379/0'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Dhaka'
task_default_queue = 'celery_see'
```

This is automatically patched in each instance during boot with correct IPs of RabbitMQ and Redis.

---

## 📦 Folder Structure

```
async-tasks/
  ├── docker-compose.yml
  ├── app/
  │   └── celeryconfig.py

async-stack-Multi-EC2/
  ├── __main__.py
  ├── Pulumi.yaml
  ├── Pulumi.dev.yaml
  └── requirements.txt
```

---

##  Deploy the System (Step-by-Step)

###  1. Prerequisites
- AWS CLI configured (`aws configure`)
- Pulumi installed (`npm install -g pulumi`)
- Docker installed
- SSH key: `~/.ssh/id_rsa.pub`
###  2. Initialize Pulumi
```bash
mkdir async-stack-Multi-EC2 && cd async-stack-Multi-EC2
pulumi new aws-python
```
Replace __main__.py with given full script.

### 3. Setup Python Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windowspip install -r requirements.txt
```

### 4. Deploy Full Infrastructure

```bash
pulumi up --yes
```

You’ll get public IPs of each EC2 instance:
- Flask UI: http://<Flask-IP>:5000
- Flower: http://<Flower-IP>:5555
- RabbitMQ UI: http://<RabbitMQ-IP>:15672 (guest/guest)
### 5. Connect & Monitor
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<Flask_Public_IP>
cat /home/ubuntu/startup.log
```
---
## Internals — Task Flow
<img src="assets/Multi-flow.jpg" alt="Implementation Diagram" align="center" width="500" >

•	RabbitMQ: Handles queues

•	Celery: Executes tasks

•	Redis: Stores task states & results

•	Flower: Visual task monitoring



##  What Happens Behind the Scenes

- **Pulumi provisions** a full cloud network and injects broker/result IPs into each EC2.
- **Each EC2** builds only its required service with Docker Compose profiles.
- **Workers connect** to RabbitMQ on a separate instance and store results in Redis on another instance.
- **Flask web UI** submits tasks and displays results using Redis.



##  Cleanup AWS Resources
```bash
pulumi destroy --yes
```


---

##  Summary

 This project showcases:
- **Distributed Celery architecture**
- **Full automation** with Pulumi (no manual AWS console clicks)
- **Service isolation** (1 EC2 per service)
- **Monitoring** via Flower
- **Scalable and modular async task processing**

---

##  License

MIT License © 2025 [poridhi.io](https://poridhi.io)



