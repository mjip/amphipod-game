import sys
import copy
import curses

COSTS = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}

class Game(object):
	def __init__(self, start_board):
		self.start_board = start_board
		self.board = copy.deepcopy(start_board)
		self.energy = 0

		self.display_height = 0
		self.display_width = 0

		self.selected_char = ''
		self.selected_x = -1
		self.selected_y = -1

	def reset(self):
		self.deselect()
		self.board = self.start_board
		self.energy = 0

	def _setup_ncurses(self, stdscr):
		curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

		curses.use_default_colors()
		curses.init_pair(1, curses.COLOR_RED, -1)

	def calculate_path(self, x, y):
		path = [self.board[y][x]]
		# in hallway, need to move across first
		if y == 1:
			dx = 1
			if self.selected_x < x:
				dx = -1
			while x != self.selected_x:
				x += dx
				path.append(self.board[y][x])
			while y != self.selected_y:
				y += 1
				path.append(self.board[y][x])
		else: # in a room, need to move up to hallway first
			while y != 1:
				y -= 1
				path.append(self.board[y][x])
			dx = 1
			if self.selected_x < x:
				dx = -1
			while x != self.selected_x:
				x += dx
				path.append(self.board[y][x])
			while y != self.selected_y:
				y += 1
				path.append(self.board[y][x])
		return path

	def calculate_energy(self, path):
		self.energy += (len(path)-1) * COSTS[path[-1]]

	def is_valid_path(self, path):
		valid = True
		for step in path[:-1]:
			if step != '.':
				valid = False
				break
		return valid

	def play(self, stdscr):
		self._setup_ncurses(stdscr)

		height, width = stdscr.getmaxyx()
		self.display_height = height // 2 - len(self.board) // 2
		self.display_width = width // 2 - len(self.board[0]) // 2
		self.display_board(stdscr)

		while True:
			event = stdscr.getch()
			if event == ord('q'):
				return
			elif event == ord('r'):
				self.reset()
				self.display_board(stdscr)
			elif event == curses.KEY_MOUSE:
				_, mx, my, _, _ = curses.getmouse()
				if self.display_height <= my < self.display_height+len(self.board) and self.display_width <= mx < self.display_width+len(self.board[0]):
					char = self.board[my-self.display_height][mx-self.display_width]
					if char.isalpha():
						if self.selected_char != char:
							self.selected_char = char
							self.selected_x = mx - self.display_width
							self.selected_y = my - self.display_height
							self.display_board(stdscr, selected=True, x=mx, y=my)
						else:
							self.deselect()
							self.display_board(stdscr)
					elif char == '.':
						if self.selected_char:
							path = self.calculate_path(mx-self.display_width, my-self.display_height)
							is_valid = self.is_valid_path(path)
							if is_valid:
								self.calculate_energy(path)
								self.board[self.selected_y][self.selected_x] = '.'
								self.board[my-self.display_height][mx-self.display_width] = self.selected_char
								self.deselect()
								self.display_board(stdscr)
							else:
								self.deselect()
								self.display_board(stdscr)
					else:
						self.deselect()

	def deselect(self):
		self.selected_char = ''
		self.selected_x = -1
		self.selected_y = -1

	def display_board(self, stdscr, selected=False, x=None, y=None):
		stdscr.clear()
		for i, row in enumerate(self.board):
				for c, col in enumerate(row):
					if selected and (x-self.display_width) == c and (y-self.display_height) == i:
						stdscr.addstr(self.display_height+i,self.display_width+c,col, curses.color_pair(1) | curses.A_BOLD)
					else:
						stdscr.addstr(self.display_height+i,self.display_width+c,col)
				stdscr.addstr(self.display_height+i,self.display_width+1+c,'\n')

		energy_line_height = self.display_height + len(self.board) + 1
		stdscr.addstr(energy_line_height, self.display_width+1, f"Energy: {self.energy}")
		stdscr.addstr(energy_line_height + 2,self.display_width-6, "Press q to quit, r to reset")
		stdscr.refresh()

def main():
	board_path = input("Enter your start board filepath: ")
	board_state = []
	with open(board_path) as f:
		board_state = [list(l.rstrip('\n')) for l in f.readlines()]
	game = Game(board_state)

	curses.wrapper(game.play)
