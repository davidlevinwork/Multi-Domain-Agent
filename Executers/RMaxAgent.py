import hashlib
import json
import os
import copy
import random
import numpy as np

from Services import io_service
import Services.goal_service as gt
from pddlsim.executors.executor import Executor
from Helpers.customized_valid_actions import CustomizedValidActions

# Globals
LAST_STATE = None
LAST_ACTION = None
LAST_H_STATE = None


class RMaxExecutor(Executor):
    def __init__(self, policy_file, process_id):
        super(RMaxExecutor, self).__init__()

        self.services = None
        self.process_id = process_id
        self.parser = None
        self.perception = None
        LAST_STATE = LAST_ACTION = LAST_H_STATE = None

        self.occurrences_dict = {}
        self.policy_file = policy_file + "-" + str(self.process_id)

    def initialize(self, services):
        self.services = services
        self.parser = services.parser
        self.perception = services.perception

        if os.path.exists(self.policy_file + ".json") and os.stat(self.policy_file + ".json").st_size != 0:
            with open(self.policy_file + ".json", 'r') as fp:
                self.occurrences_dict = json.load(fp)

    def get_hashed_representation_for_state(self, state=None):
        if state is None:
            state_values = self.services.perception.get_state()
        else:
            state_values = state
        for key in state_values:
            value = state_values[key]
            if isinstance(value, set):
                state_values[key] = list(value)
                state_values[key].sort()

        state_json_rep = json.dumps(state_values, sort_keys=True)
        hashed_state = hashlib.sha1(state_json_rep).hexdigest()
        return hashed_state

    def next_action(self):
        global LAST_ACTION, LAST_STATE, LAST_H_STATE

        self.update_action_frequency()
        current_state = self.services.perception.get_state()
        actions = CustomizedValidActions.get(CustomizedValidActions(self.parser, self.perception), current_state)

        if self.services.goal_tracking.reached_all_goals() or len(actions) == 0:
            self.calculate_probabilistic_values()
            io_service.IOService.write_q_table_to_file(self.policy_file, self.occurrences_dict)
            return None
        elif len(actions) == 1:
            chosen_action = actions[0]
        else:
            chosen_action = random.choice(actions)

        LAST_ACTION = chosen_action
        LAST_STATE = self.services.perception.get_state()
        LAST_H_STATE = self.get_hashed_representation_for_state()

        self.append_new_value(LAST_H_STATE, LAST_ACTION)
        return chosen_action

    def update_action_frequency(self):
        global LAST_ACTION, LAST_STATE, LAST_H_STATE

        if LAST_STATE is None or LAST_ACTION is None:
            return

        for i, data in enumerate(self.occurrences_dict[LAST_H_STATE]):
            for action, counter in data.iteritems():
                if action == LAST_ACTION:
                    counter = self.occurrences_dict[LAST_H_STATE][i][action]
                    self.occurrences_dict[LAST_H_STATE][i][action] = counter + 1

    def append_new_value(self, state, action):
        is_new = False
        if not self.occurrences_dict.has_key(state):
            is_new = True

        if is_new:
            self.occurrences_dict[state] = []
            action_to_occurrences = {action: 0}
            self.occurrences_dict[state].append(action_to_occurrences)
        else:
            for h_state in self.occurrences_dict.keys():
                if h_state == state:
                    for i, data in enumerate(self.occurrences_dict[h_state]):
                        if action in list(data.keys())[0]:
                            return
                    action_to_occurrences = {action: 0}
                    self.occurrences_dict[state].append(action_to_occurrences)
                    return

    def calculate_probabilistic_values(self):
        for state in self.occurrences_dict:
            total = 0
            for i, data in enumerate(self.occurrences_dict[state]):
                for action, counter in data.iteritems():
                    total += counter
            for i, data in enumerate(self.occurrences_dict[state]):
                for action, counter in data.iteritems():
                    decimal_counter = self.occurrences_dict[state][i][action]
                    probabilistic_counter = float(decimal_counter) / float(total)
                    self.occurrences_dict[state][i][action] = probabilistic_counter


class RMaxExecutive(Executor):
    def __init__(self, policy_file):
        super(RMaxExecutive, self).__init__()
        self.parser = None
        self.services = None
        self.perception = None
        self.last_15_actions = []
        self.occurrences_dict = {}
        self.policy_file = policy_file

    def initialize(self, services):
        self.services = services
        self.parser = services.parser
        self.perception = services.perception

        with open(self.policy_file, 'r') as fp:
            self.occurrences_dict = json.load(fp)

    def get_hashed_representation_for_state(self, state=None):
        if state is None:
            state_values = self.services.perception.get_state()
        else:
            state_values = state
        for key in state_values:
            value = state_values[key]
            if isinstance(value, set):
                state_values[key] = list(value)
                state_values[key].sort()

        state_json_rep = json.dumps(state_values, sort_keys=True)
        hashed_state = hashlib.sha1(state_json_rep).hexdigest()
        return hashed_state

    def next_action(self):
        current_state = self.services.perception.get_state()
        actions = CustomizedValidActions.get(CustomizedValidActions(self.parser, self.perception), current_state)

        if self.services.goal_tracking.reached_all_goals() or len(actions) == 0:
            return None
        elif len(actions) == 1:
            action = actions[0]
        else:
            action = self.choose_best_action(actions)
        self.update_agent_history(action)
        return action

    def choose_best_action(self, actions):
        best_actions = []
        best_action_counter = float('-inf')
        agent_at = self.get_hashed_representation_for_state()

        relevant_actions = self.handle_infinite_loops(actions)
        random.shuffle(relevant_actions)

        if not self.occurrences_dict.has_key(agent_at):
            return random.choice(relevant_actions)

        for i, data in enumerate(self.occurrences_dict[agent_at]):
            for action, counter in data.iteritems():
                if action in relevant_actions:
                    if counter > best_action_counter:
                        best_actions = [action]
                        best_action_counter = counter
                    elif counter == best_action_counter:
                        best_actions.append(action)
        if len(best_actions) > 0:
            return random.choice(best_actions)
        else:
            if len(self.last_15_actions) > 2:
                last_3_actions = self.last_15_actions[-3:]
                for act in last_3_actions:
                    if act in relevant_actions:
                        relevant_actions.remove(act)
            return random.choice(relevant_actions)

    def handle_infinite_loops(self, actions):
        relevant_actions = []
        for action in actions:
            if self.last_15_actions.count(action) < 3:
                relevant_actions.append(action)

        if len(relevant_actions) > 0:                                           # We are in infinite loop
            return relevant_actions
        else:                                                                   # We are not in infinite loop
            return actions

    def update_agent_history(self, action):
        if len(self.last_15_actions) >= 15:
            self.last_15_actions.pop(0)
        self.last_15_actions.append(action)
