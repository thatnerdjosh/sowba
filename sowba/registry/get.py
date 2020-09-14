from sowba.registry import REGISTRY


def app():
    return vars(REGISTRY.get())["app"].get("app")


def app_settings(name=None):
    settings = vars(REGISTRY.get())["settings"].get("settings")
    if name:
        return getattr(settings, name, None)
    return settings


def service(name):
    return vars(REGISTRY.get())["service"].get(name)


def service_settings(name: str):
    for service in app_settings("service") or list():
        if service.name == name:
            return service
    return


def storage(service):
    return vars(REGISTRY.get())["storage"].get(service)


def default_storage_settings():
    storages = app_settings("storages")
    for connector in storages.connectors:
        if connector.name == storages.default:
            return connector
    return


def storage_settings(service: str):
    srv = service_settings(service)
    assert srv, f"Service: {service} lookup error."
    connector = getattr(srv, "storage", None) or default_storage_settings()
    for c in app_settings("storages").connectors:
        if c.name == connector:
            return c
    return
