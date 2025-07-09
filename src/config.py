from pydantic_settings import BaseSettings, SettingsConfigDict


# this class is our Setting class in which we would set our environment variable in it as attrs(keys) and we would get their values by using model_config and give its path there.
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str

    REDIS_URL: str = "redis://localhost:6379/0"

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    DOMAIN: str

    # this class is used so we can influence our pydantic model and tell it where it can find the values of the attrs(keys) that we have set above, in our case it is .env file.
    # every pydantic model class has a model_config attr which is a dictionary. this dictionary will allow us to change the configuration of a specific pantic model
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


Config = Settings()  # in this line we made an obj of our Setting class to have access to our DATABASE_URL


# we are using redis as our Broker (RabbitMQ is also a good choice)
# broker is a medium that is going to allow us to send our messages to workers

broker_url = Config.REDIS_URL # our broker_url is going to point to redis
result_backend = Config.REDIS_URL # this is where results are kept in redis

# the celery worker is going to be a process that's going to run independent of our server and all it's going to do is to look for tasks that are present within the queue
# once these tasks are available, then it's going to execute those tasks so we can finally get the results out of executing those tasks
