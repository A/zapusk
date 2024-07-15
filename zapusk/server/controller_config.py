from flask import Blueprint
from zapusk.lib.json_serdes import JsonSerdes


def create_config_api(config_service):
    jobgroups_api = Blueprint("jobgroups", __name__)

    @jobgroups_api.route("/config/groups/")
    def groups_list():
        return JsonSerdes.serialize(config_service.list_jobgroups())

    @jobgroups_api.route("/config/jobs/")
    def job_list():
        return JsonSerdes.serialize(config_service.list_jobs())

    return jobgroups_api
