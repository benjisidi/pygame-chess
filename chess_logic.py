from piece import piece
import numpy as np
import operator

def classic_to_pix(pos):
	# Turns a positon in the format 'E4' into relevant pixel coordinates
	letters = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}
	x_pix = (letters[pos[0]]-1)*(100)
	y_pix = np.abs((int(pos[1]))-8)*(100)
	return [x_pix, y_pix]

def pix_to_classic(coords):
	# Identifies relevant square from pixel coordinates
	letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
	box = [x/100 for x in coords] # Integer division
	pos = letters[box[0]] + str(np.abs(box[1]-8))
	return pos

def classic_to_cart(pos):
	# Turns a position in the format 'E4' into the format [5, 4]; used for piece movement
	letters = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}
	x = letters[pos[0]]
	y = int(pos[1])
	return [x, y]

def cart_to_classic(coords):
	# Turns a move position (format [5, 4]) into 'pos' format ('E4')
	letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
	position = ''
	if coords[0]-1 >= 0:
		try: 
			position += letters[coords[0]-1]
		except IndexError:
			position += 'Z' # Assign anything off the right of the board as 'Z'
	else: position += 'Z' # Assign anything off the left of the board as 'Z'
	position += str(coords[1])
	return position

def set_board(ini):
	# Reads in ini in format <piece colour location,location,location,...>
	board = []
	setup = open(ini, 'r')
	lines = [x.split() for x in setup.readlines()]
	for line in lines:
		sqs = [x.upper() for x in line[2].split(',')]
		for sq in sqs:
			board.append(piece(line[0], line[1], sq))
	return board

def print_board(board):
	for x in board:
		piece.printpiece(x)

def sq_occupied(sq, board):
	occupied = [False, None]
	for piece_ in board:
		if getattr(piece_, 'pos') == sq:
			occupied = [True, piece_] 
	return occupied

def same_colour(piece1, piece2):
	return getattr(piece1, 'colour') == getattr(piece2, 'colour')

def threatened(sq, colour, board): # Checks if square owned by colour is threatened
	if colour == 'w': opp = 'b'
	else: opp = 'w'
	for piece_ in board:
		if getattr(piece_, 'colour') == opp:
			if sq in available_moves(piece_, board, threatcheck=True):
				return True, getattr(piece_, 'pos')
	return False, None

def in_check(colour, board):
	kings = [x for x in board if getattr(x, 'type_') == 'king' and getattr(x, 'colour') == colour] # Grab relevant king. Ya can't have more than 1. Yet.
	for x in kings:
		if threatened(getattr(x, 'pos'), colour, board)[0]:
			return True
	return False

def checkmate(colour, board):
	if in_check(colour, board):
		pieces = [x for x in board if getattr(x, 'colour') == colour]
		for piece_ in pieces:
			if available_moves(piece_, board, ch=True) != []:
				return False
		return True
	return False

def queen(params):
	# Kill pawn, replace with queen.
	pawn = params[0]
	piecetype = params[1]
	board = params[2]
	board.remove(pawn)
	sq = getattr(pawn, 'pos')
	colour = getattr(pawn, 'colour')
	board.append(piece(piecetype, colour, sq))
	return board

def can_castle(king, board):
	castlable_sqs = []
	# Checks if either piece has moved and for intervening board.
	colour = getattr(king, 'colour') # Setup; figure out which squares to check for rooks
	rows = {'w':1, 'b':8}
	row = str(rows[colour])
	rooks = []
	if in_check(getattr(king, 'colour'), board):
		return [False, []]
	if getattr(king, 'type_') != 'king': #Only kings can castle
		return [False, []]
	#if turn[counter%2] != getattr(king, 'colour'): # You can't castle if it isn't your go
	#	return False
	if getattr(king, 'moved'): # Bail if king has moved
		# print 'King has moved'
		return [False, []]
	for sq in ['A'+ row, 'H'+row]: # Check if rooks are on the appropriate squares
		if sq_occupied(sq, board)[0]:
			if getattr(sq_occupied(sq, board)[1], 'type_') == 'rook':
				rooks.append(sq_occupied(sq, board)[1])
	if rooks == []:
		# print 'No available rooks'
		return [False, []] # If no rooks, bail
	for rook in rooks:
		# print '\nChecking rook on ' + getattr(rook, 'pos') + '...'
		blocked = False
		side = ''
		if getattr(rook, 'moved'): # Rook moved, go on to next rook
			# print 'Rook has moved'
			continue 
		if getattr(rook, 'pos')[0] == 'A': # If rook hasn't moved, find if it is king or queenside
			side += 'queenside'	
			intervening = ['B', 'C', 'D']
		else:
			side += 'kingside'
			intervening = ['F', 'G'] 
		# print 'Rook is ' + side
		for col in intervening:				# Check if any intervening squares are occupied or threatened
			if sq_occupied(col + row, board)[0] or threatened(col+row, colour, board)[0]:
				blocked = True
				# print 'Rook on ' + getattr(rook, 'pos') + ' is blocked on sq ' + col + row
		if blocked == False: # If rook is in place, and king is not blocked, add the appropriate castling square.
			if side == 'queenside':
				castlable_sqs.append('C' + row)
			else:
				castlable_sqs.append('G' + row)
			# print 'Rook fine, can castle'
	if castlable_sqs == []:
		return [False, []]
	else:
		return [True, castlable_sqs]

