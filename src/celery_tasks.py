from celery import Celery
from src.mail import mail, create_message
# async_to_sync converts async code to sync code so we can run the async code inside the context of a sync code
from asgiref.sync import async_to_sync

c_app = Celery()

# here we point to the configuration that we sat up for celery in config.py
c_app.config_from_object('src.config')


# here we create our first task
@c_app.task() # this means the following function is a celery task
def send_email(recipients: list[str], subject: str, body: str):
    message = create_message(recipients=recipients, subject=subject, body=body)  # this line returns a message schema

    # this task sends email to users, and it takes a lot of time so we must push it to a background task using Celery

    # celery tasks are not going to be asynchronous, so celery does not support sending async tasks inside our function
    # we must make that task run within our synchronous code. this is doable by a tool named asgiref(it is used in django)
    # it allows us to run our asynchronous code(mail.send_message()) inside the context of a synchronous code(send_email())
    async_to_sync(mail.send_message)(message)
    print("Email sent")


