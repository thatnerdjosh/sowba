from fastapi import FastAPI
from src import security
from src.resources import items


app = FastAPI()
app.include_router(
    security.router,
    responses={404: {"description": "Not found"}},
)

app.include_router(
    items.router,
    prefix=items.PATH_PREFIX,
    responses={404: {"description": "Not found"}},
)
