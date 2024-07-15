from flask import Blueprint, abort, request
from zapusk.lib.json_serdes import JsonSerdes
from zapusk.models import Job, JobConfig, IdField
from zapusk.services.config.service import ConfigService
from zapusk.services.scheduler_service.service import SchedulerService
from .error_response import error_response


def create_scheduled_jobs_api(
    scheduler_service: SchedulerService,
    config_service: ConfigService,
):
    scheduled_jobs_api = Blueprint("scheduled_jobs", __name__)

    @scheduled_jobs_api.route("/scheduled-jobs/")
    def scheduled_jobs_list():
        scheduled_jobs = scheduler_service.list()
        return JsonSerdes.serialize(scheduled_jobs)

    @scheduled_jobs_api.route("/scheduled-jobs/", methods=["POST"])
    def scheduled_jobs_add():
        body = request.json or {}

        command = body.get("command", None)
        if not command:
            return abort(
                error_response(
                    status=400,
                    error="Request body contains no `command`",
                )
            )

        name = body.get("name", None)
        group_id = body.get("group_id", None)

        if group_id:
            group = config_service.get_job_group(group_id)
            if not group:
                return abort(
                    error_response(
                        status=404,
                        error=f"Unknown group `{group_id}`",
                    )
                )

        schedule = body.get("schedule", None)

        if not schedule:
            return abort(
                error_response(
                    status=400,
                    error=f"Request body contains no `schedule`",
                )
            )

        cmd_id = f"scheduled.{IdField.next("scheduled")}"

        job_config = JobConfig(
            id=cmd_id,
            name=name or f"{group_id}.{cmd_id}",
            schedule=schedule,
            command=command,
        )

        is_added = scheduler_service.add(job_config)

        if not is_added:
            return abort(
                error_response(
                    status=500,
                    error=f"Scheduled job hasn't been added",
                )
            )

        return JsonSerdes.serialize(job_config)

    @scheduled_jobs_api.route("/scheduled-jobs/<scheduled_id>", methods=["DELETE"])
    def scheduled_jobs_cancel(scheduled_id: str):
        return JsonSerdes.serialize(scheduler_service.delete(scheduled_id))

    return scheduled_jobs_api
