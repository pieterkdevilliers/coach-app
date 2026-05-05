from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelSchema(BaseModel):
    """Request/response schema with camelCase aliases for JS clients."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class CamelResponse(CamelSchema):
    """ORM-backed response schema with camelCase aliases."""
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )
