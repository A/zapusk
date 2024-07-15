from unittest import TestCase

from .id_field import IdField


class TestCounter(TestCase):
    def test_should_get_new_id(self):
        id = IdField.next("test")
        self.assertEqual(id, 1)
        IdField.reset("test")

    def test_should_increment_id(self):
        ids = [
            IdField.next("test"),
            IdField.next("test"),
            IdField.next("test"),
            IdField.next("test"),
            IdField.next("test"),
        ]
        self.assertEqual(ids, [1, 2, 3, 4, 5])
        IdField.reset("test")
