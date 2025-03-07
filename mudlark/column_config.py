from typing import List, Optional, Literal
from pydantic import (
    BaseModel,
    StrictStr,
    ConfigDict,
)

_handlers = ["FLOC", "RandomiseInteger", "ToUniqueString", "None"]

class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Column(BaseModel):
    name: StrictStr
    handler: Literal[*_handlers]
    new_name: Optional[StrictStr] = None
    prefix: Optional[StrictStr] = None


class ColumnConfig(ConfiguredBaseModel):
    columns: List[Column]
