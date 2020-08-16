import uvicorn
from sowba.core.application import SApp
from sowba.settings.app import AppSettings
from sowba.core.application import SService
from sowba.core.vars import sowba_services_var
from sowba.storage.utils import get_service_conf
from sowba.core.application import SServiceRouter


def get_service_router(name: str) -> SServiceRouter:
    try:
        router = sowba_services_var.get()[name]
    except KeyError:
        return
    return router


def register_service_router(name: str, router: SServiceRouter):
    routers = sowba_services_var.get()
    routers[name] = router
    sowba_services_var.set(routers)


def make_service_router(name, settings: AppSettings) -> SServiceRouter:
    router = SServiceRouter(servicename=name, app_settings=settings)
    router.conf.model = SService(router, name=name)(router.conf.model)
    return router


def run_all_services(settings: AppSettings, server=uvicorn.run):
    app = SApp(settings=settings)
    for srv in settings.services:
        router = make_service_router(srv.name, settings)
        register_service_router(srv.name, router)
        app.include_router(
            router,
            tags=[f"{settings.name}@{srv.name}"],
            prefix=f"{settings.name}/{srv.name}",
            responses={
                404: {
                    "service": f"{settings.name}/{srv.name}",
                    "error": "NOT_FOUND",
                }
            },
        )
    return server(app, **settings.asgi.dict())


def run_service(name, settings: AppSettings, server=uvicorn.run):
    app = SApp(settings=settings)
    srv = get_service_conf(name, settings)
    assert srv, f"Service {name}: NOT_FOUND"
    router = make_service_router(name, settings)
    register_service_router(name, router)
    app.include_router(
        router,
        tags=[f"{settings.name}@{name}"],
        prefix=f"{settings.name}/{name}",
        responses={
            404: {"service": f"{settings.name}/{name}", "error": "NOT_FOUND"}
        },
    )
    return server(app, **settings.asgi.dict())


def start_service(name, router, settings: AppSettings, server=uvicorn.run):
    app = SApp(settings=settings)
    app.configure(settings)
    app.include_router(
        router,
        tags=[router.tag],
        prefix=router.prefix,
        responses={
            404: {"service": f"{settings.name}/{name}", "error": "NOT_FOUND"}
        },
    )
    asgi = settings.asgi.dict()
    asgi["host"] = str(asgi["host"])
    return server(app, **asgi)
