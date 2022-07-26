import os


class DisposeService:
    def __init__(self):
        pass

    @staticmethod
    def dispose():
        files_to_remove = get_files_to_delete()
        for f in files_to_remove:
            try:
                os.remove(f)
            except OSError:
                pass

    @staticmethod
    def clean_files_after_learning(save_file, policy_file):
        files_to_remove = get_files_to_delete(False)
        for f in files_to_remove:
            try:
                if save_file in f or policy_file not in f:
                    continue
                os.remove(f)
            except OSError:
                pass

    @staticmethod
    def clean_log_files_after_learning():
        files_to_remove = ["tpm.ipc", "tmp_problem_generation", "Files/Log-Files/Log.txt"]
        for f in files_to_remove:
            try:
                os.remove(f)
            except OSError:
                pass


def get_files_to_delete(all_files=True):
    files = []
    if all_files:
        files = ["tpm.ipc", "tmp_problem_generation", "Files/Log-Files/Log.txt"]

    for item in os.listdir(os.getcwd() + "/Files/Meta-Data-Files"):
        if item.endswith(".json"):
            path_to_file = os.path.join(os.getcwd(), "Files", "Meta-Data-Files", item)
            files.append(path_to_file)
    return files
