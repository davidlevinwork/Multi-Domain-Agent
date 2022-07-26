from pddlsim.parser_independent import Literal, Disjunction, Conjunction


class GoalService:

    def __init__(self, services):
        self.parser = services.parser
        self.perception = services.perception

    def get_num_of_uncompleted_goals(self, state=None):
        if state is not None:
            return self.check_goals_status(state)
        return self.parser.goals[:]

    def check_goals_status(self, state):
        completed_goals = []
        uncompleted_goals = self.parser.goals[:]

        to_remove = list()

        for goal in uncompleted_goals:
            done_subgoal = self.parser.test_condition(goal, state)
            if done_subgoal:
                to_remove.append(goal)

        for goal in to_remove:
            completed_goals.append(goal)
            uncompleted_goals.remove(goal)

        return uncompleted_goals
