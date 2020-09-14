from sowba.registry import get as get_registry


router = get_registry.service("selectedService")



@router.get("/api/@me")
async def me():
    return {"me": "Cheick"}