from flask import Flask

from .controller_jobs import create_jobs_api
from .controller_config import create_config_api
from .controller_scheduled_jobs import create_scheduled_jobs_api


def create_app(
    executor_manager_service,
    config_service,
    scheduler_service,
):
    app = Flask(__name__)

    app.register_blueprint(
        create_jobs_api(
            config_service=config_service,
            executor_manager_service=executor_manager_service,
        )
    )
    app.register_blueprint(
        create_config_api(
            config_service=config_service,
        )
    )

    app.register_blueprint(
        create_scheduled_jobs_api(
            scheduler_service=scheduler_service,
            config_service=config_service,
        )
    )

    return app
