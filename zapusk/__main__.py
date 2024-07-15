#! /bin/python
import logging
from docopt import docopt
import importlib.metadata

from zapusk.server import create_app
from zapusk.logger import set_loglevel
from zapusk.services.config.service import ConfigService
from zapusk.services import (
    ExecutorManagerService,
    ExecutorManagerKawkaBackend,
)
from zapusk.services.scheduler_service.service import SchedulerService

logger = logging.getLogger(__name__)

doc = """zapusk

Simple background job runner

Usage:
  zapusk-server -h | --help
  zapusk-server --version
  zapusk-server [--config=PATH] [--verbose]

Options:
  -h --help                     Show this screen
  --version                     Show version.
  -v --verbose                  Enable logging

  --config PATH                 Define custom config


Examples:
    pusk start --config ~/.config/pusk/pusk.yml
"""

version = importlib.metadata.version("zapusk")


def main():
    args = docopt(doc, version=version)
    print(args)

    if "--verbose" in args:
        set_loglevel("DEBUG")
        logger.info("Verbose logging has been enabled")

    logger.info(f"{args}")
    logger.info("Start")

    executor_manager_service = ExecutorManagerService(
        backend=ExecutorManagerKawkaBackend(),
    )

    config_service = ConfigService(args["--config"])

    scheduler_service = SchedulerService(
        executor_manager_service=executor_manager_service,
        config_service=config_service,
    )
    scheduler_service.start()

    app = create_app(
        executor_manager_service=executor_manager_service,
        config_service=config_service,
        scheduler_service=scheduler_service,
    )
    app.run(host="0.0.0.0", port=config_service.get_config().port)


if __name__ == "__main__":
    main()
