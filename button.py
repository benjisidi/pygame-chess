import pygame
import numpy as np

# Object allowing text to be drawn in desired font, colour and size
class txt():

	def __init__(self, string, font, size, type_='sys', colour=[255,255,255], bold=False, italic=False):
		self.string = string
		self.colour = colour
		self.size = size
		# Load file or system font as appropriate
		if font.lower() == 'default':
			font = pygame.font.get_default_font()
		if type_.lower() == 'file':
			self.font = pygame.font.Font(font, size)
		elif type_.lower() == 'sys':
			self.font = pygame.font.SysFont(font, size, bold, italic)
		self.dims = pygame.font.Font.size(self.font, self.string)

	# Draw at x, y coordinates on given surface
	def draw(self, surface, x, y):
		string = self.string
		label = self.font.render(string, True, self.colour)
		surface.blit(label, (x, y))

# Scrollable text box with wrap
class txtbox():
	def __init__(self, surface, x, y, width, height, body, font=['default', 12, 'sys', [255, 255, 255], False, False], autoscroll=True):
		self.x = x
		self.y = y
		self.width = width # in px
		self.height = height # in lines
		self.body = body
		self.font_params = font
		self.surface = surface
		self.topline = 0
		self.autoscroll = autoscroll

		# Load file or system font as appropriate		
		if font[0].lower() == 'default':
			default_font = pygame.font.get_default_font()
			self.font = pygame.font.SysFont(default_font, font[1], font[4], font[5])
		elif font[2].lower() == 'file':
			self.font = pygame.font.Font(font[0], font[1])
		elif font[2].lower() == 'sys':
			self.font = pygame.font.SysFont(font[0], font[1], font[4], font[5])

	def draw(self):
		# Create duplicate of body as list so it can be truncated to visible part of text
		words = [line.split(' ') for line in self.body.splitlines()]
		space = self.font.size(' ')[0]
		word_x, word_y = self.x, self.y
		# If box is auto-scrolling, check if the top visible line is above the top of the box and scroll the text if necessary
		if self.autoscroll:
			while len(words) - self.topline > self.height:
				self.topline += 1
			# Truncate visible words to those that will fit in textbox
			if len(words) > self.height:
				words = words[self.topline:self.topline + self.height]
		else:
			words = words[self.topline:self.topline + self.height]
	#	while len(words) > self.height:
	#		words[len(words)-1:len(words)] = []
		# Draw visible words
		for line in words:
			for word in line:
				word_surface = self.font.render(word, 1, self.font_params[3])
				word_width, word_height = word_surface.get_size()
				if word_x + word_width >= self.x + self.width:
					word_x = self.x
					word_y += word_height
				self.surface.blit(word_surface, (word_x, word_y)) 
				word_x += word_width + space
			word_x = self.x
			word_y += word_height

	def scroll_up(self):
		self.autoscroll = False
		if self.topline > 0:
			self.topline -= 1

	def scroll_down(self):
		self.autoscroll = False
		if self.topline < len(self.body.splitlines()) - self.height:
			self.topline += 1

