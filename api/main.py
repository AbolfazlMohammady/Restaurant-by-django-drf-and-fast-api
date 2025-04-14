import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from fastapi import FastAPI
from api.core.auth import router as auth_router 

app = FastAPI()


app.include_router(auth_router, prefix="/api/auth")
