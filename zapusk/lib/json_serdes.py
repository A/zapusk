class JsonSerdes:
    """
    Static class to serialize/deserialize data for client-server
    communication
    """

    @staticmethod
    def serialize(data):
        return {"data": data}

    @staticmethod
    def deserialize(res: dict):
        return res["data"]
