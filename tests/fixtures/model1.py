from datetime import datetime
from typing import List, TypeVar
from contextlib import contextmanager

from random import randint
from sqlalchemy.orm import Session

from tests.sqla.models import (
    Model1,
    Model2,
    ModelMMParent,
    ModelMMChild,
    ModelOMParent,
    ModelOMChild,
    ModelOOParent,
    ModelOOChild,
)
from tests.const import MODEL1_DATA_SIZE, MODEL2_DATA_SIZE


def insert_model1_data(session: Session, count: int) -> List[Model1]:
    model1_collection = []
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
        session.merge(model)
        session.delete(model.group)
        session.delete(model)
    session.commit()


def insert_model_mm_children(session: Session, count: int = 1) -> List[ModelMMChild]:
    model_mm_children = []
    for i in range(1, count):
        model = ModelMMChild()
        model.field_string = str(i)
        model.field_integer = i
        model_mm_children.append(model)
        session.add(model)
    session.commit()
    return model_mm_children


def insert_model_mm_parent(
    session: Session, count: int = 1, children_count: int = 1
) -> List[ModelMMParent]:
    model_mm_parent_collection = []
    model_mm_children = insert_model_mm_children(session, children_count)
    for i in range(count):
        model = ModelMMParent()
        model.field_string = str(i)
        model.children = model_mm_children
        session.add(model)
        model_mm_parent_collection.append(model)
    session.commit()
    return model_mm_parent_collection


@contextmanager
def model_mm_parent_data(
    session: Session, count: int = 1, children_count: int = 1
) -> List[ModelMMParent]:
    models = insert_model_mm_parent(session, count, children_count)

    yield models

    for model in models:
        for child in model.children:
            session.delete(child)
        session.delete(model)
    session.commit()


def insert_model_om_children(
    session: Session, count: int, parent: ModelOMParent, parent_i: int
) -> List[ModelOMChild]:
    models = []
    for i in range(1, count):
        model = ModelOMChild()
        model.field_string = f"text{parent_i}.{i}"
        model.parent = parent
        session.add(model)

    session.commit()
    return models


def insert_model_om_parent(
    session: Session, count: int = 1, children_count: int = 1
) -> List[ModelOMParent]:
    models = []
    for i in range(count):
        model = ModelOMParent()
        model.field_string = f"text{i}"
        session.add(model)
        insert_model_om_children(session, children_count, model, i)
        session.commit()
        models.append(model)
    return models


@contextmanager
def model_om_parent_data(
    session: Session, count: int = 1, children_count: int = 1
) -> List[ModelOMParent]:
    models = insert_model_om_parent(session, count, children_count)

    yield models

    for model in models:
        childs = (
            session.query(ModelOMChild).filter(ModelOMChild.parent_id == model.id).all()
        )
        for child in childs:
            session.delete(child)
            session.commit()
        session.delete(model)
    session.commit()


def insert_model_oo_parent(session: Session, count: int = 1) -> List[ModelOOParent]:
    models = []
    for i in range(count):
        model = ModelOOParent()
        model.field_string = f"text{i}"
        model.child = ModelOOChild(field_string=f"text{i}.child")
        session.add(model)
        models.append(model)
    session.commit()
    return models


@contextmanager
def model_oo_parent_data(session: Session, count: int = 1) -> List[ModelOOParent]:
    models = insert_model_oo_parent(session, count)

    yield models

    for model in models:
        session.delete(model.child)
        session.delete(model)
    session.commit()
