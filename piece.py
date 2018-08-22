import pygame

class piece():

	# Dictionary containing allowed move directions for each piece type
	moves_dict = {
	'pawn_b': [[0,-1]],
	'pawn_w': [[0,1]],
	'king': [[0,1],[1,0],[0,-1],[-1,0],[1,1],[-1,1],[1,-1],[-1,-1]],
	'bishop':[[1,1],[-1,1],[1,-1],[-1,-1]],
	'rook': [[0,1],[1,0],[0,-1],[-1,0]], 
	'queen': [[0,1],[1,0],[0,-1],[-1,0],[1,1],[-1,1],[1,-1],[-1,-1]], 
	'knight': [[1,2],[-1,2],[1,-2],[-1,-2],[2,1],[-2,1],[2,-1],[-2,-1]],
	}

	# Dictionary containing movement range for each piece type
	ranges_dict = {
	'pawn_b': 2,
	'pawn_w': 2,
	'king': 1,
	'bishop': 7,
	'rook': 7,
	'queen': 7,
	'knight': 1,
	}

	printing_dict = {
	'pawn_w': '',
	'pawn_b': '',
	'rook': 'R',
	'knight': 'N',
	'bishop': 'B',
	'queen': 'Q',
	'king': 'K'
	}

	def __init__(self, type_, colour, pos):
		# Piece constructor
		self.type_ = type_
		self.moves = piece.moves_dict[type_]
		self.range = piece.ranges_dict[type_]
		self.pos = pos
		self.colour = colour
		self.selected = False
		self.moved = False
		box_side = 100
		if type_[:4] == 'pawn': imtype = 'pawn' # Deals with having different pawn types
		else: imtype = type_
		im = pygame.image.load('assets/' + imtype + '_' + colour + '.png') # Auto-load relevant image
		im = pygame.transform.scale(im, (box_side, box_side)) # Scale image to board size
		self.image = im
		self.prefix = piece.printing_dict[type_]

	def printpiece(self):
		print(
			'Type: ' + self.type_ + 
			'\nColour: ' + self.colour +
			'\nPosition: ' + self.pos +
			'\nHas moved: ' + str(self.moved)
			)