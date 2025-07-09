from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService
from ..db.main import get_session
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from .dependecies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blocklist
from src.errors import UserAlreadyExist, InvalidCredentials, InvalidToken, UserNotFound
from src.mail import mail, create_message
from src.celery_tasks import send_email # bringing send_email task from the respective file
from src.config import Config
from .utils import (
    create_access_token,
    verify_passwd_hash,
    create_url_safe_token,
    decode_url_safe_token,
    generate_passwd_hash
)

from .schemas import (
    UserCreateModel,
    UserLoginModel,
    UserBooksModel,
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel
)

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2

# with this endpoint we would send emails
@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses
    subject = "FastAPI"
    html = "<h1>Welcome to the app</h1>"

    send_email.delay(emails, subject, html) # delay method means this function is a celery task

    # message = create_message(recipients=emails, subject=subject, body=html) # this line returns a message schema
    #
    # await mail.send_message(message)

    return {"message": "email sent successfully"}



@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, bg_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exist = await user_service.user_exists(email, session)
    if user_exist:
        raise UserAlreadyExist()

    new_user = await user_service.create_user(user_data, session)

    # after the user has successfully created their accounts we must send them an email to tell them how to verify their account
    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1>Verify your Email</h1>
    <p>please click this <a href="{link}">link</a> to verify your email</p>
    """

    subject = "Verify your Email"

    emails = [email] # in celery we should give the email as a list

    send_email.delay(emails, subject, html_message)  # delay method means this function is a celery task



    # message = create_message(recipients=[email], subject=subject, body=html_message) # this line returns a message schema
    #
    # # this task sends email to users and it takes a lot of time so we must push it to a background task using BackgroundTasks
    # # first we would omit the "await" and then use BackgroundTasks obj for it
    # # we would use add_task method for it
    # # the first argument it takes is the function which is going to be pushed in the background and the second is the argument of that function
    # # await mail.send_message(message)
    # bg_tasks.add_task(mail.send_message ,message)


    return {
        "message": "Account created successfully! Check your email to verify your account",
        "user": new_user
    }


# this endpoint is one that users who have created an account would click on it to verify themselves
@auth_router.get("/verify/{token}")
async def verify_user(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        await user_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Account verified Successfully!"},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={"message": "Error occurred during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )









# for login we must get user detail and check if the user detail match with what we have in database and then provide access token and refresh token for them
# and in case it didn't match we should raise a HTTPException showing user that they had invalid credentials
@auth_router.post("/login")
async def login_user(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email, session)
    if user is not None:
        password_valid = verify_passwd_hash(password, user.password_hash)  # the output would be True or False
        if password_valid:  # if password is correct    then we will create both access token and refresh token for the user
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role # adding users role to the token
                }
            )
            # difference between access token and refresh token is that in refresh token we set an expiry which is longer than access token expiry
            refresh_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(
                content={
                    "massage": "login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    # we can provide some detail about the user who has logged in
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
            )
    raise InvalidCredentials()


  # this endpoint gives us a new access token(refresh token)
@auth_router.get("/refresh_token")
async def get_new_access_token(token_datails: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_datails["exp"] # we are extracting the access token expiry which is sth like 1718981303
    # we need to convert the timestamp type to a datetime type
    # here we check if our refresh token is expired and if it's not expired then we must create a new access token with the user detail which exists within our access token
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now(): # this line convert our timestamp into a datetime and checks   it with the current date and current time
        new_access_token = create_access_token(
            user_data=token_datails["user"]
        )
        return JSONResponse(content={
            "access_token": new_access_token,
        })
    # in case it doesn't return access token we shall throw an error
    raise InvalidToken()


# this path returns the current user
@auth_router.get("/me", dependencies=[Depends(role_checker)], response_model=UserBooksModel)
async def get_current_user(user = Depends(get_current_user)):
    return user


# this endpoint is used for revoking the tokenx
@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())): # since we want access token details, we must use AccessTokenBearer dependency
    jti = token_details["jti"]
    # now that we have the jti we will add it to the token_blocklist
    await add_jti_to_blocklist(jti)

    return JSONResponse(content={
        "massage": "logout successful",
    },
    status_code=status.HTTP_200_OK
    )

# this endpoint is used when a user wants to reset theirs password
@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email # here we extract the email address
    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset your password</h1>
    <p>please click this <a href="{link}">link</a> to Reset your Password</p>
    """

    subject = "Reset your password"

    message = create_message(recipients=[email], subject=subject, body=html_message) # this line returns a message schema

    await mail.send_message(message)
    return JSONResponse(
        content={
            "message": "password reset link sent! please check your email for more details",
        },
        status_code=status.HTTP_200_OK
    )


# this endpoint takes in the new password of the who wants to change theirs password and changes it
@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(token: str, passwords: PasswordResetConfirmModel, session: AsyncSession = Depends(get_session)):


    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password
    if new_password != confirm_password: # this means in our front-end user has not typed the same password in the two inputs
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="passwords don't match")

    # here we hash the new password
    password_hash = generate_passwd_hash(new_password)

    token_data = decode_url_safe_token(token) # here we encrypt user email so it wouldn't be shown in the url

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {"password_hash": password_hash}, session)
        return JSONResponse(
            content={"message": "Password reset successful"},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={"message": "Error occurred during resetting password"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )



