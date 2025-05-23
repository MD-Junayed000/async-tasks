# Updated Flask Blueprint for Task Submission
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .tasks import send_email_task, reverse_text_task, fake_sentiment_analysis
from celery.result import AsyncResult
from .tasks import celery_app  # ensure this is already defined

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    reverse_result = None
    sentiment_result = None

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        try:
            if form_type == 'email':
                recipient = request.form['recipient']
                subject = request.form['subject']
                body = request.form['body']
                result = send_email_task.delay(recipient, subject, body)
                flash(f"Email Task Submitted: {result.id}", 'success')

            elif form_type == 'reverse':
                text = request.form['text']
                result = reverse_text_task.delay(text)
                reverse_result = result.get(timeout=10)  # ⏳ fetch from Redis

            elif form_type == 'sentiment':
                text = request.form['text']
                result = fake_sentiment_analysis.delay(text)
                sentiment_result = result.get(timeout=10)  # ⏳ fetch from Redis

            else:
                flash("Unknown form submitted", 'danger')
        except Exception as e:
            flash(f"Task Submission Error: {str(e)}", 'danger')

    return render_template('index.html',
                           reverse_result=reverse_result,
                           sentiment_result=sentiment_result)


@main.route('/check_status/<task_id>', methods=['GET'])
def check_status(task_id):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": result.id,
        "state": result.state,
        "result": str(result.result)
    }
    
@main.route('/check_status_redirect', methods=['GET'])
def check_status_redirect():
    task_id = request.args.get('task_id')
    return redirect(url_for('main.check_status', task_id=task_id))
