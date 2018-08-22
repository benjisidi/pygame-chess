import pygame
import numpy as np
import operator
import time
import os
from button import button, txt, txtbox
from piece import piece
from chess_logic import *
from parse_moves import *
import wx
import engine
import multiprocessing

'''
TUTORIAL: http://programarcadegames.com/index.php?lang=en&chapter=controllers_and_graphics

ToDo:
	-Quit 'are you sure' dialog
	-Display taken board --> Under clock?
	-Toggle AI or human vs human game
	-Option to play as black vs AI, option to flip board

Done:
	-Re-do piece assets with fill
	-Write draw_piece function
	-Move board with mouse and 'Snap' to location 
	-Display available squares on click
	-Game logic:
		-Basic Movement - 
		-Basic Taking - 
		-Turns - 
		-Check/Checkmate
		-Allow taking of checking piece
		-Pawn starting move - 
		-Pawns taking diagonally -
		-Pawn queening - 
		-En passant
		-Castling
			-Castlable sqs var - 
			-Castle fn - Incorperated into move_piece - 
			-can_castle sets castlable sqs, and checks both rooks w/o being passed them - 
			-move_piece calls castle fn - Schmushed the two into one fn, 
			-Can't castle through check
		-Checkmate
	-Turn clock
	-Write new, load, save functions
	-Add sidebar with game history (+ button to save game to txt file)
	-Buttons to scroll through game, load game from txt
	-Game setup dialog
	-Load & save game dialogs
	-Implement AI --> Glaurung is UCI compatible and a good level --> UCI python module
'''

# FILL COLOUR: R: 229 G: 226 B: 221

# Draws chequerboard in given colours ([r,g,b] format), with each square having sidelength box_side
def draw_board(colour_white, colour_black):
	for j in range(0, 8):
		coords = (0, j*box_side, box_side, box_side) # box_side is global and set in run_game function
		for i in range(0, 8):
			if (i+j) % 2 == 0: colour = colour_white
			else: colour = colour_black
			pygame.draw.rect(screen, colour, coords)
			coords = tuple(map(operator.add, coords, (box_side, 0, 0, 0)))

# Takes a seconds value and returns a string in the format 'mm:ss'
def secs_to_readable(secs):
	mins = secs/60.
	minute = np.floor(mins)
	secs = (mins - minute)*60
	if minute == 0 and secs < 10:
		return '{:.2f}'.format(secs)
	else:
		minute = int(minute)
		secs = int(secs)
		return '{0:02d}'.format(minute) + ':' + '{0:02d}'.format(secs)

