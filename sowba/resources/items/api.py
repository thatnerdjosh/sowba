from sowba.resources.items.crud import router, db_context

SERVICE_PATH_PREFIX = "/api"
SERVICE_TAGS = ["Items Service"]
DB = db_context.get()


@router.get(SERVICE_PATH_PREFIX + "/@test_service", tags=SERVICE_TAGS)
async def item_service():
    return DB.get_all()
