import jwt
from django.db.models import Q
from django.conf import settings
from asgiref.sync import sync_to_async
from fastapi import APIRouter, HTTPException
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from core.models import User
from core.serializer import UserSerializer
from .schema import RefreshSchema , LoginRegisterSchema
from cashe.core.auth import blacklist_token, cache_user , is_token_blacklisted

router = APIRouter()


@sync_to_async
def get_user(phone_or_email):
    return User.objects.filter(Q(phone=phone_or_email) | Q(email=phone_or_email)).first()


@router.post('/login/')
async def login_register(data:LoginRegisterSchema):

    phone_or_email = data.phone_or_email
    password = data.password

    if not phone_or_email:
        return HTTPException(status_code=400, detail="شماره تلفن/ایمیل الزامی است.")
    if not password:
        return HTTPException(status_code=400, detail='پسورد نمیتواند خالی باشد')
    
    user = await get_user(phone_or_email)
    if user:
        user_pass = await sync_to_async(user.check_password, thread_sensitive=True)(password)
        if not user_pass:
            raise HTTPException(status_code=400, detail="رمز عبور اشتباه است 🏴‍☠️")
        user_exists = True
    

    else:
        data = {'email':phone_or_email} if '@' in phone_or_email else {'phone': phone_or_email}
        data['password'] = password
        serializer = UserSerializer(data=data)

        if await sync_to_async(serializer.is_valid, thread_sensitive=True)():
            user = await sync_to_async(serializer.save, thread_sensitive=True)()
            await sync_to_async(user.set_password, thread_sensitive=True)(password)
            await sync_to_async(user.save, thread_sensitive=True)()
            user_exists = False
        else:
            return serializer.errors
        
    await cache_user(user)

    refresh= RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "message": "کاربر جدید ثبت شد." if not user_exists else "ورود موفقیت‌آمیز.",
    }


@sync_to_async
def get_user_by_id(user_id):
    return User.objects.filter(id=user_id).first()

@router.post("/refresh/")
async def refresh_token(data: RefreshSchema):
    refresh_token_str = data.refresh

    if not refresh_token_str:
        raise HTTPException(status_code=400, detail="Refresh token is required")
    
    if await is_token_blacklisted(refresh_token_str):
        raise HTTPException(status_code=401, detail="Token has been blacklisted")

    try:
        
        decoded_token = jwt.decode(refresh_token_str, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')

        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token structure")


        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")


        await blacklist_token(refresh_token_str)

        access_token = AccessToken.for_user(user)
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(access_token),
            "refresh": str(refresh)
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired refresh token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