# Create a hypothetical board where a given piece has moved to a given square, and taken if appropriate.
def ghost_board(piece_, sq, board):
	ghost_board = [x for x in board if x != piece_]
	for x in ghost_board:
		if getattr(x, 'pos') == sq:
			ghost_board.remove(x) #Taking
	ghost_piece = piece(getattr(piece_, 'type_'), getattr(piece_, 'colour'), sq)
	ghost_board.append(ghost_piece)
	return ghost_board

def available_moves(piece_, board=None, ch=False, threatcheck=False, previous_moves=[]):
	output = []

	# Deal with pawns:
	if getattr(piece_, 'type_')[:4] == 'pawn':
		direction = getattr(piece_, 'moves')[0]
		blocked = False
		for i in range(1, getattr(piece_, 'range')+1): # Go 1 or 2 forward
			if blocked: break # Stop iterating if we've hit a piece
			else:
				current_sq = getattr(piece_, 'pos')
				check_sq = cart_to_classic(map(operator.add, classic_to_cart(current_sq), map(operator.mul, direction, [i,i]))) # Move one further down that line 
				if check_sq[0] == 'Z' or 1 > int(check_sq[1:]) or int(check_sq[1:]) > 8 : # Stop if we hit the edge of the board
					blocked = True
					break
				elif sq_occupied(check_sq, board)[0]:
					blocked = True # Mark line blocked if square is occupied
					break
			output.append(check_sq)

		# Diagonal Taking
		for i in [[1,direction[1]], [-1,direction[1]]]: # Iterate over two diagonally forward squares
			check_sq = cart_to_classic(map(operator.add, classic_to_cart(current_sq), i))
			if sq_occupied(check_sq, board)[0] and not same_colour(sq_occupied(check_sq, board)[1], piece_): # If square occupied by enemy piece, tag it as allowed
				output.append(check_sq)

		#En Passant
		if not threatcheck: 
			enpassant = en_passant(piece_, previous_moves)
			if enpassant[0]:
				output.append(enpassant[1])

	# Things that aren't pawns		
	else: 
		for direction in getattr(piece_, 'moves'): # Iterate over directions piece can move in
			blocked = False
			for i in range(1, getattr(piece_, 'range')+1): # Iterate in that direction
				if blocked: break # Stop iterating if we've hit a piece
				else:
					current_sq = getattr(piece_, 'pos')
					check_sq = cart_to_classic(map(operator.add, classic_to_cart(current_sq), map(operator.mul, direction, [i,i]))) # Move one further down that line
					if check_sq[0] == 'Z' or 1 > int(check_sq[1:]) or int(check_sq[1:]) > 8 : # Stop if we hit the edge of the board
						blocked = True
						break
					elif sq_occupied(check_sq, board)[0]:
						blocked = True # Mark line blocked if square is occupied
						if same_colour(sq_occupied(check_sq, board)[1], piece_): # Highlights the square if it contains a enemy piece, 
							break												 # and doesn't if it contains a friendly.
					output.append(check_sq) # If path isn't blocked yet, highlight the square
		
		if getattr(piece_, 'type_') == 'king' and not threatcheck:
			castlable = can_castle(piece_, board)
			if castlable[0]:
				for x in castlable[1]:
					output.append(x)

	if board == None or ch == True: # Remove all squares that result in player being in check
		dummy_output = []
		for sq in output:
			newboard = ghost_board(piece_, sq, board) # Create a 'ghost board' layout with the piece moved to candidate square
			if not in_check(getattr(piece_, 'colour'), newboard): # If player is in check on ghost board, make candidate square unavailable
				dummy_output.append(sq)
		output = dummy_output
	return output


