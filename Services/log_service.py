import os
import re
from datetime import datetime

log_file_name = os.path.join(os.getcwd(), "Files", "Log-Files", "Log.txt")


class LogService:
    def __init__(self):
        pass

    @staticmethod
    def initialize():
        try:
            open(log_file_name, 'w').close()
        except OSError:
            print('Failed creating the log file.')
        else:
            print('Log File created successfully.')

    @staticmethod
    def print_to_log(mode="Info", data=None):
        """
        Append the given {data} to the log file.
        Default mode is "Info".
        """
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y %H:%M:%S")
        str_format = "[{0: ^21}] | [{1:^9}] : {2}\n".format(date_str, mode, data)
        try:
            log_file = open(log_file_name, 'a')
            log_file.write(str_format)
            log_file.close()
        except OSError:
            print("The log file doesn't exist!")

    @staticmethod
    def parse_learning_results(number_of_process):
        learning_results = []
        try:
            f = open(log_file_name, 'r')
            lines = f.readlines()
            for line in lines:
                if "Result" in line:
                    learning_results.append(line)
        except OSError:
            print("The log file doesn't exist!")

        # Build the data structure for the learning results
        process_to_result = {}
        for process_id in range(number_of_process):
            process_to_result[str(process_id)] = []
        # Fill the data structure for the learning results
        for line in learning_results:
            process = re.findall(r'\[.*?\]', line)[2].replace("[", "").replace("]", "")
            result = re.findall(r'\[.*?\]', line)[3].replace("[", "").replace("]", "")
            process_to_result[process].append(int(result))
        # Find the best Q-Table
        best_process = None
        best_result = float('inf')
        for process in process_to_result:
            l = process_to_result[process]
            result = sum(l) / float(len(l))
            if result < best_result:
                best_result = result
                best_process = process
        return best_process
