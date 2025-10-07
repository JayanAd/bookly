from fastapi import Request, status, Depends
from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService
from typing import List
from src.db.models import User
from src.errors import InvalidToken, RefreshTokenRequired, AccessTokenRequired, InsufficientPermission
user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(TokenBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)
        if not self.token_valid(token):
            # raise HTTPException(
            #     status_code=status.HTTP_403_FORBIDDEN, detail={"error":"This token is invalid or expired.","resolution":"Please login again to obtain a new token."}
            # )
            raise InvalidToken()
        if await token_in_blocklist(token_data.get("jti")):
            # raise HTTPException(
            #     status_code=status.HTTP_403_FORBIDDEN, detail={"error":"This token is invalid or has been revoked.","resolution":"Please login again to obtain a new token."}
            # )
            raise InvalidToken()
        self.verify_token_data(token_data)
        return token_data
    
    def token_valid(self,token: str) -> bool:
            token_data = decode_token(token)
            return token_data is not None
        
    def verify_token_data(self, token_data:dict) -> None:
        raise NotImplementedError("Please override verify_token_data method in subclass.")
    
class AccessTokenBearer(TokenBearer):
    
    def verify_token_data(self, token_data:dict) -> None:
        if token_data and token_data.get("refresh", False):
            # raise HTTPException(
            #     status_code=status.HTTP_403_FORBIDDEN, detail="Please use access token."
            # )
            raise AccessTokenRequired()
    
    
class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict) -> None:
        if token_data and not token_data.get("refresh", False):
            # raise HTTPException(
            #     status_code=status.HTTP_403_FORBIDDEN, detail="Please use refresh token."
            # )
            raise RefreshTokenRequired()

async def get_current_user(token_data: dict = Depends(AccessTokenBearer()), session:AsyncSession = Depends(get_session)) -> dict:
    user_email = token_data["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role  in self.allowed_roles:
            return True
        
        # raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="You do not have the necessary permissions to access this resource.",
        #     )
        raise InsufficientPermission()