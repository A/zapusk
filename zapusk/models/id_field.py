lookup: dict[str, int] = {}


class IdField:
    @staticmethod
    def next(id: str):
        if id not in lookup:
            lookup[id] = 0

        lookup[id] += 1
        return lookup[id]

    @staticmethod
    def reset(id):
        lookup[id] = 0
