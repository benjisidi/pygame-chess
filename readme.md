# Pygame Chess

This was my first large (multi-file) project, and also my first project using pygame. As a result, it isn't terribly well written: the main file (*chess.py*) makes heavy use of global variables, the implementation of the queening screen is messy and unintuitive, and the way games are saved and loaded is very inefficient. Rather than treating the board as an object and pickling it, or writing the game in PGN (portable game notation) so that other chess applications could read it, the move seqence is written to a file in the standard "newspaper" style (eg e4 e5 Nc3 Nf6), and then on loading the program must parse this move sequence and reconstruct the board accordingly, resulting in a noticable delay for even short games. On the plus side, this means that you can easily create a save file for any game you wish.

## Usage

* Download everything ("design" folder not necessary).

* If you are on linux, you can simply use the included stockfish engine. Otherwise, download your favourite UCI-compatible engine and place it in the ai folder. Then adjust lines 434-438 of chess.py accordingly (this should be very straightforward; simply replace the path to stockfish with your engine of choice). If you don't have a preffered engine, you can get stockfish for other operating systems [here](https://stockfishchess.org/download/ "Stockfish download page"). 

* Run chess.py. You can start a new game with any time control you wish (default is 25+0).
* To play, simply left click on the piece you would like to move. Left click to move the piece to a highlighted square. Left click on a different piece to select it, or right click to deselect the current piece.
* If you wish to manually write your own save file (to load up a well-known game, or one you've played over the board), they take the following format:
  * **Line 1**: `[Time left on white's clock in seconds], [Time left on black's clock in seconds],[Number of turns taken]`
  * **Line 2**: `Space-delimited list of moves played in algebraic notation (with no move numbers).`

## File Structure

| File/Folder            | Contents                                                     |
| ---------------------- | ------------------------------------------------------------ |
| ai/stockfish-8-linux/* | Completely unedited version of Stockfish 8 for Linux.        |
| assets/*.png           | Large versions of the piece image files                      |
| assets/small/*         | Small versions of the piece image files. Obsolete.           |
| assets/*.ttf           | Font files for rendering text                                |
| board.ini              | Default config of the initial board state. Currently a standard chessboard. |
| button.py              | Contains classes for creating buttons, text and textboxes in pygame |
| chess.py               | Contains functions for starting, ending, loading, saving and running the game, as well as those for rendering the game window. |
| chess_logic.py         | Contains all functions related to implementing the rules of chess |
| engine.py              | Contains functions for reading and sending information to the UCI engine. |
| full_board.ini         | A backup config file containing a standard chessboard in case you want to mess with the main one, for easily restoring the game to normal. |
| parse_moves.py         | Contains functions for reading save file data and creating the resulting board state. |
| piece.py               | Houses the piece class, which stores the piece type, its legal moves, image, colour and position. |
| test.ch                | A simple save file used to test the save/load funciton. Also a useful example if you want to manually write your own. |


## Future Improvements, Known bugs and limitations

##### Known Bugs

- None

##### Limitations

- Only possible to play as white
- No GUI button for switching from vs AI to local multiplayer 

##### Future Improvements

If I have time, I intend to overhaul the design of this projcect to clean up what is currently rather inelegant code. When this is done, it should be much more straightforward to address the limitations above.