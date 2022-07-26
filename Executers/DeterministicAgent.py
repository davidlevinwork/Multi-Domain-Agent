import pddlsim.planner as planner
from pddlsim.executors.executor import Executor


class PlanDispatcher(Executor):
    def __init__(self):
        super(PlanDispatcher, self).__init__()
        self.steps = []

    def initialize(self, services):
        self.steps = planner.make_plan(services.pddl.domain_path, services.pddl.problem_path)

    def next_action(self):
        if len(self.steps) > 0:
            return self.steps.pop(0).lower()
        return None