# Creates the buttons and textboxes in the sidebar, along with the clock
def initialize_sidebar():
	global buttons
	global clock_time
	global moves
	# button function unnamed arguments: (surface, x, y, width, height, shape...)
	new = button(screen, 829, 27, 100, 44, 'rrect', colour = [229, 226, 221], hover_colours = [[129, 126, 121],[50,50,50],[200,200,200],[255, 255, 255]], function = new_game, text='NEW', font=['assets/Lato-Bold.ttf', 32, 'file', [64, 64, 64]])
	save = button(screen, 939, 27, 100, 44, 'rrect', colour = [229, 226, 221], hover_colours = [[129, 126, 121],[50,50,50],[200,200,200],[255,255,255]], function = save_game, text='SAVE', font=['assets/Lato-Bold.ttf', 32, 'file', [64, 64, 64]])
	load = button(screen, 1049, 27, 100, 44, 'rrect', colour = [229, 226, 221], hover_colours = [[129, 126, 121],[50,50,50],[200,200,200],[255,255,255]], function = load_game, text='LOAD', font=['assets/Lato-Bold.ttf', 32, 'file', [64, 64, 64]])
	quit = button(screen, 1159, 27, 100, 44, 'rrect', colour = [229, 226, 221], hover_colours = [[129, 126, 121],[50,50,50],[200,200,200],[255,255,255]], function = quit_game, text='QUIT', font=['assets/Lato-Bold.ttf', 32, 'file', [64, 64, 64]])
	# moves_box is a button with no associated function; simply a convenient way to draw the rounded rectangle to hold the text boxes
	moves_box = button(screen, 829, 101, 250, 335, 'rrect', colour = [50,50,50], rectrad=.05)
	# moves_box contains 3 columns; the move number, white's move and black's move
	moves_numbers = txtbox(screen, 840, 110, 25, 17, '', font=['assets/Lato-Regular.ttf', 18, 'file', [229, 226, 221], False, False])
	moves_white = txtbox(screen, 880, 110, 75, 17, '', font=['assets/Lato-Regular.ttf', 18, 'file', [229, 226, 221], False, False])
	moves_black = txtbox(screen, 980, 110, 75, 17, '', font=['assets/Lato-Regular.ttf', 18, 'file', [229, 226, 221], False, False])
	# buttons to scroll the moves box up and down
	scup = button(screen, 1095, 110, 23, 29, 'uarrow', colour = [229, 226, 221], function = scroll_moves_up, holdable=True)
	scdown = button(screen, 1095, 162, 23, 29, 'darrow', colour = [229, 226, 221], function = scroll_moves_down, holdable=True)
	clock_black = button(screen, 829, 465, 428, 123, 'rrect', colour = [50, 50, 50], text=secs_to_readable(clock_time[1]), font=['assets/Lato-Bold.ttf', 92, 'file', [229, 226, 221]])
	clock_white = button(screen, 829, 588, 428, 123, 'rrect', colour = [229, 226, 221], text=secs_to_readable(clock_time[0]), font=['assets/Lato-Bold.ttf', 92, 'file', [50, 50, 50]])
	# Convenient way to fill buttons dictionary
	buttons_list = [new, save, load, quit, moves_box, moves_numbers, moves_white, moves_black, scup, scdown, clock_black, clock_white]
	buttons_names = ['new', 'save', 'load', 'quit', 'moves_box', 'moves_numbers', 'moves_white', 'moves_black', 'scup', 'scdown', 'clock_black', 'clock_white']
	for i in range(len(buttons_names)):
		buttons[buttons_names[i]] = buttons_list[i]

def draw_sidebar():
	global buttons
	global moves
	buttons_names = ['new', 'save', 'load', 'quit', 'moves_box', 'moves_numbers', 'moves_white', 'moves_black', 'scup', 'scdown', 'clock_black', 'clock_white']
	pygame.draw.rect(screen, [64, 64, 64], (806, 0, 474, 800)) # BG fill
	pygame.draw.rect(screen, [94, 94, 94], (800, 0, 6, 800)) # Separator
	pygame.draw.rect(screen, [50, 50, 50], (829, 565, 428, 23)) # Clock fill
	pygame.draw.rect(screen, [229, 226, 221], (829, 588, 428, 23)) # Clock fill
	numbers, white, black = sort_moves(moves)
	# Update the clock and move box text
	setattr(buttons['clock_black'], 'text', secs_to_readable(clock_time[1]))
	setattr(buttons['clock_white'], 'text', secs_to_readable(clock_time[0]))
	setattr(buttons['moves_numbers'], 'body', numbers)
	setattr(buttons['moves_white'], 'body', white)
	setattr(buttons['moves_black'], 'body', black)
	# Draw all the elements
	for i in range(len(buttons_names)):
		buttons[buttons_names[i]].draw()

# Draw an image at x, y and call an associated action if it is clicked. Used for queening screen.
def draw_im_button(img, x, y, action=None, param=None, size=100):
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()
	image  = pygame.image.load(img).convert_alpha()
	image = pygame.transform.scale(image, (size, size))
	img_size = image.get_rect().size
	screen.blit(image, [x, y])
	if (x < mouse[0] < (x + img_size[0])) and (y < mouse[1] < (y + img_size[1])) and (click == (1, 0, 0)) and (action != None):
		action(param)

# Render text in font and colour at x, y
def draw_text(text, font, colour, x, y):
	text = font.render(text, True, colour)
	screen.blit(text, (x, y))

