from zapusk.models import Job, JobConfig, JobGroup


def create_jobitem(
    command: str,
    args_command=None,
    args=[],
    state=Job.JOB_STATE_ENUM.PENDING,
    on_finish=None,
    on_fail=None,
    group_on_finish=None,
    group_on_fail=None,
):
    item = Job.from_config(
        config=JobConfig(
            id="test_config",
            name="Test Job Config",
            command=command,
            group="default",
            args_command=args_command,
            on_finish=on_finish,
            on_fail=on_fail,
        ),
        group_config=JobGroup(
            id="default",
            parallel=2,
            on_finish=group_on_finish,
            on_fail=group_on_fail,
        ),
    )
    item.args = args
    item.state = state
    return item
