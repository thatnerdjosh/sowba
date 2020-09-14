from sowba.registry import get as get_registry


router = get_registry.service("{{cookiecutter.service}}")


@router.get("/api/@ping")
async def ping():
    return {"response": "OK"}


@router.get("/api/@info")
async def info():
    return {"info": "OK"}
