# app/tasks.py

'''
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


'''
# Supporting S3 backup logic for emails

import boto3
from botocore.exceptions import NoCredentialsError
import os
from celery import Celery
import time

celery_app = Celery('tasks')
celery_app.config_from_object('app.celeryconfig')

# Environment variables or constants
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'mysql-data-backup-bucket')
AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-1')

# Initialize S3 client
s3_client = boto3.client('s3', region_name=AWS_REGION)

@celery_app.task(name='app.tasks.send_email_task', bind=True, max_retries=3, default_retry_delay=2)
def send_email_task(self, recipient, subject, body):
    print(f"Sending email to {recipient} with subject '{subject}'")
    time.sleep(2)

    # Simulate failure
    if "fail" in recipient:
        raise self.retry(exc=ValueError("Failed email"), countdown=5)

    # Backup to S3
    filename = f"email_log_{int(time.time())}.txt"
    content = f"To: {recipient}\nSubject: {subject}\nBody:\n{body}"
    
    try:
        s3_client.put_object(Body=content, Bucket=S3_BUCKET_NAME, Key=filename)
        print(f"📤 Email backup uploaded to S3 as {filename}")
    except NoCredentialsError:
        print("❌ AWS credentials not found. S3 backup skipped.")
    
    return f"Email sent to {recipient}"
