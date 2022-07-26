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
Q_TABLE_TO_UPDATE = None


class QLearningExecutor(Executor):
    def __init__(self, policy_file, process_id):
        super(QLearningExecutor, self).__init__()
        self.gt = None
        LAST_STATE = LAST_ACTION = LAST_H_STATE = Q_TABLE_TO_UPDATE = None

        self.lr = 0.8                       # The 'alpha' from Bellman's equation
        self.epsilon = 1                    # The indicator for epsilon greedy method
        self.gamma = 0.6                    # The 'gamma' from Bellman's equation
        self.process_id = process_id

        self.q1_table = None
        self.q2_table = None
        self.services = None

        self.parser = None
        self.perception = None

        self.last_5_states = []
        self.last_15_actions = []
        self.policy_file_q1 = policy_file + "-" + str(self.process_id) + "-A"
        self.policy_file_q2 = policy_file + "-" + str(self.process_id) + "-B"

        self.plan_history = []

    def initialize(self, services):
        self.services = services
        self.parser = services.parser
        self.perception = services.perception

        self.initialize_q_table()                       # change to json
        self.gt = gt.GoalService(services)

    def initialize_q_table(self):
        # First Q-Table
        if os.path.exists(self.policy_file_q1 + ".json") and os.stat(self.policy_file_q1 + ".json").st_size != 0:
            with open(self.policy_file_q1 + ".json", 'r') as fp:
                self.q1_table = json.load(fp)
        else:
            self.q1_table = {}
        # Second Q-Table
        if os.path.exists(self.policy_file_q2 + ".json") and os.stat(self.policy_file_q2 + ".json").st_size != 0:
            with open(self.policy_file_q2 + ".json", 'r') as fp:
                self.q2_table = json.load(fp)
        else:
            self.q2_table = {}

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
        global LAST_ACTION, LAST_STATE, LAST_H_STATE, Q_TABLE_TO_UPDATE

        self.update_q_table()
        self.epsilon = max(self.epsilon * 0.95, 0.3)

        current_state = self.services.perception.get_state()
        actions = CustomizedValidActions.get(CustomizedValidActions(self.parser, self.perception), current_state)

        # Defines which Q-Table we will update in this iteration
        q1_q2_tradeoff = "q2"
        if np.random.random() <= 0.5:
            q1_q2_tradeoff = "q1"

        if self.services.goal_tracking.reached_all_goals() or len(actions) == 0:
            io_service.IOService.write_q_table_to_file(self.policy_file_q1, self.q1_table)
            io_service.IOService.write_q_table_to_file(self.policy_file_q2, self.q2_table)
            return None
        elif len(actions) == 1:
            chosen_action = actions[0]
        else:
            exp_exp_tradeoff = random.uniform(0, 1)

            if exp_exp_tradeoff > self.epsilon:                                 # Agent => Exploitation
                chosen_action = self.choose_best_action(actions)
            else:                                                               # Agent => Exploration
                chosen_action = self.handle_infinite_loops(actions, True)

        self.update_agent_history(chosen_action, LAST_H_STATE, LAST_ACTION)

        LAST_ACTION = chosen_action
        Q_TABLE_TO_UPDATE = q1_q2_tradeoff
        LAST_STATE = self.services.perception.get_state()
        LAST_H_STATE = self.get_hashed_representation_for_state()

        self.append_to_q_value(LAST_H_STATE, LAST_ACTION)

        return chosen_action

    def append_to_q_value(self, h_state, action):
        # Q-Table-1
        if not self.q1_table.has_key(h_state):
            self.append_data_to_q_value(self.q1_table, h_state, action)
        else:
            self.append_data_to_q_value(self.q1_table, h_state, action, False)
        # Q-Table-2
        if not self.q2_table.has_key(h_state):
            self.append_data_to_q_value(self.q2_table, h_state, action)
        else:
            self.append_data_to_q_value(self.q2_table, h_state, action, False)

    @staticmethod
    def append_data_to_q_value(table, state, action, is_new=True):
        if is_new:
            table[state] = []
            action_to_reward = {action: 0}
            table[state].append(action_to_reward)
        else:
            for h_state in table.keys():
                if h_state == state:
                    for i, data in enumerate(table[h_state]):
                        if action in list(data.keys())[0]:
                            return
                    action_to_reward = {action: 0}
                    table[state].append(action_to_reward)
                    return

    def handle_infinite_loops(self, actions, is_random_choice=False):
        relevant_actions = []
        for action in actions:
            if self.last_15_actions.count(action) < 3:
                relevant_actions.append(action)

        if len(relevant_actions) > 0:                                           # We are in infinite loop
            if is_random_choice:
                return random.choice(relevant_actions)
            else:
                return relevant_actions
        else:                                                                   # We are not in infinite loop
            if is_random_choice:
                return random.choice(actions)
            else:
                return actions

    def update_agent_history(self, chosen_action, prev_state, prev_action):
        if len(self.last_5_states) >= 5:
            self.last_5_states.pop(0)
        if len(self.last_15_actions) >= 15:
            self.last_15_actions.pop(0)

        agent_at = self.get_hashed_representation_for_state()
        self.last_5_states.append(agent_at)
        self.last_15_actions.append(chosen_action)

        self.plan_history.append((prev_state, prev_action))

    def get_agent_location(self):
        current_state = self.services.perception.get_state()
        agent_at = list(current_state['at'])[0][1]
        return agent_at

    def get_max_q_table_value(self, table):
        value = float("-inf")
        agent_at = self.get_hashed_representation_for_state()

        if table.has_key(agent_at) is False:
            return 0
        for i, data in enumerate(table[agent_at]):
            for action, reward in data.iteritems():
                if reward > value:
                    value = reward
        return value

    @staticmethod
    def get_q_table_value(hashed_state, agent_action, table):
        value = float("-inf")
        for i, data in enumerate(table[hashed_state]):   # The data (state / action) exists in the Q-Table
            for action, reward in data.iteritems():
                if action == agent_action:
                    value = reward
        if value == float("-inf"):
            value = 0                                            # Add data (state / action) is not exist in the Q-Table
            table[hashed_state] = []
            action_to_reward = {agent_action: 0}
            table[hashed_state].append(action_to_reward)
        return value

    def update_q_table(self):
        global LAST_ACTION, LAST_STATE, LAST_H_STATE, Q_TABLE_TO_UPDATE

        if LAST_STATE is None or LAST_ACTION is None:
            return

        if Q_TABLE_TO_UPDATE == "q1":
            current_q_value = self.get_q_table_value(LAST_H_STATE, LAST_ACTION, self.q1_table)
            highest_q_value = self.get_max_q_table_value(self.q2_table)
        else:
            current_q_value = self.get_q_table_value(LAST_H_STATE, LAST_ACTION, self.q2_table)
            highest_q_value = self.get_max_q_table_value(self.q1_table)

        reward = self.get_reward()
        # Update Q(s,a):= (1 - alpha) * Q(s,a) + alpha * [R(s,a) + gamma * max Q(s',a')]
        new_q = (1 - self.lr) * current_q_value + self.lr * (reward + self.gamma * highest_q_value)

        if Q_TABLE_TO_UPDATE == "q1":
            self.set_value_into_q_table(self.q1_table, LAST_H_STATE, new_q)
        else:
            self.set_value_into_q_table(self.q2_table, LAST_H_STATE, new_q)

    @staticmethod
    def set_value_into_q_table(table, h_state, new_q):
        for i, data in enumerate(table[h_state]):   # The data (state / action) exists in the Q-Table
            for action, reward in data.iteritems():
                if action == LAST_ACTION:
                    table[h_state][i][action] = new_q
                    return

    def get_reward(self):
        global LAST_ACTION, LAST_STATE, LAST_H_STATE

        agent_at = self.get_hashed_representation_for_state()
        agent_last_at = self.get_hashed_representation_for_state(LAST_STATE)

        prev_state_goal_status = self.gt.get_num_of_uncompleted_goals(LAST_STATE)
        current_state_goal_status = self.gt.get_num_of_uncompleted_goals(self.services.perception.get_state())

        if len(current_state_goal_status) == 0:
            return 100
        elif len(current_state_goal_status) < len(prev_state_goal_status):
            return 100
        elif len(current_state_goal_status) > len(prev_state_goal_status):
            return -50
        elif agent_at == agent_last_at:
            return -3
        elif agent_at in self.last_5_states:
            return -20
        elif self.last_15_actions.count(LAST_ACTION) > 3:
            return -20
        else:
            return -1

    def merge_q_tables(self):
        merged = copy.deepcopy(self.q1_table)
        for h_action in self.q2_table:
            for i, data in enumerate(self.q2_table[h_action]):
                action = data.keys()[0]
                q2_action_value = data.values()[0]
                q1_action_value = merged[h_action][i][action]
                normalized_data = (q1_action_value + q2_action_value) / 2
                merged[h_action][i][action] = normalized_data
        return merged

    def choose_best_action(self, actions):
        best_actions = []
        best_action_value = float('-inf')
        agent_at = self.get_hashed_representation_for_state()

        relevant_actions = self.handle_infinite_loops(actions)
        random.shuffle(relevant_actions)

        merged_table = self.merge_q_tables()

        if not merged_table.has_key(agent_at):
            return random.choice(relevant_actions)

        for i, data in enumerate(merged_table[agent_at]):
            for action, reward in data.iteritems():
                if action in relevant_actions:
                    if reward > best_action_value:
                        best_actions = [action]
                        best_action_value = reward
                    elif reward == best_action_value:
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


