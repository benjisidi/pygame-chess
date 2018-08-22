from piece import piece
import chess_logic as clogic
import readline
import numpy as np

# Read a traditionally written move and return the board state following that move
def parse(board, move, colour):
	pawn_specifiers = 'abcdefgh'
	piece_specifiers = {e: k for k, e in piece.printing_dict.iteritems()} # Invert type dictionary
	move = move.replace('+', '') #Drop unneeded check and take specifiers
	move = move.replace('x', '')
	move = move.replace('#', '')
	
	# ---Deal with castling special case before anything else
	if move in ('O-O', 'O-O-O'):
		king = [x for x in board if getattr(x, 'colour') == colour and getattr(x, 'type_') == 'king']
		if colour == 'w':
			row = '1'
		else:
			row = '8'
		if len(move) == 3:
			col = 'G'
		else:
			col = 'C'
		sq = col + row
		return clogic.move_piece(king[0], sq, board)

	# ---Pawn moves of the form e[x]b4[=Q][+]
	queen = False
	if '=' in move:
		new_piece_type = piece_specifiers[move[move.index('=')+1]] # Get index of 'Q' in example and use it to grab relevant piece type
		move = move[:move.index('=')] # Truncate before "=" so we have a normal move format
		queen = True
	if len(move) == 2: # Simplest case; eg 'e4'
		pawns = [piece_ for piece_ in board if 'pawn' in getattr(piece_, 'type_') and\
				 getattr(piece_, 'colour') == colour and getattr(piece_, 'pos')[0].lower() == move[0]]
		for pawn in pawns:
			if move.upper() in clogic.available_moves(pawn, board, ch=True):
				if not queen:
					return clogic.move_piece(pawn, move.upper(), board)	
				else:
					board_temp = clogic.move_piece(pawn, move.upper(), board)
					return clogic.queen([pawn, new_piece_type, board_temp])
	elif move[0] in pawn_specifiers: # This leaves taking moves of form e[x]b4
		row = move[0]
		square = move[1:3].upper()
		pawns = [piece_ for piece_ in board if 'pawn' in getattr(piece_, 'type_') and\
				 getattr(piece_, 'colour') == colour and getattr(piece_, 'pos')[0].lower() == move[0]]
		for pawn in pawns:
			if square not in clogic.available_moves(pawn, board, ch=True):
				pawns.remove(pawn)
		#Pawns should now just contain the piece we want
		board_temp = clogic.move_piece(pawns[0], square, board)
		if not queen: 
			return board_temp
		else:
			return clogic.queen([pawns[0], new_piece_type, board_temp])

	# ---Other moves
	# At this point, moves are of the form N[b,1][x]c3[+]
	if len(move) == 3: #Standard move format, no identifier
		identifier = move[0]
		square = move[1:3].upper()
		row, col = '', ''
	else:
		try:
			row = int(move[1])
			col = ''
		except ValueError:
			col = move[1]
			row = ''
		square = move[2:4].upper()
	piecetype = piece_specifiers[move[0]]
	#Filter pieces by type and colour, then additional identifier to find right one
	candidates = [piece_ for piece_ in board if getattr(piece_, 'type_') == piecetype and\
												getattr(piece_, 'colour') == colour]
	for cand in candidates:
		if (row or col not in getattr(cand, 'pos')) or square not in clogic.available_moves(cand, board, ch=True):
			candidates.remove(cand)
	#Should only have one candidate left at this point
	return clogic.move_piece(candidates[0], square, board)

# Open a saved game file and parse the moves one by one to calculate the final board state
def parse_game(game):
	gamefile = open(game, 'r')
	game_board = clogic.set_board('full_board.ini')
	colour = ['w', 'b']
	lines = gamefile.readlines()
	[clock_time_w, clock_time_b, counter] = lines[0].split(', ')
	clock_time = [float(clock_time_w), float(clock_time_b)]
	moves = lines[1].split(' ')
	for i in range(len(moves)):
		game_board = parse(game_board, moves[i], colour[i%2])
	return game_board, moves, clock_time, int(counter)

# Sort saved moves out so that they can be displayed in the moves box
def sort_moves(moves):
	numbers = white = black = ''
	if moves == []:
		return '', '', ''
	for i in np.arange(0, len(moves), 2):
		numbers += (str(i/2 +1)+'.'+'\n')
		white += moves[i] + '\n'
		try:
			black += moves[i+1] + '\n'
		except IndexError:
			black += ' '
			pass
	return numbers, white, black
