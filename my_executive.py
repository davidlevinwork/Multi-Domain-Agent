import sys
from Executers.BasicAgent import BasicAgent


class ProblemOrganizer:
    def __init__(self, flag, domain, problem):
        self.flag = flag
        self.domain = domain
        self.problem = problem

    def run(self):
        if self.is_deterministic():
            agent = BasicAgent("Deterministic", self.flag, self.domain, self.problem)
        else:
            agent = BasicAgent("Probabilistic", self.flag, self.domain, self.problem)
        agent.run()

    def is_deterministic(self):
        with open(self.domain) as f:
            content = f.read()
            return not "probabilistic" in content


if __name__ == '__main__':
    input_flag = sys.argv[1]
    domain_path = sys.argv[2]
    problem_path = sys.argv[3]

    my_executive = ProblemOrganizer(input_flag, domain_path, problem_path)
    my_executive.run()
