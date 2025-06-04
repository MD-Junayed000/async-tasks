
## for a single instances
broker_url = 'amqp://guest:guest@rabbitmq:5672//'
result_backend = 'redis://redis:6379/0'

'''
# For Multiple Instances
broker_url = 'amqp://guest:guest@<BROKER_IP>:5672//'
result_backend = 'redis://<REDIS_IP>:6379/0'
'''
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Dhaka'


task_default_queue = 'celery_see'


'''
# Define Queues
task_queues = (
    Queue('high_priority'),
    Queue('low_priority'),
)

# Default queue
task_default_queue = 'low_priority'

# Route tasks
task_routes = {
    'app.tasks.send_email_task': {'queue': 'high_priority'},
    'app.tasks.reverse_text_task': {'queue': 'low_priority'},
    'app.tasks.fake_sentiment_analysis': {'queue': 'low_priority'},
}

'''
