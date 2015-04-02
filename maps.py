import pygame
import globals as g
from parse import load_jpg, load_doors, load_area, play_music
from controls import player_face_door, fade_black, fade_out
import os
from collisions import collision_door
from constants import u, d, l, r

""" The world is broken up into areas. Areas are place into  the areas folders
Each area has a folder and a text file. The text file sets the starting position and room
In the area folder images for each room, text maps and door files can be fond. These are all used
to load up rooms when they are entered. All areas are collected together into the world map.
Area names need to be added to the file areas.txt. The first name in this file is the starting area
"""


class Area_map(pygame.sprite.Sprite):

    """This class is used for each area and basically controlls navigation between rooms
    Collisions with maps, loading up the maps and there grids etc. It is inherited and used
    in the worldmap class and used for the current area."""

    def __init__(self, name):
        self.name = name  # The name of the area which is blitted in the map.
        self.menu_name = None  # This is used for the name that is displayed in the menu
        self.area_num = 0   # The number not. Not currently used
        self.current_room = 0  # The current room
        self.doors = []  # A list of the doors in the room, loaded fromm room.doors
        # [room door leads to, xpos, ypos, direction player must travel ]
        self.starting = False  # If True the area is the first area the player enters
        # [room door leads to, xpos, ypos, direction player must travel ]
        # new list is loaded every time the room is changed
        self.player_pos = []  # used for the players initial position in an area
        self.next_update_time = 0
        self.room_change = False  # set to true when the room changes.
        self.image = None  # the image used for the room
        self.rect = None  # room rectangle
        self.room_map = None  # Map of 0's and 1's describing walls
        self.song = None

    def load_area(self):
        # loads up the area starting position and room
        # This comes from the text file that comes with each area folder
        self.area_data = load_area(os.path.join('data', 'areas', self.name + '.txt'))
        self.menu_name = self.area_data[0]
        self.current_room = self.area_data[1]
        self.player_pos = self.area_data[2]
        self.song = self.area_data[3]
        g.current_area = self.name
        if self.song[0] == 'None':
            fade_black(1500)
        else:
            fade_out(1500)
            play_music(self.song[0], self.song[1], 0.7)

    def load_room(self):
        """ loads up initial map images rects, map grids and door positions"""
        # first load image name and door info froom .doors file
        self.doors = load_doors(
            os.path.join(
                'data', 'areas', self.name, str(
                    self.current_room)+'.doors'))
        # load the room image
        self.image = load_jpg(os.path.join('data', 'areas', 'images', self.doors[0][0]))
        self.rect = self.image.get_rect()
        # get rid of the room image name leaving just the door positions
        self.doors.pop(0)
        # load the room map, 0's and 1's
        self.room_map = [
            i.strip().split() for i in open(
                os.path.join('data',
                             'areas',
                             self.name,
                             str(self.current_room)+'.txt'))]
        if not self.room_change:
            # this is run if the map is being initiated for the first time
            # It positions the map image so that the player lands in the right place
            self.rect.left = -self.player_pos[0]+g.xsize/2
            self.rect.top = -self.player_pos[1]+g.ysize/2

    def change_rooms(self, player, current_time, bottom, right):
        # IF you walk to a door this changes rooms
        if self.next_update_time > current_time:
            for door in self.doors:
                # Check if player collides with a door
                if collision_door(player, door, self, 40):
                    # stores room which player came from: for repositioning player
                    came_from = self.current_room
                    # used for updating objects
                    self.room_change = True
                    # sets the current room
                    self.current_room = door[0]
                    self.load_room()

                    # reposition player and map if the room changes
                    for door in self.doors:
                        if door[0] == came_from:
                            player.going = False
                            player_face_door(player, door)
                            fade_black(200)
                            self.rect.left = player.rect.center[0] - door[1]
                            self.rect.top = player.rect.center[1] - door[2]
                            break

        # check every 50 miliseconds
        self.next_update_time = current_time + 50


class World_map(Area_map):

    """ The world is just a list of the area names
    It inherits the class Area_map as this is used for the current area
    This allows for each area to be loaded only when its needed"""

    def __init__(self):
        self.areas = []   # list of the areas. Just has names
        self.current_area = None
        self.area_names = None
        self.chests = {}
        self.texts = {}

    def load_areas(self):
        # loads up a list of are names.
        # Only used to set the current are atm.
        self.area_names = open(os.path.join('data', 'areas.txt'))
        for name in self.area_names:
            name = name.strip().split()
            self.areas.append(name[0])
        self.current_area = self.areas[0]

    def load_chests(self):
        """ Loads up a list of chests for each area dictionaried to the area_name
        Note, number of rooms in one area is limited to 30 by the length of the chest array"""
        for name in self.areas:
            self.chests[name] = [[], [], [], [], [], [], [],
                                 [], [], [], [], [], [], [],
                                 [], [], [], [], [], [], [],
                                 [], [], [], [], [], [], [],
                                 [], [], [], [], [], [], [],
                                 [], [], [], [], [], [], [],
                                 [], [], [], [], [], [], []]
        # Scroll true areas containing chests
        for area_name in os.listdir(os.path.join('data', 'chest')):
            # check for room folders
            for room_dir in os.listdir(os.path.join('data', 'chest', area_name)):
                for files in os.listdir(os.path.join('data', 'chest', area_name, room_dir)):
                    self.chests[area_name][int(room_dir)].append(False)

    def load_texts(self):
        """ Loads up a list of text objects for each area which can only be interacted with once
        Note, number of rooms in one area is limited to 30 by the length of the chest array"""
        for name in self.areas:
            self.texts[name] = [[], [], [], [], [], [], [],
                                [], [], [], [], [], [], [],
                                [], [], [], [], [], [], [],
                                [], [], [], [], [], [], [],
                                [], [], [], [], [], [], [],
                                [], [], [], [], [], [], [],
                                [], [], [], [], [], [], []]
        # Scroll true areas containing chests
        for area_name in os.listdir(os.path.join('data', 'text')):
            # check for room folders
            for room_dir in os.listdir(os.path.join('data', 'text', area_name)):
                for files in os.listdir(os.path.join('data', 'text', area_name, room_dir)):
                    self.texts[area_name][int(room_dir)].append(False)

    def load_all(self):
        self.load_areas()
        self.load_chests()
        self.load_texts()

    def load_current_area(self):
        # loads current area
        Area_map.__init__(self, self.current_area)
        Area_map.load_area(self)
        Area_map.load_room(self)

    def change_rooms(self, player, current_time, bottom, right):
        # change rooms
        Area_map.change_rooms(self, player, current_time, bottom, right)

    def change_area(self, new_area):
        # change area if new areas name is given
        self.current_area = new_area
        self.load_current_area()
