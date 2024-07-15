from zapusk.models import JobGroup


DEFAULT_COLORS = False
DEFAULT_PORT = 9876
DEFAULT_JOB_GROUPS: dict[str, JobGroup] = {
    "default": JobGroup(
        id="default",
        parallel=10,
    )
}
