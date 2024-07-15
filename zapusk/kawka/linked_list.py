class LinkedList[T]:
    """
    Simple linked list implementation
    """

    next: "LinkedList[T] | None" = None
    """
    Link to a next element
    """

    def __init__(self, data: T):
        self.data = data

    def append(self, data: T):
        """
        Appends an element to the linked list
        """
        self.next = LinkedList(data)
        return self.next

    def __str__(self):
        return f"linked_list.{self.data}"
