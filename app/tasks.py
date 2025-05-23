
from celery import Celery
import time
from celery.exceptions import MaxRetriesExceededError

celery_app = Celery('tasks')
celery_app.config_from_object('app.celeryconfig')

@celery_app.task(name='app.tasks.send_email_task', bind=True, max_retries=3, default_retry_delay=2)
def send_email_task(self, recipient, subject, body):
    print(f"Sending email to {recipient} with subject '{subject}'")
    time.sleep(2)
    if "fail" in recipient:
        raise self.retry(exc=ValueError("Failed email"), countdown=5) ### experiment
    return f"Email sent to {recipient}"

@celery_app.task(name='app.tasks.reverse_text_task')
def reverse_text_task(text):
    time.sleep(2)
    return text[::-1]

@celery_app.task(name='app.tasks.fake_sentiment_analysis')
def fake_sentiment_analysis(text):
    time.sleep(2)
    return "positive" if "good" in text.lower() else "negative"



