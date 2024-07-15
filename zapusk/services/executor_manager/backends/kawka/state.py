class ExecutorManagerState:
    running_consumergroups: dict
    running_producers: dict

    def __init__(self):
        self.running_consumergroups = {}
        self.running_producers = {}

    def reset(self):
        self.running_consumergroups = {}
        self.running_producers = {}
