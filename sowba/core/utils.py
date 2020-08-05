import uvicorn
from datetime import datetime
from urllib.parse import quote_plus


from uvicorn.config import Config
from uvicorn.main import Server


def run_app(settings, factory=uvicorn.run):
    app = get_app(settings)
    # print(f"sowba service run : {settings}: {app}")
    return factory(app, **app.settings["asgi"])


def get_app(settings):
    module = resolve_dotted_name('sowba.main')
    app = getattr(module, "app")
    app.configure(settings)
    app.setup_task_vars()
    return app


def get_server(app, factory=Server, config_factory=Config):
    config = config_factory(app, **app.settings["asgi"])
    return factory(config=config)


def resolve_dotted_name(name: str):
    """
    import the provided dotted name

    >>> resolve_dotted_name('guillotina.interfaces.IRequest')
    <InterfaceClass guillotina.interfaces.IRequest>

    :param name: dotted name
    """
    if not isinstance(name, str):
        return name  # already an object
    names = name.split(".")
    used = names.pop(0)
    found = __import__(used)
    for n in names:
        used += "." + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)

    return found


def strings_differ(string1: str, string2: str) -> bool:
    """Check whether two strings differ while avoiding timing attacks.

    This function returns True if the given strings differ and False
    if they are equal.  It's careful not to leak information about *where*
    they differ as a result of its running time, which can be very important
    to avoid certain timing-related crypto attacks:

        http://seb.dbzteam.org/crypto/python-oauth-timing-hmac.pdf

    >>> strings_differ('one', 'one')
    False
    >>> strings_differ('one', 'two')
    True

    :param string1:
    :param string2:
    """
    if len(string1) != len(string2):
        return True

    invalid_bits = 0
    for a, b in zip(string1, string2):
        invalid_bits += a != b

    return invalid_bits != 0


def get_keydb_uri(host="127.0.0.1", port=6379):
    return f"redis://{quote_plus(host)}:{quote_plus(str(port))}"


def get_mongo_uri(user, password, host="127.0.0.1", port=27017):
    user = quote_plus(user)
    password = quote_plus(password)
    host = quote_plus(host)
    port = quote_plus(str(port))
    return f"mongodb://{user}:{password}@{host}:{port}"


def date_convertor(o):
    if isinstance(o, datetime):
        return str(o)
