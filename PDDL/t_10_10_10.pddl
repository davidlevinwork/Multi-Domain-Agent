
(define (problem maze_food-prob2)
(:domain maze_food)
(:objects
	person1
	food1
	food2
	start_tile
	c0
	c1
	c2
	c3
	c4
	c5
	c6
	c7
	c8
	g0
	g1
	g2
	g3
	g4
	g5
	g6
	g7
	g8
	d0
	d1
	d2
	d3
	d4
	d5
	d6
	d7
	d8
	)
(:init
	(empty start_tile)
	(empty c0)
	(empty c1)
	(empty c2)
	(empty c3)
	(empty c4)
	(empty c5)
	(empty c6)
	(empty c7)
	(empty c8)
	(empty g0)
	(empty g1)
	(empty g2)
	(empty g3)
	(empty g4)
	(empty g5)
	(empty g6)
	(empty g7)
	(empty g8)
	(empty d0)
	(empty d1)
	(empty d2)
	(empty d3)
	(empty d4)
	(empty d5)
	(empty d6)
	(empty d7)
	(empty d8)
	
	(east start_tile c0)
	(west c0 start_tile)
	(east c0 c1)
	(west c1 c0)
	(east c1 c2)
	(west c2 c1)
	(east c2 c3)
	(west c3 c2)
	(east c3 c4)
	(west c4 c3)
	(east c4 c5)
	(west c5 c4)
	(east c5 c6)
	(west c6 c5)
	(east c6 c7)
	(west c7 c6)
	(east c7 c8)
	(west c8 c7)
	
	(north g0 g1)
	(south g1 g0)
	(north g1 g2)
	(south g2 g1)
	(north g2 g3)
	(south g3 g2)
	(north g3 g4)
	(south g4 g3)
	(north g4 g5)
	(south g5 g4)
	(north g5 g6)
	(south g6 g5)
	(north g6 g7)
	(south g7 g6)
	(north g7 g8)
	(south g8 g7)
	
	(south d0 d1)
	(north d1 d0)
	(south d1 d2)
	(north d2 d1)
	(south d2 d3)
	(north d3 d2)
	(south d3 d4)
	(north d4 d3)
	(south d4 d5)
	(north d5 d4)
	(south d5 d6)
	(north d6 d5)
	(south d6 d7)
	(north d7 d6)
	(south d7 d8)
	(north d8 d7)
	
	(north c8 g0)
	(south g0 c8)
	
	(south c8 d0)
	(north d0 c8)
	
    (person person1)
    	(food food1)
	(food food2)
    (at person1 start_tile)   
)
(:reveal ((and (at person1 g4) (not (has person1 food1))) (at food1 g4) 1)
		 ((and (at person1 d4) (not (has person1 food2))) (at food2 d4) 0.8)
)
(:goal 
    (and (has person1 food1) (has person1 food2))
)
)
