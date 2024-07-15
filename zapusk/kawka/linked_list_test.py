from unittest import TestCase
from .linked_list import LinkedList


class TestLinkedList(TestCase):
    def test_linked_list_create(self):
        head = LinkedList(1)

        self.assertEqual(head.data, 1)
        self.assertEqual(head.next, None)

    def test_linked_list_append(self):
        head = LinkedList(1)
        item = head.append(2)

        self.assertEqual(head.next, item)

    def test_linked_list_str(self):
        head = LinkedList("data")

        self.assertEqual(f"{head}", "linked_list.data")
