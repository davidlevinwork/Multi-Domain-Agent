(define (domain maze)
(:predicates
	 (at ?p ?t) (person ?p) (empty ?x) (wall ?x) (north ?a ?b) (south ?a ?b) (west ?a ?b) (east ?a ?b))

(:action move-north
 :parameters ( ?p ?a ?b)
 :precondition
	(and (person ?p) (empty ?b) (at ?p ?a)  (north ?a ?b))
 :effect
	(and (at ?p ?b) (not (at ?p ?a))))
(:action move-south
 :parameters ( ?p ?a ?b)
 :precondition
	(and (person ?p) (empty ?b) (at ?p ?a)  (south ?a ?b))
 :effect
	(and (at ?p ?b) (not (at ?p ?a))))
(:action move-west
 :parameters ( ?p ?a ?b)
 :precondition
	(and (person ?p) (empty ?b) (at ?p ?a)  (west ?a ?b))
 :effect
	(and (at ?p ?b) (not (at ?p ?a))))
(:action move-east
 :parameters ( ?p ?a ?b)
 :precondition
	(and (person ?p) (empty ?b) (at ?p ?a)  (east ?a ?b))
 :effect
	(and (at ?p ?b) (not (at ?p ?a))))


)
