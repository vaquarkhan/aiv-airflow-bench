            resp = self.client.get(f"xcoms/{dag_id}/{run_id}/{task_id}/{key}", params=params)
        except ServerResponseError as e:
            if e.response.status_code == HTTPStatus.NOT_FOUND:
                log.warning(
                    "XCom not found",
                    dag_id=dag_id,
                    run_id=run_id,
            resp = self.client.get(f"xcoms/{dag_id}/{run_id}/{task_id}/{key}/item/{offset}")
        except ServerResponseError as e:
            if e.response.status_code == HTTPStatus.NOT_FOUND:
                log.warning(
                    "XCom not found",
                    dag_id=dag_id,
                    run_id=run_id,
