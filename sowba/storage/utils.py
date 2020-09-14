from sowba.settings.model import StorageName
from sowba.storage import BaseStorage
from sowba.settings.model import AppSettings
from sowba.core.model import SBaseModel
from sowba.settings.model import ServiceConf
from sowba.settings.storage import ConnectorConf
from sowba.settings.service import ServiceStatus
from sowba.settings.storage import ConnectorConfig


def get_service_conf(name: str, settings: AppSettings) -> ServiceConf:
    for service in settings.services:
        if service.name == name:
            return service
    return


def get_service_connector_name(
    service: ServiceConf, settings: AppSettings
) -> StorageName:
    return service.storage.connector or settings.storages.default


def get_app_connector_conf(
    connector: StorageName, settings: AppSettings
) -> ConnectorConf:
    for conf in settings.storages.connectors:
        if conf.connector == connector:
            return conf
    return


def make_storage(
    model: SBaseModel,
    connector_cls: BaseStorage,
    storage_configs: ConnectorConfig = None,
    storage_settings: dict = None,
) -> BaseStorage:

    storage_configs = storage_configs or ConnectorConfig()
    storage_settings = storage_settings or dict()
    assert issubclass(
        connector_cls, BaseStorage
    ), f"<{connector_cls}> invalid connector class."
    storage = connector_cls()
    storage.configure(model, **storage_configs.dict())
    storage.settings(**storage_settings)
    # storage.setup()
    return storage


def get_storage(
    servicename: str, settings: AppSettings, /, connector: StorageName = None
) -> BaseStorage:

    service = get_service_conf(servicename, settings)
    assert service, f"Service <{servicename}> not found in {settings.file}."
    assert (
        service.status == ServiceStatus.enable
    ), f"Service <{servicename}> must be enabled."
    connector_name = connector or get_service_connector_name(service, settings)
    connector_conf = get_app_connector_conf(connector_name, settings)
    assert connector_conf, f"No connector found for Service: <{servicename}>"
    return make_storage(
        service.storage.model,
        connector_conf.connector_cls,
        storage_configs=connector_conf.configuration,
        storage_settings=connector_conf.settings,
    )


if __name__ == "__main__":
    import os
    from sowba.core import path
    from examples.model import User
    from sowba.settings.utils import load_settings

    def create_user(storage, count=7):
        for i in range(count):
            for name in {"sekou", "oumar", "idrissa", "cheick"}:
                storage.store(obj=User(name=name, age=i + 30))

    os.environ["SOWBA_ENV_ADMIN_USER_PASSWORD"] = "ChangeMe"
    os.environ[
        "SOWBA_ENV_SECURITY_SECRET_KEY"
    ] = "1e0b60f78d76d242514b13253e4092c3aea4fafeb9b56998b3a09ed68ea1cf71"
    settings = load_settings(f"{path.root().parent}/snippets/config.json")
    storage = get_storage("users", settings, connector="rocksdb")
    create_user(storage)
    print(storage.count())
    print(list(storage.find("name", "e", opr="in")))
    storage.close()
    print("*" * 70)
