(define (domain satellite_multi_effect)
(:requirements :equality :strips)
(:predicates
	 (on_board ?i ?s) (supports ?i ?m) (pointing ?s ?d) (power_avail ?s) (power_on ?i) (calibrated ?i) (have_image ?d ?m) (calibration_target ?i ?d)(satellite ?x) (direction ?x) (instrument ?x) (mode ?x) )
	
	(:action turn_to
	 :parameters ( ?s ?d_new ?d_prev ?d_rand)
	 :precondition
		(and (satellite ?s) (direction ?d_new) (direction ?d_prev) (direction ?d_rand) (pointing ?s ?d_prev))
	 :effect
		(probabilistic 0.7 (and (pointing ?s ?d_new) (not (pointing ?s ?d_prev)))
					   0.2 (and (pointing ?s ?d_rand) (not (pointing ?s ?d_prev)))					
		)
	)

	(:action switch_on
	 :parameters ( ?i1 ?i2 ?s)
	 :precondition
		(and (instrument ?i1) (instrument ?i2) (satellite ?s)  (on_board ?i1 ?s) (on_board ?i2 ?s) (power_avail ?s))
	 :effect
 			(probabilistic 0.6 (and (power_on ?i1) (not (calibrated ?i1)) (not (power_avail ?s)))
						   0.2 (and (power_on ?i2) (not (calibrated ?i2)) (not (power_avail ?s)))
			)
	)

	(:action switch_off
	 :parameters ( ?i ?s)
	 :precondition
		(and (instrument ?i) (satellite ?s)  (on_board ?i ?s) (power_on ?i))
	 :effect
		(probabilistic 0.8 (and (power_avail ?s) (not (power_on ?i)))
		)
	)

	(:action calibrate
	 :parameters ( ?s ?i ?d)
	 :precondition
		(and (satellite ?s) (instrument ?i) (direction ?d)  (on_board ?i ?s) (calibration_target ?i ?d) (pointing ?s ?d) (power_on ?i))
	 :effect
		(probabilistic 0.6 (calibrated ?i)
		)
	)

	(:action take_image
	 :parameters ( ?s ?d ?i ?m)
	 :precondition
		(and (satellite ?s) (direction ?d) (instrument ?i) (mode ?m)  (calibrated ?i) (on_board ?i ?s) (supports ?i ?m) (pointing ?s ?d) (power_on ?i))
	 :effect
		(probabilistic 0.75 (have_image ?d ?m)
		)
	)

)
