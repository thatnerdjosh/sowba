from sowba.registry import REGISTRY


def app(value):
    _registry = REGISTRY.get()
    vars(_registry)["app"]["app"] = value


def app_settings(value):
    _registry = REGISTRY.get()
    vars(_registry)["settings"]["settings"] = value


def service(name, value):
    _registry = REGISTRY.get()
    vars(_registry)["service"][name] = value


def storage(service, value):
    _registry = REGISTRY.get()
    vars(_registry)["storage"][service] = value
