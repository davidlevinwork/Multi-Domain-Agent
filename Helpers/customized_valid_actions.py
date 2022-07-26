SUPPORTS_LAPKT = False


class CustomizedValidActions:
    def __init__(self, parser, perception):
        self.parser = parser
        self.perception = perception

    def get(self, current_state=None):
        if current_state is None:
            current_state = self.perception.get_state()
        possible_actions = []
        for (name, action) in self.parser.actions.items():
            for candidate in self.get_valid_candidates_for_action(current_state, action):
                possible_actions.append(action.action_string(candidate))
        return possible_actions

    @staticmethod
    def join_candidates(previous_candidates, new_candidates, p_indexes, n_indexes):
        shared_indexes = p_indexes.intersection(n_indexes)
        if previous_candidates is None:
            return new_candidates
        result = []
        for c1 in previous_candidates:
            for c2 in new_candidates:
                if all([c1[idx] == c2[idx] for idx in shared_indexes]):
                    merged = c1[:]
                    for idx in n_indexes:
                        merged[idx] = c2[idx]
                    result.append(merged)
        return result

    @staticmethod
    def indexed_candidate_to_dict(candidate, index_to_name):
        return {name[0]: candidate[idx] for idx, name in index_to_name.items()}

    def on_action(self, action_sig):
        pass

    def get_valid_candidates_for_action(self, state, action):
        objects = dict()
        signatures_to_match = {name: (idx, t) for idx, (name, t) in enumerate(action.signature)}
        index_to_name = {idx: name for idx, name in enumerate(action.signature)}
        candidate_length = len(signatures_to_match)
        found = set()
        candidates = None
        # copy all preconditions
        for precondition in sorted(action.precondition, key=lambda x: len(state[x.name])):
            truths = state[precondition.name]
            if len(truths) == 0:
                return []
            # map from predicate index to candidate index
            dtypes = [(name, 'object') for name in precondition.signature]
            reverse_map = {idx: signatures_to_match[pred][0] for idx, pred in enumerate(precondition.signature)}
            indexes = reverse_map.values()
            overlap = len(found.intersection(indexes)) > 0
            precondition_candidates = []
            for entry in truths:
                candidate = [None] * candidate_length
                for idx, param in enumerate(entry):
                    candidate[reverse_map[idx]] = param
                precondition_candidates.append(candidate)

            candidates = self.join_candidates(candidates, precondition_candidates, found, indexes)
            found = found.union(indexes)
        return [self.indexed_candidate_to_dict(c, index_to_name) for c in candidates]
