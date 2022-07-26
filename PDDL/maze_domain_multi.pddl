(define (domain maze_food)
	(:predicates
		 (at ?p ?t) (person ?p) (empty ?x) (wall ?x) (north ?a ?b) (south ?a ?b) (west ?a ?b) (east ?a ?b) (food ?f1) (has ?p ?f)
	)

	(:action move-north0
	 :parameters ( ?p ?a ?b)
	 :precondition
		(and (person ?p) (empty ?b) (at ?p ?a)  (north ?a ?b))
	 :effect
		(probabilistic  0.5 (and (at ?p ?b) (not (at ?p ?a)))
		)
	)
	(:action move-north1
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (north ?a ?b) (south ?a ?c))
	 :effect
		(probabilistic  0.75 (and (at ?p ?b) (not (at ?p ?a)))
		                0.25 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)

	(:action move-north2
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (north ?a ?b) (west ?a ?c))
	 :effect
		(probabilistic  0.75 (and (at ?p ?b) (not (at ?p ?a)))
		                0.25 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)
	(:action move-north3
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (north ?a ?b) (east ?a ?c))
	 :effect
		(probabilistic  0.75 (and (at ?p ?b) (not (at ?p ?a)))
		                0.25 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)
	(:action move-south0
	 :parameters ( ?p ?a ?b)
	 :precondition
		(and (person ?p) (empty ?b) (at ?p ?a)  (south ?a ?b))
	 :effect
		(probabilistic  0.2 (and (at ?p ?b) (not (at ?p ?a)))
		)
	)
	(:action move-south1
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (south ?a ?b) (north ?a ?c))
	 :effect
		(probabilistic  0.8 (and (at ?p ?b) (not (at ?p ?a)))
		                0.2 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)
	(:action move-south2
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (south ?a ?b) (west ?a ?c))
	 :effect
		(probabilistic  0.8 (and (at ?p ?b) (not (at ?p ?a)))
		                0.2 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)
	(:action move-south3
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (south ?a ?b) (east ?a ?c))
	 :effect
		(probabilistic  0.8 (and (at ?p ?b) (not (at ?p ?a)))
		                0.2 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)
	(:action move-west0
	 :parameters ( ?p ?a ?b)
	 :precondition
		(and (person ?p) (empty ?b) (at ?p ?a)  (west ?a ?b))
	 :effect
		(probabilistic  0.3 (and (at ?p ?b) (not (at ?p ?a)))
		)
	)

	(:action move-west1
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (west ?a ?b) (north ?a ?c))
	 :effect
		(probabilistic  0.6 (and (at ?p ?b) (not (at ?p ?a)))
		                0.4 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)
	(:action move-west2
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (west ?a ?b) (north ?a ?c))
	 :effect
		(probabilistic  0.6 (and (at ?p ?b) (not (at ?p ?a)))
		                0.4 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)
	(:action move-west3
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (west ?a ?b) (east ?a ?c))
	 :effect
		(probabilistic  0.6 (and (at ?p ?b) (not (at ?p ?a)))
		                0.4 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)


	(:action move-east0
	 :parameters ( ?p ?a ?b)
	 :precondition
		(and (person ?p) (empty ?b) (at ?p ?a)  (east ?a ?b))
	 :effect
		(probabilistic  0.4 (and (at ?p ?b) (not (at ?p ?a)))
		)
	)
	(:action move-east1
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (east ?a ?b) (north ?a ?c))
	 :effect
		(probabilistic  0.6 (and (at ?p ?b) (not (at ?p ?a)))
		                0.4 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)
	(:action move-east2
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (east ?a ?b) (north ?a ?c))
	 :effect
		(probabilistic  0.6 (and (at ?p ?b) (not (at ?p ?a)))
		                0.4 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)
	(:action move-east3
	 :parameters ( ?p ?a ?b ?c)
	 :precondition
		(and (person ?p) (empty ?b) (empty ?c) (at ?p ?a)  (east ?a ?b) (north ?a ?c))
	 :effect
		(probabilistic  0.6 (and (at ?p ?b) (not (at ?p ?a)))
		                0.4 (and (at ?p ?c) (not (at ?p ?a)))
		)
	)
	(:action pick-food
	 :parameters ( ?p ?a ?f)
	 :precondition
		(and (person ?p) (food ?f) (at ?p ?a) (at ?f ?a))
	 :effect
		(and (has ?p ?f)
		)
	)

)
