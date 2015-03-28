import pygame
from pygame.locals import *
try:
    import android
    android.init()
except ImportError:
    android = None

pygame.display.init()

global xsize    # Screen Size
global ysize    # Screen Size
global screen   # The screen itself
global mouse    # Mous controls on or off used in pc version
global fullscreen   # Fullscreen on or off used in pc version
global exit_menu_on  # Exit menu on or off used in pc version
global boss_defeated # Used in Android version to stop music after a boss has been Vanquished
global mouse_position # Used for investigating npc's and story objects
width = pygame.display.Info().current_w
height = pygame.display.Info().current_h
if android:
    # Setting screen size on android
    dpi = android.get_dpi()
    if 450 > dpi > 260:
        ysize = 2*height/3
        xsize = 2*width/3
    elif 500 > dpi > 450:
        xsize = 9*width/20
        ysize = 9*height/20
    elif dpi > 500:
        xsize = 3*width/9
        ysize = 3*height/9
    elif height < 360:
        ysize = 360
        xsize = ysize*width/360
    elif 660 > height > 360:
        ysize = height
        xsize = width
    else:
        ysize = 660
        xsize = 660*width/height
    print dpi
    print xsize
    print ysize
else:
    ysize = 500
    xsize = ysize*width/height

screen = pygame.display.set_mode((xsize, ysize))
mouse = True
fullscreen = False
exit_menu_on = False
boss_defeated = False
mouse_position = None
