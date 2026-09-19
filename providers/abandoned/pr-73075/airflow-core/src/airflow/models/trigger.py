            # Callback triggers
            select(cls.id)
            .join(Callback, isouter=False)
            .where(or_(cls.triggerer_id.is_(None), cls.triggerer_id.not_in(alive_triggerer_ids)))
            .order_by(Callback.priority_weight.desc(), cls.created_date),
            # Task Instance triggers
            select(cls.id)
