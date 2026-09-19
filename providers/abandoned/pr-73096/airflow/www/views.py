        arg_sorting_key = request.args.get("sorting_key", "dag_id")
        arg_sorting_direction = request.args.get("sorting_direction", default="asc")

        if request.args.get("reset_filters") is not None:
            flask_session[FILTER_LASTRUN_COOKIE] = None
            flask_session[FILTER_TAGS_COOKIE] = None
            flask_session[FILTER_STATUS_COOKIE] = None
            flask_session.modified = True
            return redirect(url_for("Airflow.index"))

        if request.args.get("reset_tags") is not None:
            flask_session[FILTER_TAGS_COOKIE] = None
            # Remove the reset_tags=reset from the URL
