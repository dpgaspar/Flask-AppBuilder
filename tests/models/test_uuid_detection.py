import unittest
from uuid import UUID

from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import BINARY, TypeDecorator


class UUIDDetectionTestCase(unittest.TestCase):
    def test_string_detection(self):
        class CustomUUID(TypeDecorator):
            impl = BINARY(16)
            python_type = UUID
            cache_ok = True

        class UnknownType(TypeDecorator):
            impl = BINARY(16)
            cache_ok = True

        class Example(declarative_base()):
            __tablename__ = "uuid_detection"
            id = Column(Integer, primary_key=True)
            name = Column(String)
            native_uuid = Column(PGUUID(as_uuid=True))
            string_uuid = Column(PGUUID(as_uuid=False))
            custom_uuid = Column(CustomUUID())
            unknown = Column(UnknownType())

        interface = SQLAInterface(Example)
        for name, expected in (
            ("name", True),
            ("native_uuid", True),
            ("string_uuid", True),
            ("custom_uuid", True),
            ("unknown", False),
            ("id", False),
            ("missing", False),
        ):
            with self.subTest(column=name):
                self.assertEqual(interface.is_string(name), expected)
