from sowba.resources.{{ cookiecutter.resource_name }}.crud import router, db_context

SERVICE_PATH_PREFIX = "/@api"
SERVICE_TAGS = ["{{ cookiecutter.resource_name|capitalize }} Services"]
DB = db_context.get()


@router.get(SERVICE_PATH_PREFIX + "/@{{ cookiecutter.resource_name }}_service", tags=SERVICE_TAGS)
async def {{ cookiecutter.resource_name }}_service():
    return DB.get_all()
