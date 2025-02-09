import random

from py_trees.trees import BehaviourTree

from src.service.behavior.active_behavior import StartConversation, ReadNews, Greetings
from src.service.behavior.condition_node import IsPushEnabled, IsAwakeTime
from src.service.logger import logger

import py_trees
from src.service.user_session import UserSessionManager, UserSession
from telegram.ext import ContextTypes


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

def create_behavior_tree(user_session: UserSession, bot):
    root = py_trees.composites.Sequence("Push Notification Decision", memory=True)
    is_push_enabled = IsPushEnabled(user_session)
    is_awake_time = IsAwakeTime(user_session)
    send_message = StartConversation(user_session, bot)
    read_news = ReadNews(user_session, bot)
    random_choice = RandomSelector("Random Choice", [read_news, send_message])
    root.add_children([is_push_enabled, is_awake_time, random_choice])
    behavior_tree = py_trees.trees.BehaviourTree(root)
    logger.info(py_trees.display.ascii_tree(root))
    return behavior_tree

def create_greeting_tree(user_session: UserSession, bot) -> BehaviourTree:
    root = py_trees.composites.Sequence("Say Greetings Behavior Tree", memory=True)
    is_push_enabled = IsPushEnabled(user_session)
    greeting = Greetings(user_session, bot)
    root.add_children([is_push_enabled, greeting])
    behavior_tree = py_trees.trees.BehaviourTree(root)
    logger.info(py_trees.display.ascii_tree(root))
    return behavior_tree

async def push_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    idle_users = UserSessionManager.get_all_sessions()
    for user_session in idle_users:
        tree = create_behavior_tree(user_session, context.bot)
        tree.tick()
        tree2 = create_greeting_tree(user_session, context.bot)
        tree2.tick()
