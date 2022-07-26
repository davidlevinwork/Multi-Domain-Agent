import random
from pddlsim.executors.executor import Executor


class RandomExecutor(Executor):
    def __init__(self):
        super(RandomExecutor, self).__init__()

    def initialize(self, services):
        self.services = services

    def next_action(self):
        if self.services.goal_tracking.reached_all_goals():
            return None
        options = self.services.valid_actions.get()

        if len(options) == 0:
            return None
        if len(options) == 1:
            return options[0]
        return random.choice(options)


class SmartRandomExecutor(Executor):
    def __init__(self):
        super(SmartRandomExecutor, self).__init__()
        self.agent_actions = []

    def initialize(self, services):
        self.services = services

    def next_action(self):
        if self.services.goal_tracking.reached_all_goals():
            return None

        actions = self.services.valid_actions.get()
        if len(actions) == 0:
            return None
        if len(actions) == 1:
            action = actions[0]
        else:
            relevant_actions = self.get_relevant_actions(actions)
            action = random.choice(relevant_actions)

        self.agent_actions.append(action)
        return action

    def get_relevant_actions(self, actions):
        last_10_actions = self.agent_actions[-10:]
        relevant_actions = []
        for action in actions:
            if action not in last_10_actions:
                relevant_actions.append(action)

        if len(relevant_actions) == 0:
            return actions
        return relevant_actions
