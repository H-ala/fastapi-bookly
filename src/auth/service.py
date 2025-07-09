from src.db.models import User
from .schemas import UserCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from .utils import generate_passwd_hash


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession): # this function is going to get the user by its email
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)
        user = result.first()
        return user

    async def user_exists(self, email: str, session: AsyncSession) -> bool: # this function allow us to check if the user exists or not
        user = await self.get_user_by_email(email, session)

        return True if user else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump() # these fields are going to be submitted from client side
        new_user = User(**user_data_dict) # in this line we craete a new user obj

        # the next two fields are fields that we have modified f or our users
        new_user.password_hash = generate_passwd_hash(user_data_dict.get("password"))
        new_user.role = "user" # we set default role value to users

        session.add(new_user)
        await session.commit()
        return new_user


    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        """This function verifies users"""
        # so if the user gave a valid email, is_verified filed would have a value of True
        for k, v in user_data.items():
            setattr(user, k, v)

        await session.commit()
        return user
