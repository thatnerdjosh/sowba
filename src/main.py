from fastapi import FastAPI
from app import security
from app.resources import lodges
# from app.resources import members


app = FastAPI()
app.include_router(
    security.router,
    responses={404: {"description": "Not found"}},
)

app.include_router(
    lodges.router,
    prefix=lodges.PATH_PREFIX,
    responses={404: {"description": "Not found"}},
)

# app.include_router(
#     members.router,
#     prefix=members.PATH_PREFIX,
#     responses={404: {"description": "Not found"}},
# )
