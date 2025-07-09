# this file is responsible for sending emails
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from .config import Config
from pathlib import Path

# we should create the folder of our root project
# __file__ is the current file that we are in it
# with resolve method we can get the absolute path and access things such as parent folder and stuff like that
# the parent folder of this file(mail.py) is src so we would make a template folder there
BASE_DIR = Path(__file__).resolve().parent

# the config obj is a set of configurations that are necessary to send emails and its type is connection config class
mail_config = ConnectionConfig(
    MAIL_USERNAME = Config.MAIL_USERNAME,
    MAIL_PASSWORD = Config.MAIL_PASSWORD,
    MAIL_FROM = Config.MAIL_FROM,
    MAIL_PORT = Config.MAIL_PORT,
    MAIL_SERVER = Config.MAIL_SERVER,
    MAIL_FROM_NAME= Config.MAIL_FROM_NAME,
    MAIL_STARTTLS = Config.MAIL_STARTTLS,
    MAIL_SSL_TLS = Config.MAIL_SSL_TLS,
    USE_CREDENTIALS = Config.USE_CREDENTIALS,
    VALIDATE_CERTS = Config.VALIDATE_CERTS,

    # to use paths on our system we need to import pathlib. it helps us to create files and we will be able to get things like the parent folders and their location and so on
    TEMPLATE_FOLDER= Path(BASE_DIR, "templates"), # this one leads to a directory path. a path on our system if we are to send html template as our emails. first we would give the parent folder and then template folder
    # we can keep it simple by not sending HTML templates, but if we want to we need to provide the template folder
)


# this obj is responsible for sending the messages and this is where we access methods that will help us to send emails and the only arg it needs is the Config obj
mail = FastMail(config=mail_config)

# now we would send the email
def create_message(recipients: list[str], subject: str, body: str)  :
    message = MessageSchema(recipients=recipients, subject=subject, body=body, subtype=MessageType.html) # we are sending html emails
    # MessageSchema is a structure that's going to describe the email addresses we want to send mail to, the message subject and the message body
    return message