def move_piece(piece_, sq, board):
	occupied = sq_occupied(sq, board)

	# ---Pawns
	if getattr(piece_, 'type_')[:4] == 'pawn':
		setattr(piece_, 'range', 1) # Deal with pawns' first moves
		en_passant_move = getattr(piece_, 'pos')[0].upper() != sq[0]\
							and not occupied[0] 					# Move is diagonal and onto empty square
		if en_passant_move:
			if getattr(piece_, 'colour') == 'w':
				take_sq = sq[0] + str(int(sq[1])-1)
			else:
				take_sq = sq[0] + str(int(sq[1])+1) 
			taken_piece = sq_occupied(take_sq, board)[1]
			board.remove(taken_piece)

	# ---Castling
	castlable_sqs = can_castle(piece_, board)
	if getattr(piece_, 'type_') == 'king' and sq in castlable_sqs[1]: # Deal with castling
		if sq[0] == 'C': # If queenside:
			rook = sq_occupied('A' + sq[1], board)[1] # Grab the queenside rook
			setattr(rook, 'pos', 'D' + sq[1]) # Move it to correct square
		else:
			rook = sq_occupied('H' + sq[1], board)[1] # Same on kingside
			setattr(rook, 'pos', 'F' + sq[1])

	# ---Normal movement
	if occupied[0]: # Check if square occupied
		board.remove(occupied[1]) # Kill occupying piece
		setattr(piece_, 'pos', sq) # Move selected piece to sq
	else:
		setattr(piece_, 'pos', sq)
	setattr(piece_, 'moved', True)
	movedpiece = piece_
	return board

def record_move(piece_, sq, board, turn_colour, queening_piece=None):
	occupied = sq_occupied(sq, board)	
	move = ''
	move += getattr(piece_, 'prefix') # Add piece prefix
	same_type = [x for x in board if getattr(x, 'colour') == getattr(piece_, 'colour') and getattr(x, 'type_') == getattr(piece_, 'type_') and x != piece_]
	if same_type != []:
		for x in same_type: # Iterate over pieces of the same type and colour
			if sq in available_moves(x, board, ch=True): # Check if any can also move to the same square
				current_pos = getattr(piece_, 'pos') # The position of our current piece
				conflicting_pos = getattr(x, 'pos') # The position of our potentially conflicting piece
				same_col = current_pos[0] == conflicting_pos[0]	# Check if pieces in same column
				same_row = current_pos[1] == conflicting_pos[1]		# Check if pieces in same row
				if same_row and current_pos[0] not in move:			# Add column if necessary and not already done
					move += current_pos[0].lower()
				if same_col and current_pos[1] not in move:			# Add row if necessary and not already done
					move += current_pos[1]
	if occupied[0]:															# If we're taking:
		if getattr(piece_, 'type_') == 'pawn_b' or 'pawn_w' and move == '': 	# If it's a pawn and we haven't already specified row, add it
			move += getattr(piece_, 'pos')[0].lower()
		move += 'x' 															# Add an x
	move += sq.lower()												# Add the square
	if (getattr(piece_, 'type_') == 'pawn_b' and sq[1] == '1')\
		or (getattr(piece_, 'type_') == 'pawn_w' and sq[1] == '8'):	# Add queening notation if necessary
		move += '='
		if queening_piece != None:
			move+= queening_piece			
	newboard = ghost_board(piece_, sq, board) 						# Create a 'ghost board' layout with the piece moved to candidate square, to add '+' for check
	if in_check(turn_colour, newboard):
		if checkmate(turn_colour, newboard):
			move += '#' 				
		else:
			move += '+'
	if getattr(piece_, 'type_') == 'king':
		castlable_sqs = can_castle(piece_, board)[1]
		if sq in castlable_sqs:											# Replace with castling notation if necessary
			if sq[0] == 'G':
				move = 'O-O'
			else:
				move = 'O-O-O'
	return move

def en_passant(piece_, moves):
	if moves == []:
		return False, None
	colour = getattr(piece_, 'colour')
	current_pos = getattr(piece_, 'pos')
	if colour == 'w':
		jumprow = 5
		back = 1
	else:
		jumprow = 4
		back = -1
	if current_pos[1] != str(jumprow): #Check if pawn is in position for en passant taking
		return False, None
	previous_move = moves[-1]
	rows = 'abcdefgh'
	rowindex = rows.index(current_pos[0].lower())
	if rowindex == 0:
		adjacent_rows = 'b'
	elif rowindex == 8:
		adjacent_rows = 'g'
	else:
		adjacent_rows = rows[rowindex+1] + rows[rowindex-1]
	if len(previous_move) == 2: 	#Check if last move was a simple pawn move
		if previous_move[1] == str(jumprow) and previous_move[0] in adjacent_rows:	#Check if it was a 2-square pawn move on the right row
			col = previous_move[0]
			two_square = col + str(jumprow + back) not in moves #Check if 'e3' exists, if move were 'e4'
			if two_square:
				return True, (col + str(jumprow + back)).upper()
	return False, None
