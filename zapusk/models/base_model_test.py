from dataclasses import dataclass
from unittest import TestCase

from .base_model import BaseModel


class TestBaseModel(TestCase):
    def test_base_model_should_compare_dict_and_dataclass(self):
        @dataclass(eq=False)
        class Model(BaseModel):
            attr: int = 1

        model = Model()

        self.assertEqual(model, {"attr": 1})

    def test_base_model_should_compare_dict_and_dataclass_fail(self):
        @dataclass(eq=False)
        class Model(BaseModel):
            attr: int = 1

        model = Model()

        self.assertNotEqual(model, {"attr": 2})

    def test_base_model_should_compare_dataclasses(self):
        @dataclass(eq=False)
        class Model(BaseModel):
            attr: int

        model1 = Model(attr=1)
        model2 = Model(attr=1)

        self.assertEqual(model1, model2)

    def test_base_model_should_compare_dataclasses_fail(self):
        @dataclass(eq=False)
        class Model(BaseModel):
            attr: int

        model1 = Model(attr=1)
        model2 = Model(attr=2)

        self.assertNotEqual(model1, model2)

    def test_base_model_should_compare_other_types(self):
        @dataclass(eq=False)
        class Model(BaseModel):
            attr: int = 1

        model = Model()

        self.assertNotEqual(model, 1)
        self.assertNotEqual(model, "1")
        self.assertNotEqual(model, None)
