# Async Task Processing System with Flask, Celery, RabbitMQ & Pulumi-Driven AWS Deployment

This project demonstrates a production-ready asynchronous task processing system (i.e Deployed in EC2 using Pulumi explained in infra-branch) using:

* ✅ Flask (Web + API)
* ✅ Celery (Task Queue Executor)
* ✅ RabbitMQ (Message Broker)
* ✅ Redis (Result Backend)
* ✅ Flower (Monitoring UI)
* ✅ Docker (Multi-service orchestration)


## Table of Contents

- [🎯 Project Overview](#-project-overview)
- [System Architecture](#-system-architecture)
- [ Project Features](#-project-features)
- [ Components](#-components)
- [📁 Project Structure](#-project-structure)
- [🛠️ Step-by-Step Setup](#-step-by-step-setup)
- [🌐 URLs & Ports](#-urls--ports)
- [ Poridhi Lab Setup](#-poridhi-lab-setup)
- [ Application API Endpoints](#-application)



## 🎯 Project Overview

This project is divided into 3 Labs, each Lab shows various implementation with techonology tools:

- **Lab-1-Async-Tasks**: System Design in Local machine and Poridhi lab implementation ([Read more](README.md))
- **Lab-2-Single-Instance**: Pulumi-Driven AWS Deployment steps (single EC2 instance) ([Read more](https://github.com/MD-Junayed000/async-tasks/blob/main/Lab-2-Single-Instance/README.md))
- **Lab-3-Multi-EC2**: Multi-EC2 instance deployment ([Read more](https://github.com/MD-Junayed000/async-tasks/blob/main/Lab-3-Multi-EC2/README.md))




>  **Objective**: Design a system that allows users to submit tasks asynchronously from a Flask API, execute them reliably in the background using Celery, queue tasks in RabbitMQ, and store task states and results in a backend db (redis).

---

##  System Architecture :
<img src="assets/implement.svg" alt="Implementation Diagram" width="1000">

***1. User Request via API :***

→ Sends request from UI (email, text reverse, sentiment).

***2. Flask App :***

→ Receives request and pushes task to Celery using delay()

→ Immediately responds to user (non-blocking).

***3. Celery Producer Role (📩 Task Sent to Broker):***

→  When .delay() is called in Flask,  celery sends the task to RabbitMQ (the message broker).

→ So, Flask acts as the Producer in this diagram.

***4. RabbitMQ Queue (Message Broker):***

→ Holds tasks in queue(s).

→ Forwards them to Celery Worker.

***5. Celery Workers:***

→ Continuously listens to RabbitMQ.

→ Pulls and executes tasks (email/text/sentiment).

→ Can run multiple processes (parallel).



***6. Redis (Result Backend):***

→ Stores task result/status (e.g., SUCCESS, FAILURE).

→ Flask can query result using ***AsyncResult.***

***7. UI Feedback:***

→ Task ID flashed in UI.

→ Success/failure notification shown based on result from Redis.

---
## Project Features :
* 📨 Async Email Sender with retry logic

* 🔁 Reverse Text Processor * 💬 Fake Sentiment Analyzer

* 🔁 Redis-based task result storage

* 📊 Live task monitoring via Flower

* 🧪 Task inspection via Redis

* 🖥️ UI with feedback using Flask + Bootstrap

* 🐳 Docker-based deployment


### 🔧 Components :

| Component    | Role                                 |
| ------------ | ------------------------------------ |
| **Flask**    | UI, task submission, status fetch    |
| **Celery**   | Task execution engine                |
| **RabbitMQ** | Message broker to queue tasks        |
| **Redis**    | Stores task status & results         |
| **Flower**   | Real-time task monitoring dashboard  |
| **Docker**   | Container orchestration for services |




###  Queues and Exchange in RabbitMQ

<img src="assets/Broker.svg" alt="Broker Diagram" width="700">

* Celery uses a direct exchange

* Tasks routed by name → bound to celery_see queue

* Each worker listens on that queue

>> In RabbitMQ:

* Producer = Flask (via Celery)

* Consumer = Celery Worker

* Exchange = Implicit direct exchange

* Queue = celery_see (task queue)





## 📁 Project Structure

```
async-tasks/
│
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── celeryconfig.py      # Celery broker/backend configs
│   ├── routes.py            # Routes for UI + task handling
│   ├── tasks.py             # Celery tasks
│   ├── templates/           # Jinja2 HTML UI (index.html)
│   └── static/              # CSS, images, icons
│
├── Dockerfile               # Docker image setup
├── docker-compose.yml       # Multi-service Docker config
├── requirements.txt         # Python dependencies
├── run.py                   # Flask run entry
├── start.sh / start.ps1     # Quick Docker starter script

```

---



---

## Step-by-Step Setup

### 1️⃣ Clone the Repo and Navigate

```bash
git clone https://github.com/MD-Junayed000/async-tasks.git
cd async-tasks
cd Lab-1-Async-Tasks/Async-tasks
```

### 2️⃣ Start Services via Docker

```bash
docker-compose up --build
```



## 🌐 URLs & Ports

| Service        | URL                                              |
| -------------- | ------------------------------------------------ |
| Flask UI       | [http://localhost:5000](http://localhost:5000)   |
| RabbitMQ Admin | [http://localhost:15672](http://localhost:15672) |
| Flower Monitor | [http://localhost:5555](http://localhost:5555)   |



##  Available Tasks

| Task Type        | Description                           |
| ---------------- | ------------------------------------- |
| **Send Email**   | Simulates sending an email (w/ retry) |
| **Reverse Text** | Reverses any string                   |
| **Sentiment**    | Fake sentiment analysis on input text |

Each task returns a `Task ID` and status message ✅/❌.

---

## Poridhi Lab Setup

1. Access the application through load balancer:
At first we load the system following the instructions as in local machine and checking if all the ports are forwarded
![image](https://github.com/user-attachments/assets/7e400c90-6b9e-4787-8416-12f10e29657c)

2.Configure IP and port:
- Get IP from eth0 using `ifconfig`

![WhatsApp Image 2025-06-03 at 15 58 00_f2d59dd0](https://github.com/user-attachments/assets/c007ea7b-90ba-4270-a214-0e7b24545a1a)
- Use application port from Dockerfile

3. Create load balancer and Configure with your application's IP and port in Poridhi lab:
![Screenshot 2025-06-03 155900](https://github.com/user-attachments/assets/aec14ae4-a1d6-405b-aa52-e710c5a9ece5)

![image](https://github.com/user-attachments/assets/f7786750-1b00-4e37-86a1-34744d5b7cb4)

---
## Appication
### API Endpoints
**Submit a Task:** Submit any sorts of task like Email,Reverse text proessing,Sentiment analysis if text contain 'good'keywords.If 'fail' keyword in email receipent,it will raise error and will retry max 3 times then discarded.
Domain name for a load balancer in the Poridhi lab environment (For 5000 port):https://67aa3ccddb2c69e7e975ceff-lb-803.bm-southeast.lab.poridhi.io/
   
![Screenshot 2025-06-03 192518](https://github.com/user-attachments/assets/6054e0c2-23f9-4f16-8fd2-e99298c52616)


##  Task Monitoring with Flower

* Open the load balancer for port 5555 in the poridhi lab environment:https://67aa3ccddb2c69e7e975ceff-lb-751.bm-southeast.lab.poridhi.io/tasks

  ![Screenshot 2025-06-03 192629](https://github.com/user-attachments/assets/2dbf9954-abf7-4611-af9f-8e9be87efc2b)

* View task history, retries, failures
* Inspect live workers and system load

## RabbitMQ Management UI
-Default credentials: guest/guest
-Monitor queues, exchanges, and connections
![Screenshot 2025-06-03 192604](https://github.com/user-attachments/assets/66837fde-a699-4a30-afab-009b97812658)


## Error Handling & Retries
>Email task uses self.retry() with max_retries=3

>If task fails, it's requeued

>Redis tracks the task state:

*PENDING, SUCCESS, RETRY, FAILURE
![Screenshot 2025-06-03 192859](https://github.com/user-attachments/assets/c33a9312-de04-4305-b0d6-40a9be625430)


> inspect it using:

```bash
docker exec -it async-tasks-redis-1 redis-cli
> KEYS *
> GET celery-task-meta-xxxxxxx
```


###  Use Postman for Submissions

Example JSON for email:

```json
{
  "form_type": "email",
  "recipient": "someone@example.com",
  "subject": "Greetings",
  "body": "Hello from Flask"
}
```

---
## ⚠️ Common Issues & Fixes

| Problem                 | Fix                                    |
| ----------------------- | -------------------------------------- |
| Task not completing     | Check RabbitMQ & Celery logs           |
| Task stuck in `PENDING` | Check Redis config or broker queue     |
| No Redis output         | Use `AsyncResult().get()` or API fetch |
| UI not showing output   | Ensure sessions are set up correctly   |

---

##  Deployment on AWS EC2 (Fully Explained in Lab-2 and Lab-3)

1. Launch Ubuntu EC2
2. SSH into it
3.Run docker-compose up
4.Expose ports 5000, 5672, 6379, 15672, 5555 in security group



##  Concepts Implemented

* ✅ Direct exchange with `celery_see` queue
* ✅ Multi-worker concurrency with `--concurrency=4`
* ✅ Flask session flash for notifications
* ✅ Redis result tracking via `AsyncResult`
* ✅ Queue retry using `self.retry()`





## License

MIT License © 2025 [poridhi.io](https://poridhi.io)
