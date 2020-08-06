from sowba.resources.{{ cookiecutter.resource_name }}.crud import router
from sowba.resources.{{ cookiecutter.resource_name }}.crud import {{ cookiecutter.resource_name|capitalize }}
from sowba.resources.{{ cookiecutter.resource_name }}.api import {{ cookiecutter.resource_name }}_service


PATH_PREFIX = "/{{ cookiecutter.resource_name }}"
