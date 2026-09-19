
# list_jobs
ARG_DAG_ID_OPT = Arg(("-d", "--dag-id"), help="The id of the dag")
ARG_LIMIT = Arg(("--limit",), type=positive_int(allow_zero=False), help="Return a limited number of records")
job_states = tuple(state.value for state in JobState)
ARG_JOB_STATE = Arg(
    ("--state",),
