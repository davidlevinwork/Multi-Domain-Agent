import os
import re
import numpy as np
import multiprocessing

from pddlsim.local_simulator import LocalSimulator
from Executers.DeterministicAgent import PlanDispatcher
from Executers.RMaxAgent import RMaxExecutor, RMaxExecutive
from Services import log_service, dispose_service, io_service
from Executers.RandomAgent import RandomExecutor, SmartRandomExecutor
from Executers.QLearningAgent import QLearningExecutor, QLearningExecutive


class BasicAgent:
    def __init__(self, model_type, flag, domain, problem):
        self.flag = flag
        self.domain = domain
        self.problem = problem
        self.model_type = model_type
        self.number_of_learning_iterations = 3
        self.process_id_to_learn_result = {}
        self.policy_file = None
        self.number_of_cpus = multiprocessing.cpu_count()

    def set_policy_file_name(self, agent):
        # The problem name will be composed of two parts: "<env>-<task>.pddl"
        problem_name = self.problem.split('/')[-1][:-5]
        evn_name = problem_name.split("-")[0]
        task_name = problem_name.split("-")[1]
        # Q-Learning problems - the environment and the task are important for the execution time
        if agent == "Q-Learning":
            path = os.path.join(os.getcwd(), "Files", "Meta-Data-Files", evn_name + "-" + task_name)
        # R-Max problems - only the environment is important for the execution time
        else:
            path = os.path.join(os.getcwd(), "Files", "Meta-Data-Files", evn_name)
        return path

    def initialize_log_service(self):
        log_service.LogService.initialize()
        self.print_welcome_message()

    def calculate_model_complexity(self):
        """
        Function role is to obtain a "superficial" assessment of the complexity of the given model.
        """
        number_of_goals = self.get_number_of_goals_in_problem()
        number_of_actions = self.get_number_of_actions_in_domain()
        number_of_objects = self.get_number_of_actions_in_problem()

        if number_of_goals == 1:
            return "Easy"
        elif number_of_goals > 3:
            return "Hard"
        elif number_of_objects * number_of_actions > 400:
            return "Hard"
        elif number_of_objects * number_of_actions < 400:
            return "Easy"
        else:
            return "Easy"

    def get_number_of_actions_in_domain(self):
        f = open(self.domain)
        data = f.readlines()

        counter = 0
        for line in data:
            if "(:action" in line and ";;;" not in line:
                counter += 1
        f.close()
        return counter

    def get_number_of_actions_in_problem(self):
        f = open(self.problem)
        data = f.readlines()

        parsing = False
        relevant_lines = []
        for line in data:
            if line.startswith("(:objects"):
                parsing = True
            elif line.startswith("(:init"):
                parsing = False
            if parsing:
                relevant_lines.append(line)
        f.close()

        counter = 0
        for line in relevant_lines:
            s_line = line.split()
            if len(s_line) == 1 and s_line[0] == "(:objects":
                continue
            s_line_counter = len([word for word in s_line if word != ")"])
            counter += s_line_counter
        return counter

    def get_number_of_goals_in_problem(self):
        f = open(self.problem)
        data = f.readlines()

        parsing = False
        relevant_lines = []
        for line in data:
            if line.startswith("(:goal"):
                parsing = True
            elif line.startswith(")"):
                parsing = False
            if parsing:
                relevant_lines.append(line)
        f.close()

        counter = 0
        for line in relevant_lines:
            counter += len(re.findall(r'\(.*?\)', line))
        return counter

    def run(self):
        if self.flag == "-L":
            self.learning()
            dispose_service.DisposeService.clean_log_files_after_learning()
        if self.flag == "-E":
            self.executing()

    def executing(self):
        if self.model_type == "Deterministic":
            result = LocalSimulator().run(self.domain, self.problem, PlanDispatcher())
        elif self.model_type == "Probabilistic":
            level = self.calculate_model_complexity()
            if level == "Easy":
                self.policy_file = self.set_policy_file_name("Q-Learning")
                policy_files = self.get_q_learning_executable_file()
                if policy_files is None:
                    result = LocalSimulator().run(self.domain, self.problem, SmartRandomExecutor())
                else:
                    result = LocalSimulator().run(self.domain, self.problem, QLearningExecutive(policy_files))
            elif level == "Hard":
                self.policy_file = self.set_policy_file_name("R-Max")
                policy_file = self.policy_file + "-0.json"

                # Check if we have learning files from the given domain, problem and environment
                files_exists = True
                if not os.path.exists(policy_file) or not os.stat(policy_file).st_size != 0:
                    files_exists = False
                if files_exists:
                    result = LocalSimulator().run(self.domain, self.problem, RMaxExecutive(policy_file))
                else:
                    # If we miss the learning files - run a random executer
                    result = LocalSimulator().run(self.domain, self.problem, SmartRandomExecutor())

    def learning(self):
        """
        Function role is to manage the learning phase as follows:
        If the given model is Deterministic --> We can ignore the learning phase (exit code 128)
        If the given model is Probabilistic --> We will execute the learning phase with an agent who fits the complexity
        of the problem:
            * Easy (complexity) problems- Q-Learning executer
            * Hard (complexity) problems- R-Max executer
        """
        if self.model_type == "Deterministic":
            exit(128)
        elif self.model_type == "Probabilistic":
            level = self.calculate_model_complexity()
            if level == "Easy":
                self.policy_file = self.set_policy_file_name("Q-Learning")
                for i in range(self.number_of_learning_iterations):
                    manager = multiprocessing.Manager()
                    return_dict = manager.dict()
                    processes = []
                    for j in range(self.number_of_cpus):
                        process = multiprocessing.Process(target=self.run_executer, args=(return_dict, "Q-Learning", j))
                        processes.append(process)
                        process.start()
                    for proc in processes:
                        proc.join()
                    self.parse_learning_result(return_dict)
                self.create_q_table_executable_file()
            elif level == "Hard":
                self.policy_file = self.set_policy_file_name("R-Max")
                for i in range(self.number_of_learning_iterations):
                    manager = multiprocessing.Manager()
                    return_dict = manager.dict()
                    processes = []
                    for j in range(1):
                        process = multiprocessing.Process(target=self.run_executer, args=(return_dict, "R-Max", j))
                        processes.append(process)
                        process.start()
                    for proc in processes:
                        proc.join()
                    self.parse_learning_result(return_dict)

    def run_executer(self, return_dict, mode, process_id):
        s = "Process [{}] starting the LEARNING phase.".format(process_id + 1)
        log_service.LogService.print_to_log("Info", s)

        if mode == "Q-Learning":
            result = LocalSimulator().run(self.domain, self.problem, QLearningExecutor(self.policy_file, process_id))
            return_dict[process_id] = result
        elif mode == "R-Max":
            result = LocalSimulator().run(self.domain, self.problem, RMaxExecutor(self.policy_file, process_id))
            return_dict[process_id] = result

    def set_learning_result(self, process_id_to_result):
        for process_id in process_id_to_result.keys():
            result = process_id_to_result[process_id]
            if result.success == "False":
                continue
            self.process_id_to_learn_result[process_id] = result.total_actions

    def parse_learning_result(self, process_id_to_result):
        self.set_learning_result(process_id_to_result)

        s = "------------------------------------------------------"
        log_service.LogService.print_to_log("Info", s)
        for process_id in process_id_to_result.keys():
            result = process_id_to_result[process_id]
            s = "Learning results of process [{0}] are:".format(process_id)
            log_service.LogService.print_to_log("Info", s)

            lines = str(result).split("\n")
            for line in lines:
                if "Success" in line:
                    log_service.LogService.print_to_log("Info", line)
                elif "Total time" in line:
                    log_service.LogService.print_to_log("Info", line)
                elif "Total actions" in line:
                    log_service.LogService.print_to_log("Info", line)
                elif "Failed actions" in line:
                    log_service.LogService.print_to_log("Info", line)
            s = "Summary: process [{0}] --> [{1}] total actions".format(process_id, result.total_actions)
            log_service.LogService.print_to_log("Result", s)
            s = "------------------------------------------------------"
            log_service.LogService.print_to_log("Info", s)

    def print_welcome_message(self):
        s1 = "Welcome to our agent service! We hope you will enjoy our services."
        s2 = "The following arguments were submitted: [flag : {0}] , [domain : {1}] , [problem : {2}]".\
            format(self.flag, self.domain, self.problem)
        log_service.LogService.print_to_log("Info", s1)
        log_service.LogService.print_to_log("Info", s2)

    def merge_learning_result(self):
        process_id_by_result = sorted(self.process_id_to_learn_result.items(), key=lambda x: x[1])

        self.print_learn_summary(process_id_by_result[0])

        best_process = process_id_by_result[0]
        for process in process_id_by_result[1:]:
            self.normalize_q_table(process, best_process)

    @staticmethod
    def print_learn_summary(result):
        s = "Best result for this learning iteration is for process [{0}] : [{1}] steps".format(result[0], result[1])
        log_service.LogService.print_to_log("Debug", s)
        s = "------------------------------------------------------"
        log_service.LogService.print_to_log("Info", s)

    def normalize_q_table(self, current_process_values, best_process_values):
        current_process_q1 = self.policy_file + "-" + str(current_process_values[0]) + "-A"
        normalized_values_q1 = self.get_normalize_q_table(current_process_values, best_process_values, "-A")

        current_process_q2 = self.policy_file + "-" + str(current_process_values[0]) + "-B"
        normalized_values_q2 = self.get_normalize_q_table(current_process_values, best_process_values, "-B")

        io_service.IOService.write_q_table_to_file(current_process_q1, normalized_values_q1)
        io_service.IOService.write_q_table_to_file(current_process_q2, normalized_values_q2)

    def get_normalize_q_table(self, current_process_values, best_process_values, type):
        current_process = self.policy_file + "-" + str(current_process_values[0]) + type
        current_process_np_values = self.get_normalized_q_table_values(current_process)

        best_process = self.policy_file + "-" + str(best_process_values[0]) + type
        best_process_np_values = self.get_normalized_q_table_values(best_process)

        factor = float(best_process_values[1]) / float(current_process_values[1])
        normalized_values = (current_process_np_values * factor) + (best_process_np_values * (1 - factor))
        return normalized_values

    @staticmethod
    def get_normalized_q_table_values(file_name):
        values = []
        file_name = file_name + ".txt"
        lines = open(file_name).read().splitlines()
        for line in lines:
            values.append(np.fromstring(line, dtype=float, sep=' '))

        return np.array(values)

    def create_q_table_executable_file(self):
        best_policy_id = log_service.LogService.parse_learning_results(self.number_of_cpus)
        best_policy = self.policy_file + "-" + str(best_policy_id)
        policy_file = self.policy_file.split("/")[-1]
        dispose_service.DisposeService.clean_files_after_learning(best_policy, policy_file)

    def get_q_learning_executable_file(self):
        files = []
        for item in os.listdir(os.getcwd() + "/Files/Meta-Data-Files"):
            if self.policy_file.split("/")[-1] in item:
                files.append(item.split('.')[0])
        if len(files) < 2:
            return None
        files.sort()
        return files[0], files[1]
