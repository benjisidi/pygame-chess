import subprocess, time

def load(engine_file):
	engine = subprocess.Popen(
		engine_file,
		universal_newlines=True,
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
	)
	return engine

def put(engine, command):
	engine.stdin.write(command+'\n')

def get(engine, wait_for_bestmove=False):
	# using the 'isready' command (engine has to answer 'readyok')
	# to indicate current last line of stdout
	engine.stdin.write('isready\n')
	output = ['']
	while True:
		text = engine.stdout.readline().strip()
		if not wait_for_bestmove: 
			breakstring = 'readyok'
		else:
			breakstring = 'bestmove'
		if breakstring in text:
			if wait_for_bestmove:
				output.append(text)
			break
		else:
			output.append(text)
	return output[-1]

def play(engine, engine_board, wtime, btime):
	movestring = ' '.join(engine_board)
	put(engine, 'position startpos moves ' + movestring)
	get(engine)
	put(engine, 'go wtime {} btime {} depth 18'.format(wtime*1000, btime*1000))
	move = get(engine, wait_for_bestmove=True).split(' ')[1]
	piece_loc = move[0:2].upper()
	dest = move[2:].upper()
	return move, piece_loc, dest

if __name__ == '__main__':
	test = load('ai/cheese-19-linux/cheese-19-linux-32')
	put(test, 'uci')
	a = get(test)
	command = raw_input('Enter a command: ')
	while command != 'done':
		bestmove = 'y' in raw_input('Best move on next? (y/n)')
		put(test, command)
		a = get(test, wait_for_bestmove=bestmove)
		command = raw_input('\nEnter a command: ')
