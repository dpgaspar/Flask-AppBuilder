from datetime import datetime
from typing import List, TypeVar
from contextlib import contextmanager

from random import randint
from sqlalchemy.orm import Session

from tests.sqla.models import Model1, Model2
from tests.const import MODEL1_DATA_SIZE, MODEL2_DATA_SIZE


T = TypeVar("T")


def insert_model1_data(session: Session, count: int) -> List[Model1]:
    model1_collection = list()
    # Fill model1
    for i in range(count):
        model = Model1()
        model.field_string = f"test{i}"
        model.field_integer = i
        model.field_float = float(i)
        session.add(model)
        model1_collection.append(model)
    session.commit()
    return model1_collection


@contextmanager
def model1_data(session: Session, count: int = MODEL1_DATA_SIZE) -> List[Model1]:
    model1_collection = insert_model1_data(session, count)

    yield model1_collection

    for model in model1_collection:
        session.delete(model)
    session.commit()


def insert_model2_data(session: Session, count: int) -> List[Model2]:
    model1_collection = insert_model1_data(session, count)
    model2_collection = list()
    for i in range(count):
        model = Model2()
        model.field_string = f"test{i}"
        model.field_integer = i
        model.field_float = float(i)
        model.group = model1_collection[i]
        year = randint(1900, 2012)
        month = randint(1, 12)
        day = randint(1, 28)
        model.field_date = datetime(year, month, day)

        session.add(model)
        model2_collection.append(model)
    session.commit()
    return model2_collection


@contextmanager
def model2_data(session: Session, count: int = MODEL2_DATA_SIZE) -> List[Model2]:
    model2_collection = insert_model2_data(session, count)

    yield model2_collection

    for model in model2_collection:
        session.delete(model.group)
        session.delete(model)
    session.commit()
