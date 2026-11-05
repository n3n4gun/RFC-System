from typing import Literal

from pydantic import BaseModel, Field

class CreateApplicationModel(BaseModel):
    title: str = Field(..., min_length = 5, max_length = 120)
    service: str = Field(..., min_length = 1, max_length = 60)
    priority: Literal['low', 'medium', 'high', 'critical'] = Field(...)
    description: str = Field(..., min_length = 20, max_length = 2000)
    