# Create new game dialog and reset board with new time control
def new_game():
	global clock_time
	global counter
	global live_board
	global queening
	global moves
	global buttons
	global increment
	global engine_moves
	# Create time control dialog
	temp_app = wx.App(False)
	settings = wx.TextEntryDialog(None, 'Set time control [minutes(25)+increment(0)]')
	# On 'ok', parse input and apply default values if necessary
	if settings.ShowModal() == wx.ID_OK:
		time_control = settings.GetValue().split('+')
		try: 
			initial_time = float(time_control[0])*60
		except ValueError: 
			initial_time = 25*60
		try:
			increment = float(time_control[1])
		except ValueError:
			increment = 0
		except IndexError:
			increment = 0
		settings.Destroy()
		# Reset board, turn counter and time
		for x in live_board:
			deselect(x)
		moves = []
		engine_moves = []
		queening = [False, None]
		live_board = set_board('board.ini')
		clock_time = [initial_time, initial_time]
		setattr(buttons['clock_black'], 'neutral_text_colour', [229, 226, 221])
		setattr(buttons['clock_white'], 'neutral_text_colour', [50, 50, 50])
		counter = 0

# Create save game dialog, and write clock times and game moves to file
def save_game():
	file_path = None
	# Concatenate moves into single space delimited string
	gametxt = ' '.join(move for move in moves)
	# Create save file dialog
	temp_app = wx.App(False)
	save_dialog = wx.FileDialog(
		None, message='Save game as...',
		defaultDir=os.getcwd(),
		defaultFile='',
		wildcard='Saved Chess Games (*ch)|*.ch',
		style=wx.FD_SAVE
		)
	if save_dialog.ShowModal() == wx.ID_OK:
		file_path = [x for x in save_dialog.GetPaths()]
	temp_app.MainLoop()
	# If a file has been entered/selected, write save information to the file and close it
	if file_path != None:
		file_path[0] += '.ch'
		savefile = open(file_path[0], 'w')
		savefile.write('{}, {}, {}'.format(clock_time[0], clock_time[1], counter))
		savefile.write('\n')
		savefile.write(gametxt)
		savefile.close()

