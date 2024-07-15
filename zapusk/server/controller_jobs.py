from flask import Blueprint, Response, abort, request
from zapusk.lib.json_serdes import JsonSerdes
from zapusk.models import Job, JobConfig, IdField
from .error_response import error_response


def create_jobs_api(config_service, executor_manager_service):
    jobs_api = Blueprint("jobs", __name__)

    @jobs_api.route("/jobs/<job_id>")
    def job_get(job_id: str):
        job = executor_manager_service.get(int(job_id))
        if not job:
            return abort(
                error_response(status=404, error=f"Job with id {job_id} not found")
            )

        return JsonSerdes.serialize(job)

    @jobs_api.route("/jobs/")
    def job_list():
        jobs = executor_manager_service.list()
        return JsonSerdes.serialize(jobs)

    @jobs_api.route("/jobs/", methods=["POST"])
    def job_add():
        body = request.json or {}

        job_config_id = body.get("job_config_id", None)

        # if no config id, let's try to execute it as a command
        if not job_config_id:
            command = body.get("command", None)
            if not command:
                return abort(
                    error_response(
                        status=400,
                        error="Request body contains no `command` or `job_config_id`",
                    )
                )

            group_id = body.get("group_id", None)
            name = body.get("name", None)

            job_group = config_service.get_job_group(group_id or "default")

            if not command or not job_group:
                return abort(
                    error_response(
                        status=404,
                        error=f'group_id "{group_id}" not found',
                    )
                )

            cmd_id = f"command.{IdField.next("command")}"
            job_item = Job.from_config(
                group_config=job_group,
                config=JobConfig(
                    id=cmd_id,
                    name=name or f"{job_group.id}.{cmd_id}",
                    command=command,
                ),
            )
            executor_manager_service.add(job_item)

            return JsonSerdes.serialize(job_item)

        job_config = config_service.get_job(job_config_id)

        if not job_config:
            return abort(
                error_response(
                    status=404,
                    error=f"Job with id `{job_config_id}` not found",
                )
            )

        job_group = config_service.get_job_group(job_config.group)

        if not job_group:  # pragma: no cover
            # this technically not possible, because config_parser will fail first
            return abort(
                error_response(
                    status=404,
                    error=f"Job configuration for {job_config.id} contains unknown jobgroup `{job_config.group}`",
                )
            )

        job_item = Job.from_config(
            group_config=job_group,
            config=job_config,
        )
        executor_manager_service.add(job_item)

        return JsonSerdes.serialize(job_item)

    @jobs_api.route("/jobs/<job_id>", methods=["DELETE"])
    def job_delete(job_id):
        job_item = executor_manager_service.get(int(job_id))
        if not job_item:
            return abort(
                error_response(
                    status=404,
                    error=f"Job with id `{job_id}` not found",
                )
            )

        cancelled_job = executor_manager_service.cancel(job_item)
        return JsonSerdes.serialize(cancelled_job)

    return jobs_api
