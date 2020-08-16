from sowba.core.utils import get_service_router


router = get_service_router("items")


@router.get("/api/@ping")
async def ping():
    return {"response": "OK"}


@router.get("/api/@info")
async def info():
    return {"info": "OK"}
