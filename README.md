# Async Task Processing System with Flask, Celery, RabbitMQ & Pulumi-Driven AWS Deployment

This project demonstrates a production-ready asynchronous task processing system (i.e Deployed in EC2 using Pulumi explained in infra-branch) using:

* ✅ Flask (Web + API)
* ✅ Celery (Task Queue Executor)
* ✅ RabbitMQ (Message Broker)
* ✅ Redis (Result Backend)
* ✅ Flower (Monitoring UI)
* ✅ Docker (Multi-service orchestration)

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
git clone https://github.com/your-username/async-tasks.git
cd async-tasks
```

### 2️⃣ Create & Activate Python Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# OR
source venv/bin/activate  # Linux/macOS
```

### 3️⃣ Install Required Packages

```bash
pip install -r requirements.txt
```

### 4️⃣ Start Services via Docker

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
## Error Handling & Retries
>Email task uses self.retry() with max_retries=3

>If task fails, it's requeued

>Redis tracks the task state:

*PENDING, SUCCESS, RETRY, FAILURE

> inspect it using:

```bash
docker exec -it redis redis-cli
> KEYS *
```




##  Task Monitoring with Flower

* Open [http://localhost:5555](http://localhost:5555)
* View task history, retries, failures
* Inspect live workers and system load



##  Task Status API

### 🔍 GET `/check_status/<task_id>`

Returns task status from Redis:

```json
{
  "task_id": "a1b2c3d4",
  "state": "SUCCESS",
  "result": "Email sent to xyz"
}
```

### 🧪 Use Postman for Submissions

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

##  Deployment on AWS EC2 (Fully Explained in --branch infra)

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
