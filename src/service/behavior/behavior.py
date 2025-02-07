import random

from src.service.behavior.active_behavior import SendTextMessage, ReadNews
from src.service.logger import logger
from src.service.user_session import UserSession

import py_trees
from src.service.user_session import UserSessionManager
from telegram.ext import ContextTypes


class IsUserIdle(py_trees.behaviour.Behaviour):
    def __init__(self, user_session: UserSession):
        super(IsUserIdle, self).__init__(name="Is User Idle?")
        self.user_session = user_session

    def update(self):
        logger.info(f"Behavior update: {self.name}")
        if self.user_session.is_idle(0, 0):
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

class IsPushEnabled(py_trees.behaviour.Behaviour):
    def __init__(self, user_session):
        super(IsPushEnabled, self).__init__(name="Is Push Enabled?")
        self.user_session = user_session

    def update(self):
        print(self.name)
        if self.user_session.enable_push:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

class RandomSelector(py_trees.behaviour.Behaviour):
    def __init__(self, name, behaviors):
        super(RandomSelector, self).__init__(name)
        self.behaviors = behaviors
        self.selected_behavior = None

    def setup(self, timeout):
        self.selected_behavior = random.choice(self.behaviors)

    def initialise(self):
        self.selected_behavior = random.choice(self.behaviors)

    def update(self):
        if self.selected_behavior:
            self.selected_behavior.tick_once()
            return self.selected_behavior.status
        return py_trees.common.Status.FAILURE

def create_behavior_tree(user_session, bot):
    root = py_trees.composites.Sequence("Push Notification Decision", memory=True)
    is_push_enabled = IsPushEnabled(user_session)
    send_message = SendTextMessage(user_session, bot)
    read_news = ReadNews(user_session, bot)
    random_choice = RandomSelector("Random Choice", [read_news, send_message])
    root.add_children([is_push_enabled, random_choice])
    behavior_tree = py_trees.trees.BehaviourTree(root)
    logger.info(py_trees.display.ascii_tree(root))
    return behavior_tree

async def push_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    idle_users = UserSessionManager.get_all_sessions()
    for user_session in idle_users:
        tree = create_behavior_tree(user_session, context.bot)
        tree.tick()
