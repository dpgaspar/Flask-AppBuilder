from contextlib import contextmanager
from datetime import datetime
from random import randint
from typing import List

from sqlalchemy.orm import Session
from tests.const import MODEL1_DATA_SIZE, MODEL2_DATA_SIZE
from tests.sqla.models import (
    Model1,
    Model2,
    Model3,
    Model4,
    ModelMMChild,
    ModelMMParent,
    ModelOMChild,
    ModelOMParent,
    ModelOOChild,
    ModelOOParent,
    ModelWithEnums,
    ModelWithProperty,
    TmpEnum,
)


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
    model_ids = [model.id for model in model1_collection]

    try:
        yield model1_collection
    finally:
        for model_id in model_ids:
            model = session.get(Model1, model_id)
            if model:
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
    model2_ids = [model.id for model in model2_collection]

    try:
        yield model2_collection

    finally:
        for model_id in model2_ids:
            model = session.query(Model2).get(model_id)
            if model:
                session.delete(model)
        # kill all Orphans
        session.query(Model1).delete()

        session.commit()


def insert_model4_data(session: Session, count: int = 1) -> List[Model4]:
    model1_collection = insert_model1_data(session, count)
    models = []
    for i in range(count):
        model = Model4()
        model.field_string = f"test{i}"
        model.model1_1 = model1_collection[i]
        model.model1_2 = model1_collection[i]
        session.add(model)
        session.commit()

        session.add(model)
        models.append(model)
    session.commit()
    return models


@contextmanager
def model4_data(session: Session, count: int = 1) -> List[Model4]:
    models = insert_model4_data(session, count)
    model_ids = [model.id for model in models]

    try:
        yield models
    finally:
        for model_id in model_ids:
            model = session.query(Model4).get(model_id)
            model1_1 = session.query(Model1).get(model.model1_1.id)
            model1_2 = session.query(Model1).get(model.model1_2.id)
            session.delete(model1_1)
            session.delete(model1_2)
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
    model_ids = [model.id for model in models]

    try:
        yield models
    finally:
        child_ids = set()
        for model_id in model_ids:
            model = session.query(ModelMMParent).get(model_id)
            child_ids.update([child.id for child in model.children])
            model.children = []
            session.commit()
            session.delete(model)
            session.commit()
        for child_id in child_ids:
            child = session.query(ModelMMChild).get(child_id)
            session.delete(child)
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
    model_ids = [model.id for model in models]

    try:
        yield models
    finally:
        for model_id in model_ids:
            model = session.query(ModelOMParent).get(model_id)
            childs = (
                session.query(ModelOMChild)
                .filter(ModelOMChild.parent_id == model.id)
                .all()
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
    model_ids = [model.id for model in models]

    try:
        yield models
    finally:
        for model_id in model_ids:
            model = session.query(ModelOOParent).get(model_id)
            session.delete(model.child)
            session.delete(model)
        session.commit()


def insert_model_with_enums(session: Session, count: int = 1) -> List[ModelWithEnums]:
    models = []
    for i in range(count):
        model = ModelWithEnums()
        model.enum1 = "e1"
        model.enum2 = TmpEnum.e2
        model.enum3 = TmpEnum.e3.name
        models.append(model)
        session.add(model)
    session.commit()
    return models


@contextmanager
def model_with_enums_data(session: Session, count: int = 1) -> List[ModelWithEnums]:
    models = insert_model_with_enums(session, count)
    model_ids = [model.id for model in models]

    try:
        yield models
    finally:
        for model_id in model_ids:
            model = session.query(ModelWithEnums).get(model_id)
            session.delete(model)
        session.commit()


def insert_model_with_property(
    session: Session, count: int = 1
) -> List[ModelWithProperty]:
    models = []
    for i in range(count):
        model = ModelWithProperty()
        model.field_string = str(i)
        session.add(model)
        models.append(model)
    session.commit()
    return models


@contextmanager
def model_with_property_data(
    session: Session, count: int = 1
) -> List[ModelWithProperty]:
    models = insert_model_with_property(session, count)
    model_ids = [model.id for model in models]

    try:
        yield models
    finally:
        for model_id in model_ids:
            model = session.query(ModelWithProperty).get(model_id)
            session.delete(model)
        session.commit()


def insert_model3(session: Session) -> Model3:
    model3 = Model3(pk1=3, pk2=datetime(2017, 3, 3), field_string="foo")
    session.add(model3)
    session.commit()

    return model3


@contextmanager
def model3_data(session: Session) -> Model3:
    model3 = insert_model3(session)
    model3_id = model3.pk1
    try:
        yield model3
    finally:
        model3 = session.query(Model3).filter_by(pk1=model3_id).first()
        if model3:
            session.delete(model3)
            session.commit()
