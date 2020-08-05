from fastapi import FastAPI
from sowba import security
from sowba.resources import items


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



# sowba service start --all
# sowba service start service-name service-name