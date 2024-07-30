from typing import Generic, List, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj = self.model(**obj_in.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get(self, obj_id: int) -> ModelType:
        return self.db.query(self.model).filter(self.model.id == obj_id).first()

    def get_multi(self, skip: int = 0, limit: int = 10) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, obj_id: int, obj_in: UpdateSchemaType) -> ModelType:
        obj = self.db.query(self.model).filter(self.model.id == obj_id).first()
        if not obj:
            raise ValueError(f"{self.model.__name__} not found")
        for key, value in obj_in.dict(exclude_unset=True).items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj_id: int):
        obj = self.db.query(self.model).filter(self.model.id == obj_id).first()
        if obj:
            self.db.delete(obj)
            self.db.commit()
