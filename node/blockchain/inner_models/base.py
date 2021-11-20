from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):

    class Config:
        allow_mutation = False
