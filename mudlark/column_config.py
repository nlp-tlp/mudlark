import os
from typing import List, Optional, Literal, Union
from pydantic import (
    BaseModel,
    StrictStr,
    Extra,
    field_validator,
    FieldValidationInfo,
)

_handlers = ["FLOC", "RandomiseInteger", "ToUniqueString", "None"]


class ConfiguredBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class Column(BaseModel):
    name: StrictStr
    handler: Literal[*_handlers]
    new_name: Optional[StrictStr] = None
    prefix: Optional[StrictStr] = None


class ColumnConfig(ConfiguredBaseModel):
    columns: List[Column]
