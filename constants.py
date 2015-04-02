import os.path
""" This file contains constants used in the code"""
d, u, r, l = 1, 2, 3, 4  # used for going up down left and right
up_down = [u ,d]
left_right = [l, r]
direction = {'down': 1, 'up': 2, 'right': 3, 'left': 4, 'noreturn': 5}
fonts = [os.path.join('data', 'Fonts', 'OpenSans.ttf'), os.path.join('data','Fonts', 'ampersand.ttf'),
         os.path.join('data','Fonts','Devroye.ttf'), os.path.join('data','Fonts', 'hand_writing.ttf')]

# SCREEN SETTINGS

GREEN = (30, 150, 30)
DARKGREEN = (10, 60, 10)
GREY = (70, 70, 70)
BLUE = (30, 30, 100)
RED = (160, 50, 20)
BLACK = (0, 0, 0)
DARKGREY = (25, 25, 25)
