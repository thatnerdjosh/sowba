from app.resources.lodges.crud import router, db_context

SERVICE_PATH_PREFIX = "/api"
SERVICE_TAGS = ["Lodge Service"]
DB = db_context.get()


@router.get(SERVICE_PATH_PREFIX + "/@test_service", tags=SERVICE_TAGS)
async def lodge_service():
    return DB.get_all()
