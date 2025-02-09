import datetime

import py_trees
import pytz

from src.config import config
from src.service.logger import logger
from src.service.user_session import UserSession
from src.utils import get_current_time


class IsUserIdle(py_trees.behaviour.Behaviour):
    def __init__(self, user_session: UserSession):
        super(IsUserIdle, self).__init__(name="Is User Idle?")
        self.user_session = user_session

    def update(self):
        logger.info(f"Condition Node: {self.name}")
        if self.user_session.is_idle(0, 0):
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

class IsPushEnabled(py_trees.behaviour.Behaviour):
    def __init__(self, user_session):
        super(IsPushEnabled, self).__init__(name="Is Push Enabled?")
        self.user_session = user_session

    def update(self):
        logger.info(f"Condition Node: {self.name}")
        if self.user_session.enable_push:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

class IsAwakeTime(py_trees.behaviour.Behaviour):
    def __init__(self, user_session):
        super(IsAwakeTime, self).__init__(name="Is It Awake Time?")
        self.user_session = user_session

    def update(self):
        logger.info(f"Condition Node: {self.name}")
        current_time, _ = get_current_time()
        if config.is_awake_settings["sleep_time_hour_start"] <= current_time <= config.is_awake_settings["sleep_time_hour_end"]:
            return py_trees.common.Status.FAILURE
        else:
            return py_trees.common.Status.SUCCESS