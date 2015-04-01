# Copyright 2015, Brendan Bulfin
import pygame
import os
import globals as g
from constants import *
from controls import control_events
from inventory import Inventory, Inventory_Menu
from maps import World_map
from objects import Interactable_Objects, Player
from menus import Intro_Menu, Exit_Menu

try:
    import android
    android.init()
except ImportError:
    android = None


try:
    import pygame.mixer as mixer
except ImportError:
    import mixer

pygame.init()
pygame.display.set_caption('First Reality')
if android:
    android.init()
    android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
    android.map_key(android.KEYCODE_MENU, pygame.K_z)
    pygame.mouse.set_visible(0)

myplayer = Player()
world = World_map()
myinventory = Inventory()
inter_objects = Interactable_Objects()
inventory_menu = Inventory_Menu(GREEN, myinventory)
intro_menu = Intro_Menu(BLACK)
exit_menu = Exit_Menu(BLACK)
intro_menu.update(myinventory, world, myplayer)
next_update_time = 0


while True:
    """ This is the main game loop. There are sub game loops like the inventory menu"""
    time = pygame.time.get_ticks()
    if next_update_time < time:
        if android:
            if android.check_pause():
                mixer.music.pause()
                android.wait_for_resume()
                mixer.music.unpause()
#            elif mixer.music.get_busy() == False and g.boss_defeated == False and world.name != 'Tower0':
#                mixer.music.play(-1)
        next_update_time = time + 30
        control_events(myplayer, world, inter_objects.objects)
        world.change_rooms(myplayer, time, g.ysize, g.xsize)
        myplayer.update(world, inter_objects.objects, time)
        inter_objects.update(world, myplayer, time)
        inventory_menu.update(myplayer, myinventory, world)
        intro_menu.game_over(myinventory, world, myplayer, inter_objects)
        exit_menu.update()
        g.screen.fill((0, 0, 0))
        g.screen.blit(
            world.image, (0, 0),
            (-world.rect.left, -world.rect.top, g.xsize, g.ysize))
        for a in inter_objects.objects:
            g.screen.blit(a.image, a.rect)
        g.screen.blit(myplayer.image, myplayer.rect)
        inter_objects.interact_objects(myplayer, world, myinventory, time)
        pygame.display.flip()
        time2 = pygame.time.get_ticks()
    pygame.time.wait(4)  # Used to limit cpu usage
