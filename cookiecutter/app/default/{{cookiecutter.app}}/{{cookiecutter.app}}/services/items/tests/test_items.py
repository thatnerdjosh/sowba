import pytest
import json
from pydantic import ValidationError
from {{cookiecutter.app}}.services.items.model import Items


def test_create_item():
    with open("fixtures/item.json") as item_json_file:
        item_json = json.load(item_json_file)
        try:
            Items(**item_json)
        except ValidationError as error:
            err_str = ""
            for err_obj in error.errors():
                err_str += "{} gave error {}\r\n".format(
                        '.'.join(err_obj["loc"]), err_obj["msg"])
            pytest.fail(err_str)
