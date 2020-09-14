import asyncio
from functools import wraps
from fastapi import FastAPI
from fastapi import APIRouter
from sowba.storage import BaseStorage
from sowba.settings.model import AppSettings
from starlette.middleware.cors import CORSMiddleware


class SServiceRouter(APIRouter):
    def __init__(self, *args, storage: BaseStorage, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = storage
        self.on_startup.append(self.storage.start)
        self.on_shutdown.append(self.storage.stop)


class SApp(FastAPI):
    def configure(self, settings: AppSettings):
        self.settings = settings
        self.add_middleware(CORSMiddleware, **self.settings.cors.dict())
