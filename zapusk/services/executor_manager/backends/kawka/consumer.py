import logging

from zapusk.kawka import Consumer, ConsumerGroup, Producer
from zapusk.models import Job

from .args_consumer import ArgsConsumer
from .executor import Executor
from .state import ExecutorManagerState


logger = logging.getLogger(__name__)
executorManagerState = ExecutorManagerState()


class ExecutorManagerConsumer(Consumer):
    state = executorManagerState

    def __init__(self, block=True, *args, **kwargs):
        self.state.reset()
        self.block = block
        super().__init__(*args, **kwargs)

    def join(self, timeout=None, *args, **kwargs):
        for cgs in self.state.running_consumergroups.values():
            [args_cg, run_cg] = cgs
            args_cg.join(timeout)
            run_cg.join(timeout)

        for ps in self.state.running_producers.values():
            [args_ps, run_ps] = ps
            args_ps.add(Producer.End)
            run_ps.add(Producer.End)

        super().join(*args, **kwargs)

    def process(self, job: Job):
        group_config = job.group_config
        [args_producer, _] = self.__get_or_create_producers(group_config)
        self.__get_or_create_consumergroups(group_config)
        args_producer.add(job)

    def __get_or_create_producers(self, group_config):
        if group_config.id not in self.state.running_producers:
            args_producer = Producer(
                name=f"producer_{group_config.id}_args", block=self.block
            )
            run_producer = Producer(
                name=f"producer_{group_config.id}_run", block=self.block
            )

            self.state.running_producers[group_config.id] = [
                args_producer,
                run_producer,
            ]
            return [args_producer, run_producer]

        return self.state.running_producers[group_config.id]

    def __get_or_create_consumergroups(self, group_config):
        if group_config.id not in self.state.running_consumergroups:
            [args_producer, run_producer] = self.__get_or_create_producers(group_config)
            args_cg = ConsumerGroup(
                name=f"{group_config.id}_args",
                producer=args_producer,
                Consumer=ArgsConsumer,
                parallel=1,
                context={"sink": run_producer},
            )
            args_cg.start()

            run_cg = ConsumerGroup(
                name=f"{group_config.id}_run",
                producer=run_producer,
                Consumer=Executor,
                parallel=group_config.parallel,
                context={"sink": run_producer},
            )
            run_cg.start()

            self.state.running_consumergroups[group_config.id] = [args_cg, run_cg]
            return [args_cg, run_cg]

        return self.state.running_consumergroups[group_config.id]
