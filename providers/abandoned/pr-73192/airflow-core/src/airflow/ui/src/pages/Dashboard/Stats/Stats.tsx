          isLoading={isStatsLoading}
          isRTL={isRTL}
          label={translate("stats.failedDags")}
          link="/dags?last_dag_run_state=failed"
          state="failed"
        />

            isLoading={isStatsLoading}
            isRTL={isRTL}
            label={translate("stats.queuedDags")}
            link="/dags?dag_run_state=queued"
            state="queued"
          />
        ) : undefined}
          isLoading={isStatsLoading}
          isRTL={isRTL}
          label={translate("stats.runningDags")}
          link="/dags?dag_run_state=running"
          state="running"
        />

          isLoading={isStatsLoading}
          isRTL={isRTL}
          label={translate("stats.activeDags")}
          link="/dags?paused=false"
        />
      </Flex>
    </Box>