# Flexible button object with settable shape, text, colours and function. Can be one-press or holdable
class button():

	def __init__(self, surface, x, y, width, height, shape, colour = [255, 255,255], hover_colours = [[0,0,0],[0,0,0],[255,255,255],[200, 200, 200]], function = None,\
				param=None, text=None, font=['default', 12, 'sys', [0, 0, 0]], rectrad=.2, holdable=False):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.function = function
		self.shape = shape
		self.colour = colour
		self.hover_colour = hover_colours[0]
		self.click_colour = hover_colours[1]
		self.current_colour = colour
		self.hover_text_colour = hover_colours[2]
		self.click_text_colour = hover_colours[3]
		self.neutral_text_colour = font[3]
		self.surface = surface
		self.param = param
		self.text = text
		self.font = font
		self.rectrad = rectrad
		self.clicked_counter = 0
		self.holdable = holdable

	def update_text(self, string):
		self.text = string

	def draw(self):
		# Initialize params
		width = self.width
		height = self.height
		x = self.x
		y = self.y
		if width >= height:
			radius = int(height * self.rectrad)
		else:
			radius = int(width * self.rectrad)
		function = self.function
		param = self.param
		surface = self.surface

		mouse = pygame.mouse.get_pos()
		click = pygame.mouse.get_pressed()

		
		# On click
		if (x < mouse[0] < (x + width)) and (y < mouse[1] < (y + height)) and (click == (1, 0, 0)) and (function != None) or self.clicked_counter != 0: 
			self.current_colour = self.click_colour
			self.font[3] = self.hover_text_colour
			# Repeat function if button is meant to be holdable, otherwise execute it once then stop
			self.clicked_counter += 1
			if self.clicked_counter > 1 and self.holdable:
				self.clicked_counter = 0
			elif self.clicked_counter > 1 and click != (1, 0, 0):
				self.clicked_counter = 0
			if param != None and self.clicked_counter == 0:
				function(param)
			elif self.clicked_counter == 0:
				function()

		# Else, on hover
		elif (x < mouse[0] < (x + width)) and (y < mouse[1] < (y + height)) and (function != None):
			self.current_colour = self.hover_colour # Hover
			self.font[3] = self.click_text_colour

		# Else, neutral behaviour
		else:
			self.current_colour = self.colour
			self.font[3] = self.neutral_text_colour

		colour = self.current_colour

		# Use black as the colour key, unless button is black, in which case use minimum gray
		if colour[0] + colour[1] + colour[2] == 0:
			colourkey = (1,1,1)
		else:
			colourkey = (0,0,0)

		# Rounded Rectangle shape
		if self.shape == 'rrect':
			surf_temp = pygame.Surface((width,height))
			surf_temp.fill(colourkey)

			pygame.draw.rect(surf_temp,colour,(0,radius,width,height-2*radius),0)
			pygame.draw.rect(surf_temp,colour,(radius,0,width-2*radius,height),0)

			for point in [
				[radius,radius],
				[width-radius,radius],
				[radius,height-radius],
				[width-radius,height-radius]
			]:
				pygame.draw.circle(surf_temp,colour,point,radius,0)
			
		# Up arrow
		if self.shape == 'uarrow':
			height = int(self.width * 4/3.)
			surf_temp = pygame.Surface((width,height))
			surf_temp.fill(colourkey)
			pygame.draw.polygon(surf_temp, colour, [(0, height), (width/2, 0), (width/2, int(height*(5/8.)))])
			pygame.draw.polygon(surf_temp, colour, [(width/2, 0), (width, height), (width/2, int(height*(5/8.)))])

		# Down arrow; just draws up one then flips
		if self.shape == 'darrow':
			height = int(self.width * 4/3.)
			surf_temp = pygame.Surface((width,height))
			surf_temp.fill(colourkey)
			pygame.draw.polygon(surf_temp, colour, [(0, height), (width/2, 0), (width/2, int(height*(5/8.)))])
			pygame.draw.polygon(surf_temp, colour, [(width/2, 0), (width, height), (width/2, int(height*(5/8.)))])
			surf_temp = pygame.transform.flip(surf_temp, False, True)

		# Draw shape to surface
		surf_temp.set_colorkey(colourkey)
		surface.blit(surf_temp,(x, y))

		# Draw text if required
		if self.text != None:
			text = self.text
			font = self.font
			try: 
				bold = font[4]
			except IndexError: 
				bold = False
			try:
				italic = font[5]
			except IndexError: 
				italic = False
			label = txt(text, font[0], font[1], font[2], font[3], bold, italic)
			size = label.dims
			xpos = self.x + (self.width - size[0])/2
			ypos = self.y + (self.height - size[1])/2
			if  'avenir' in font[0]:
				ypos += font[1]*.14
			label.draw(surface, xpos, ypos)