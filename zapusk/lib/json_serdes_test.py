from unittest import TestCase

from zapusk.lib.json_serdes import JsonSerdes


class TestJsonSerdes(TestCase):
    def test_should_serialize_and_deserialize_data(self):
        item = {}
        serialized = JsonSerdes.serialize(item)
        deserialized = JsonSerdes.deserialize(serialized)

        self.assertEqual(deserialized, item)
