from typing import Any, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


def list_page(db: Session, model: type[ModelT], page: int = 1, page_size: int = 25, where: Any | None = None) -> tuple[list[ModelT], int]:
    statement = select(model)
    count_statement = select(func.count()).select_from(model)
    if where is not None:
        statement = statement.where(where)
        count_statement = count_statement.where(where)
    total = int(db.scalar(count_statement) or 0)
    items = list(db.scalars(statement.offset((page - 1) * page_size).limit(page_size)))
    return items, total
