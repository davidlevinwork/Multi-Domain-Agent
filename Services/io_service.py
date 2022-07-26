import json

import numpy as np
from prettytable import PrettyTable


class IOService:
    def __init__(self):
        pass

    @staticmethod
    def write_q_table_to_file(file_name, q_table):
        file_name = file_name + ".json"
        with open(file_name, 'w') as f:
            json.dump(q_table, f)
            f.close()

    @staticmethod
    def write_q_table_helper_to_file(file_name, q_table, actions, states):
        file_name_helper = file_name + "_helper.txt"
        t_headers = list(actions)
        t_headers.insert(0, "State")

        table = PrettyTable([header for header in t_headers])

        for i, n_row in enumerate(q_table):
            row = list([col for col in n_row])
            row.insert(0, states[i])
            table.add_row([col for col in row])

        with open(file_name_helper, 'wb') as w:
            w.write(str(table))
        w.close()

    @staticmethod
    def extract_action_space_from_file(file_name):
        relevant_actions = []
        lines = open(file_name).read().splitlines()
        for line in lines:
            if "State" in line:
                actions = [col.replace(" ", "") for col in line.split("|")]
                relevant_actions = [action for action in actions if action != ""]
                relevant_actions = [action for action in relevant_actions if action != "State"]
        return relevant_actions

    @staticmethod
    def extract_state_space_from_file(file_name):
        relevant_states = []
        lines = open(file_name).read().splitlines()
        for line in lines:
            if "|" in line and not "State" in line:
                state = line.split("|")[1].strip()
                relevant_states.append(state)
        return relevant_states