class QLearningExecutive(Executor):
    def __init__(self, policy_files):
        super(QLearningExecutive, self).__init__()
        self.services = None
        self.parser = None
        self.perception = None
        self.last_15_actions = []

        self.q1_table = {}
        self.q2_table = {}
        self.merged_table = {}

        self.policy_merged_q = os.getcwd() + "/Files/Meta-Data-Files/" + "executive"
        self.policy_file_q1 = os.getcwd() + "/Files/Meta-Data-Files/" + policy_files[0] + ".json"
        self.policy_file_q2 = os.getcwd() + "/Files/Meta-Data-Files/" + policy_files[1] + ".json"

    def initialize(self, services):
        self.services = services
        self.parser = services.parser
        self.perception = services.perception
        self.get_merged_q_table()

    def get_merged_q_table(self):
        with open(self.policy_file_q1, 'r') as fp:
            self.q1_table = json.load(fp)
        with open(self.policy_file_q2, 'r') as fp:
            self.q2_table = json.load(fp)

        self.merged_table = self.merge_q_tables()

    def merge_q_tables(self):
        merged = copy.deepcopy(self.q1_table)
        for h_action in self.q2_table:
            for i, data in enumerate(self.q2_table[h_action]):
                action = data.keys()[0]
                q2_action_value = data.values()[0]
                q1_action_value = merged[h_action][i][action]
                normalized_data = (q1_action_value + q2_action_value) / 2
                merged[h_action][i][action] = normalized_data
        return merged

    def next_action(self):
        current_state = self.services.perception.get_state()
        actions = CustomizedValidActions.get(CustomizedValidActions(self.parser, self.perception), current_state)

        action = None
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
        best_action_value = float('-inf')
        agent_at = self.get_hashed_representation_for_state()

        relevant_actions = self.handle_infinite_loops(actions)
        random.shuffle(relevant_actions)

        if not self.merged_table.has_key(agent_at):
            return random.choice(relevant_actions)

        for i, data in enumerate(self.merged_table[agent_at]):
            for action, reward in data.iteritems():
                if action in relevant_actions:
                    if reward > best_action_value:
                        best_actions = [action]
                        best_action_value = reward
                    elif reward == best_action_value:
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

    def get_relevant_actions(self, actions):
        relevant_actions = []
        for action in actions:
            if action in self.last_15_actions:
                continue
            relevant_actions.append(action)
        return relevant_actions