# Create load save-file dialog and parse the file to reconstruct the game board state 
def load_game():
	global live_board
	global moves
	global clock_time
	global counter
	global buttons
	# Create file dialog
	chosen_file = None
	temp_app = wx.App(False)
	load_dialog = wx.FileDialog(
		None, message='Select game file',
		defaultDir=os.getcwd(), 
		defaultFile="",
		wildcard="Saved Chess Games (*.ch)|*.ch|" \
				"All files (*.*)|*.*",
		style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
	if load_dialog.ShowModal() == wx.ID_OK:
			paths = load_dialog.GetPaths()
			chosen_file = [x for x in paths]
	temp_app.MainLoop()
	# If file chosen, call parsing logic on saved file
	if chosen_file != None:
		live_board, moves, clock_time, counter = parse_game(chosen_file[0])

# When quit button clicked, stop engine and set "done" flag to true, closing window
def quit_game():
	global done
	# ToDo: are you sure you want to quit?
	engine.put(AI, 'quit')
	done = True

# Scroll all three columns in the moves box together
def scroll_moves_up():
	global buttons
	for i in ['moves_white', 'moves_black', 'moves_numbers']:
		buttons[i].scroll_up()

# Scroll all three columns in the moves box together
def scroll_moves_down():
	global buttons
	for i in ['moves_white', 'moves_black', 'moves_numbers']:
		buttons[i].scroll_down()


# At checkmate, set move clock to red
def end_game():
	global buttons
	fullcolour = {'b':'black', 'w':'white'}
	setattr(buttons['clock_' + fullcolour[turn_colour[(counter)%2]]], 'neutral_text_colour', [198, 0, 0])


# Draw rectangle in highlight_colour around the given sq. Takes classic coords.
def highlight(sq, highlight_colour=[249, 255, 183]): 
	rect = classic_to_pix(sq)
	rect += [box_side, box_side]
	pygame.draw.rect(screen, highlight_colour, rect, 3)


# Highlight squares that selected piece can move to
def draw_moves(piece_):
	global allowed_sqs
	global moves
	available = available_moves(piece_, board=live_board, ch=True, previous_moves=moves)
	for x in available:
		allowed_sqs.append(x)

# Set a piece to "selected" and highlight its available moves
def select(piece_):
	setattr(piece_, 'selected', True),
	draw_moves(piece_)

# Deselct piece and remove square highlighting
def deselect(piece_):
	global allowed_sqs
	global castlable_sqs
	setattr(piece_, 'selected', False) # Deselect piece
	allowed_sqs = [] # De-highlight squares

# Draw piece sprite on its occupied square
def draw_piece(piece_):
	coords = classic_to_pix(getattr(piece_, 'pos'))
	screen.blit(getattr(piece_, 'image'), coords)

# Apply moving a piece to a square
def turn(piece_, sq):
	global live_board
	global counter
	global queening
	global check
	global moves
	global buttons
	global engine_moves
	global engine
	global AI_plays

	# ---Record move before moving piece. 
	moves.append(record_move(piece_, sq, live_board, turn_colour[(counter+1)%2]))
	initial_sq = getattr(piece_, 'pos').lower()
	engine_moves.append(initial_sq+sq.lower())
	#print record_move(piece_, sq, live_board)

	# ---Update live_board as new board state
	live_board = move_piece(piece_, sq, live_board)

	# ---Deal with queening
	if 'pawn' in getattr(piece_, 'type_'):
		if (getattr(piece_, 'colour') == 'b' and sq[1] == '1') or (getattr(piece_, 'colour') == 'w' and sq[1] == '8'):
			queening = [True, piece_]
	if counter != 0: clock_time[counter%2] += increment
	# ---Deselect piece and advance turn
	deselect(piece_)
	counter += 1
	if checkmate(turn_colour[counter%2], live_board):
		end_game()
	for key in ['moves_white', 'moves_black', 'moves_numbers']:
		setattr(buttons[key], 'autoscroll', True)
	AI_plays = True

# Manage the engine taking a turn; create a separate process so the window does not hang while the
# engine is "thinking"
def turn_engine():
	global AI_plays
	global clock
	global clock_time
	# Create process to communicate with engine
	def AI_worker(AI, engine_moves, return_dict):
		global clock_time
		move, loc, dest = engine.play(AI, engine_moves, clock_time[0], clock_time[1])
		return_dict['move'] = move
		return_dict['loc'] = loc
		return_dict['dest'] = dest
	manager =  multiprocessing.Manager()
	return_dict = manager.dict()
	p = multiprocessing.Process(target=AI_worker, args=(AI, engine_moves, return_dict))
	p.start()
	# Continuously check if engine is complete and update the clock in the meantime
	engine_completed = False
	while not engine_completed:
		try:
			move = return_dict['move']
			loc = return_dict['loc']
			dest = return_dict['dest']
			engine_completed = True
		except KeyError:
			frametime = clock.get_time()
			clock_time[counter%2] -= frametime * 0.001
			draw_sidebar()
			pygame.display.flip()
			clock.tick(30)
	# Once the engine has returned a move, play it
	loc = loc.upper()
	dest = dest.upper()
	engine_piece = [x for x in live_board if getattr(x, 'pos') == loc][0]
	turn(engine_piece, dest)
	AI_plays = False

# Update the board with queened piece
def queen_piece(params):
	global live_board
	global queening
	live_board = queen(params) # Queen fn in chess_logic - destroy pawn and replace with piece
	moves[counter-1] += piece.printing_dict[params[1]]
	queening = [False, None]


def run_game():
	# Define colours for convenience
	BLACK = [0, 0, 0]
	WHITE = [255, 255, 255]
	COLOUR_WHITE = [200, 200, 200]
	COLOUR_BlACK = [50, 50, 50]

	# Manage framerate
	global clock
	clock = pygame.time.Clock()

	# initialize screen
	size = [1280, 800]
	global screen
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption('Chess v0.5 ')
	font = pygame.font.SysFont('default', 22)

	
	# Track allowed and castlable squares, and check
	global allowed_sqs
	global check
	allowed_sqs = []
	check = False

	# Track moves made
	global moves
	moves = []
	global engine_moves
	engine_moves = []
	# Get width and height of window, compute box dimensions
	w, h = pygame.display.get_surface().get_size()
	play_area = min([w, h])
	global box_side
	box_side = play_area/8

	# Create global live_board variable populate it from ini file
	global live_board
	live_board = set_board('board.ini')

	# Set up sidebar buttons
	global buttons
	buttons = {}
	global initial_time
	initial_time = 25*60
	global increment
	increment = 0
	global clock_time
	clock_time = [initial_time, initial_time]
	initialize_sidebar()

	# Set starting turn to white
	global turn_colour
	global counter
	turn_colour = ['w', 'b']
	counter = 0

	# Queening screen check
	global queening 
	queening = [False, None]

	# Set up engine
	global AI
	AI = engine.load('ai/stockfish-8-linux/Linux/stockfish_8_x64')
	engine.put(AI, 'uci')
	engine.put(AI, 'uci setoption name Skill Level value 0')
	engine.put(AI, 'ucinewgame')
	garbage = engine.get(AI)
	print 'AI started.'

	global AI_plays
	AI_plays = False

	# Loop until user closes
	global done
	done = False
	#  ------- Main Program Loop ------
	while not done:

		#  --- Main event loop
		for event in pygame.event.get():
			m_pos = pygame.mouse.get_pos()
			if event.type == pygame.QUIT:
				quit_game()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if (829 < m_pos[0] < (829+250)) and (101 < m_pos[1] < (101+335)): 
					if event.button == 4:
						scroll_moves_up()
					elif event.button == 5:
						scroll_moves_down()
				if 0 < m_pos[0] < 800: # If mouse is over board, do chess logic
					m_sq = pix_to_classic(m_pos)
					if pygame.mouse.get_pressed() == (0, 0, 1):
						for piece_ in live_board:
							deselect(piece_) # Right click delesects all board
					elif pygame.mouse.get_pressed() == (1, 0, 0): # Left click
						for piece_ in live_board:
							if getattr(piece_, 'selected') == True:
								if m_sq in allowed_sqs:
									#test_board = set_board('board.ini')
									turn(piece_, m_sq)
									#print parse(test_board, moves[counter-1], turn_colour[(counter-1)%2])	
							elif getattr(piece_, 'pos') == m_sq and turn_colour[counter%2] == getattr(piece_, 'colour'):
								for all_piece in live_board: # If there's a piece on the square we clicked, and that piece is of the right colour:.
									deselect(all_piece) # Deselect all board, then:
								select(piece_)  		# Select the piece
			# Quit on 'q'
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					quit_game()

		#  --- Drawing code ---

		# Display moves to the right of the board

		screen.fill([255, 255, 255])

		if queening[0]:
			# Fill with grey
			pygame.draw.rect(screen, [100, 100, 100], (0, 0, 800, 800))
			# Draw queening options
			textfont = pygame.font.Font('assets/Lato-Bold.ttf', 72) 
			draw_text('Choose your piece', textfont, [0, 0, 0], 75, 100)
			available_piecetypes = ['queen', 'knight', 'bishop', 'rook']
			for i in range(0, len(available_piecetypes)):
				try:
					draw_im_button('assets/'+ available_piecetypes[i] + '_' + getattr(queening[1], 'colour') + '.png'\
									, 50 + i*200, 200, queen_piece, [queening[1], available_piecetypes[i], live_board])
				except AttributeError:
					continue

		else:
			# Draw board and pieces
			draw_board(COLOUR_WHITE, COLOUR_BlACK)
			for piece_ in live_board:
				draw_piece(piece_)
			for sq in allowed_sqs:
				highlight(sq)
			check = in_check(turn_colour[counter%2], live_board)
			if check:
				king = [x for x in live_board if getattr(x, 'colour') == turn_colour[counter%2] and getattr(x, 'type_') == 'king']
				highlight(getattr(king[0], 'pos'), [254, 86, 160])
	
		draw_sidebar()


		pygame.display.flip()



		# Limit fps
		clock.tick(60)

		# Update clock
		if not queening[0] and not checkmate(turn_colour[counter%2], live_board):
			frametime = clock.get_time()
			if counter > 0:
				clock_time[counter%2] -= frametime * 0.001

		if AI_plays:
			turn_engine()

	# Exit gracefully
	pygame.quit()

if __name__ == '__main__':
	pygame.init()
	run_game()