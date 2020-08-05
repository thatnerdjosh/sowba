import json
import asyncio
import logging

from sowba.core import Application
from sowba import security
from sowba.resources import routers





logger = logging.getLogger(__name__)



app = Application()

for router in routers:
    app.include_router(
        router.router,
        prefix=router.PATH_PREFIX,
        responses={404: {"description": "Not found"}},
    )

# sowba service start --all
# sowba service start service-name service-name
