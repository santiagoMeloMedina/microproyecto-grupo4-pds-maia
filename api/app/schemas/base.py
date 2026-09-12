from pydantic import BaseModel, ConfigDict


def _to_camel(field: str) -> str:
    head, *tail = field.split("_")
    return head + "".join(word.capitalize() for word in tail)


class CamelModel(BaseModel):
    """Modelos internos en snake_case (Pythonico), JSON expuesto en camelCase."""

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)
