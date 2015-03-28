import pygame
from random import randint
import os.path
import globals as g
from constants import *
from text_box import TextBox
from sounds import (attack, openc, damage, enemy_dead, ability,
                    levelup, boss_defeated, boss_victory, explosion)
from parse import (
    load_npc_array,
    load_text_array,
    load_chest_array,
    load_enemy_array,
    load_tile_table,
    load_png,
    load_story_array,
    load_jpg,
    play_music)
from collisions import (proximity, fight_enemy, collision_map, collision_room,
                        collision_ply, collision_ob, talk_npc, open_chest, track)
from controls import space_loop, control_ob, control_player, fade_black, fade_out, dim, wait
from menus import Exit_Menu
try:
    import android
    android.init()
except ImportError:
    android = None

try:
    import pygame.mixer as mixer
except ImportError:
    import mixer
exit_menu = Exit_Menu(BLACK)


"""Thisa file contains the classes for npcs chests enemies and other objects
wich are all loaded into the class objects which is a list of sprites that the
player can interact with. It also loads up all the sound effects"""
class Player(object):

    """Player class. used to update and animate the player"""

    def __init__(self):
        self.images = [
            load_png(
                os.path.join('data',
                    'player', 'sidef.png')), load_png(
                os.path.join('data',
                    'player', 'sidef_r1.png')), load_png(
                os.path.join('data',
                    'player', 'sidef_r2.png')), load_png(
                os.path.join('data',
                    'player', 'sideb.png')), load_png(
                os.path.join('data',
                    'player', 'sideb_r1.png')), load_png(
                os.path.join('data',
                    'player', 'sideb_r2.png')), load_png(
                os.path.join('data',
                    'player', 'sider.png')), load_png(
                os.path.join('data',
                    'player', 'sider1.png')), load_png(
                os.path.join('data',
                    'player', 'sidel.png')), load_png(
                os.path.join('data',
                    'player', 'sidel1.png'))]
        # sword images
        self.attack_images = [
            load_png(
                os.path.join('data',
                    'player', 'cut.png')), load_png(
                os.path.join('data',
                    'player', 'cutr.png')), load_png(
                os.path.join('data',
                    'player', 'cutd.png')), load_png(
                os.path.join('data',
                    'player', 'cutl.png'))]
        self.image = self.images[0]
        self.attack_image = self.attack_images[0]  # sword image
        self.attack_rect = self.attack_image.get_rect()
        self.rect = self.image.get_rect()
        self.rect.topleft = [g.xsize/2, g.ysize/2]
        # (d,u,r,l) down up right left defines direction of movement.
        # False or any other value means player is stopped
        self.going = False
        self.speed = 6  # needs to be set to some sort of inventory dependence
        self.investigate = False
        self.attack = False
        self.menu = False
        self.position = None  # players position relative to objects
        self.facing = d  # (d,u,r,l) (down,up,right,left)

    def update(self, room, objects, current_time):
        # If the player is moving we need to check for collisions
        # First check for collisions with room walls or room obstacles
        if (self.going
                and (collision_room(self, room, 10) or collision_map(self, room, 10))):
            self.going = False
        # next check for collisions with objects
        elif self.going:
            for a in objects:
                if collision_ply(self, a, 10):
                    self.going = False
                    break
        # No that collisions have been checked we can update the player
        # This involves changing images and or moving the player
        control_player(self, objects, room, current_time)

    def animate_attack(self, enemy, inventory):
        # Blit sword slash to screen and the health of enemies and the player
        if self.facing == u:
            self.attack_image = self.attack_images[0]
            self.attack_rect = self.attack_image.get_rect()
            self.attack_rect.right = self.rect.right + 20
            self.attack_rect.bottom = self.rect.top + 20

        elif self.facing == d:
            self.attack_image = self.attack_images[2]
            self.attack_rect = self.attack_image.get_rect()
            self.attack_rect.right = self.rect.right + 55
            self.attack_rect.top = self.rect.bottom - 35

        elif self.facing == r:
            self.attack_image = self.attack_images[1]
            self.attack_rect = self.attack_image.get_rect()
            self.attack_rect.left = self.rect.right - 5
            self.attack_rect.bottom = self.rect.bottom + 8

        elif self.facing == l:
            self.attack_image = self.attack_images[3]
            self.attack_rect = self.attack_image.get_rect()
            self.attack_rect.right = self.rect.left + 5
            self.attack_rect.bottom = self.rect.bottom + 8
        g.screen.blit(self.attack_image, self.attack_rect)
        text = TextBox(
            (55, 30), (self.rect.left + 5, self.rect.top + 15), GREEN, fonts[0], 15)
        text.setText(str(inventory.health[0]))
        text2 = TextBox(
            (55, 30), (enemy.rect.left + -10, enemy.rect.top - 10), RED, fonts[0], 15)
        text2.setText(str(enemy.health))
        pygame.display.flip()
        wait(self, 300)


class Npc(object):

    """ nEW npc class desigen to be used for each individual npc
    The idea is that new npcs can be added by just adding a tile grid and a text
    file specifing the npcs attribtes in the npcs position folder.
    It will also use the class name type(object).__name__ to decide how to
    interact with it. all npc's can then be loaded at the start and then used
    as needed or loaded per room as needed and then added to interactable objec
    ts in that current room"""

    def __init__(self, name):
        self.name = name                  # npc's name
        self.moving = False              # If True npc follows random walk
        self.going = False                # The direction the npc is going in
        self.facing = d                   # The direction the npc is faceing
        self.speed = 0
        self.starting_position = [0, 0]    # The npcs starting position
        self.images = []              # The tile of images of the npc
        self.image = None                 # The npcs current image
        self.rect = None                  # The npcs rect
        # The conversation Bob has with the npc
        self.dialogue = []

    def load(self, area, array):
        # given the array obtained from the text files that comes with each
        # npc this loads the array and sets the npcs attributes
        self.name = array[0]
        self.moving = array[1]
        self.facing = array[2]
        self.speed = array[3]
        self.starting_position = array[4]   # sets starting position
        self.dialogue = array[5]
        # Load up the images of the npc
        self.images = load_tile_table(os.path.join('data', 'npc', 'images', self.name + '.png'), 3, 4)
        self.image = self.images[1][self.facing]  # picks the facing down image
        self.rect = self.image.get_rect()  # get the rectangle
        self.rect.left = area.rect.left + \
            self.starting_position[0]  # place x
        self.rect.top = area.rect.top + \
            self.starting_position[1]    # place y

    def interact(self, area, player):
        # sets what happens when an npc is interacted with
        # first we set the npc to face our player using the players position
        # from the interact objects function
        if player.position == d:
            self.image = self.images[1][0]
        elif player.position == r:
            self.image = self.images[1][2]
        elif player.position == l:
            self.image = self.images[1][1]
        elif player.position == u:
            self.image = self.images[1][3]
        # update sprites
        g.screen.blit(
            area.image,
            self.rect,
            (self.rect.left -
             area.rect.left,
             self.rect.top -
             area.rect.top,
             self.rect.width,
             self.rect.height))                        # blits map over current npc
        g.screen.blit(self.image, self.rect)       # blits new npc image
        g.screen.blit(player.image, player.rect)  # blits player character
        dim(120)  # DIm the screen by 55 %
        # vary the position of the conversation boxes
        boxposx = g.xsize/8+randint(0, 1)*(g.xsize-(450+2*g.xsize/8))
        boxposy = g.ysize/8+randint(0, 1)*(g.ysize-(110 + 2*g.ysize/8))  # same
        for sentance in self.dialogue:
            # loops through dialogue
            text = TextBox((450, 110), (boxposx, boxposy), GREY, fonts[1], 28)
            text.wait = True
            text.setText(sentance)
            player.investigate = False
            # Loops on each dialogue entry until the player presses space bar
            space_loop(player)
        # after space loop need to reset player.investigate
        player.investigate = False
        player.going = False

    def update(self, area, objects, player, current_time):
            # updates moving npcs
        timing = 0
        if self.moving:
            # check collisions with maps
            if (self.going
                and (collision_room(self, area, 10) or collision_map(self, area, 10))):
                self.going = False
            # next check for collisions with objects
            elif self.going:
                for a in objects + [player]:
                    if collision_ply(self, a, 10):
                        self.going = False
                        break
            # update images and move object
            control_ob(
                self,
                objects,
                player,
                area,
                current_time)
            # randomly selects movement direction every 2 seconds. 2/5 chance not to move
            # if not moving then it randomly selects a facing direction
            if (1100*4/self.speed+60 > (current_time+timing) % 2200*4/self.speed >
               1100*4/self.speed):
                self.going = randint(0, 5)
                if self.going == 0 or self.going == 5:
                    self.facing = randint(1, 4)
                else:
                    self.facing = self.going
                # seperates times at which npc randomly decide to move by 0.4
                # seconds
            timing = timing+350


class Text_dis(object):

    """Text class, blits text to the screen if the player walks near the object. Used to give direction etc"""

    def __init__(self, name):
        self.num = 0                 # object name
        self.starting_position = [0, 0]    # position where you run to make text appear
        self.image = None                 # The image transpant
        self.rect = None                  # The image rect
        # text blitted to screen
        self.text = []
        self.display_time = False         # used to regulate the display time of the text
        self.xpos = g.xsize/7+randint(0, 1)*(g.xsize-(410+2*g.xsize/7))
        self.ypos = g.ysize/7+randint(0, 1)*(g.ysize-(120 + 2*g.ysize/7))  # same
        self.interacting = False     # is the object being interacted with
        self.finished = False     # is it finished interacting
        self.font = 0

    def load(self, area, array):
        # given the array obtained from the text files that comes with each
        # npc this loads the array and sets the npcs attributes
        if area.texts[area.current_area][area.current_room][self.num] is True:
            self.finished = True
        self.name = array[0]
        self.font = array[1]
        self.starting_position = array[2]   # sets starting position
        self.text = array[3]
        self.image = text_image  # image
        self.rect = self.image.get_rect()  # get the rectangle
        self.rect.left = area.rect.left + \
            self.starting_position[0]  # place x
        self.rect.top = area.rect.top + \
            self.starting_position[1]    # place y

    def interact(self, current_time, area):
        if self.interacting is True:
            if self.display_time is False:
                self.display_time = current_time

            if current_time < self.display_time + 5500:
                for i in range(0, len(self.text)):
                    # loops through dialogue
                    dim(100)
                    text = TextBox(
                        (410, 120), (self.xpos, self.ypos), DARKGREEN, fonts[
                            self.font], 29)
                    text.setText(self.text[i])
            else:
                self.finished = True
                area.texts[area.current_area][area.current_room][self.num] = True


class Chest(object):

    def __init__(self, num):
        # chests are numbered to keep track of whats been opened
        self.num = num
        self.contents = None  # contents
        self.image = None     # chest image
        self.rect = None      # chest rect
        self.position = None  # position of the chest
        self.open = None

    def load(self, area, array):
        # given the array obtained from the text files that comes with each
        # chest this loads chest
        self.num = array[0]
        self.position = array[1]
        self.contents = array[2]
        if area.chests[area.current_area][area.current_room][self.num] is False:
            self.open = False
            self.image = chest_images[0]
            self.rect = self.image.get_rect()

        else:
            self.open = True
            self.image = chest_images[1]
            self.rect = self.image.get_rect()
        # position chest
        self.rect.left = area.rect.left + self.position[0]
        self.rect.top = area.rect.top + self.position[1]

    def interact(self, area, inventory, player):
        if self.open is False:
            # prints contents in a text box
            openc.play()
            self.open = True
            area.chests[area.current_area][area.current_room][self.num] = True
            self.image = chest_images[1]
            g.screen.blit(self.image, self.rect)  # blits open box
            g.screen.blit(player.image, player.rect)
            dim(120)  # DIm the screen
            # vary the position of the conversation boxes
            boxposx = g.xsize/6+randint(0, 1)*(g.xsize-(200+2*g.xsize/6))
            boxposy = g.ysize/6+randint(0, 1)*(g.ysize-(45 + 2*g.ysize/6))  # same
            text = TextBox((200, 45), (boxposx, boxposy), BLUE, fonts[2], 22)
            text.setText(self.contents)
            player.investigate = False
            player.going = False
            space_loop(player)
            # update the inventory
            inventory.update_inventory(self.contents)


class Enemy(object):

    """This is similiar to the npc class. Except that an interaction
    will involve some basic fighting of some basic fighting of some sort."""

    def __init__(self, name):
        self.name = name                  # enemies's name
        self.moving = False              # If True enemy follows random walk
        self.going = False                # The direction the enemy is going in
        self.facing = d                   # The enemies faceing
        self.speed = 0                      # The enemies speed
        self.health = 0                     # The enmies health points
        self.strength = 0                   # The enemies strength
        self.next_attack_time = 0           # The time until the next attack
        self.display_time = 0               # The time the damage is displayed for
        self.starting_position = [0, 0]    # The enemy's starting position
        self.images = []              # The tile of images of the enemy
        self.image = None                 # The enemy current image
        self.rect = None                  # The enemy rect
        self.next_update_time = 100*randint(0, 4)+30*randint(0, 3)
        # loads enemys of to the starting room

    def load(self, area, array):
        # given the array obtained from the text files that comes with each
        # enemy this loads the array and sets the enemies attributes
        self.moving = array[1]
        self.health = array[2]
        self.strength = array[3]
        self.speed = array[4]
        self.starting_position = array[5]   # sets starting position
        self.images = load_tile_table(
            os.path.join('data', 'enemy', 'images', array[6]),
            3,
            4)  # loads the array of images
        self.image = self.images[1][0]  # picks the facing down image
        self.rect = self.image.get_rect()  # get the rectangle
        self.rect.left = area.rect.left + \
            self.starting_position[0]  # place x
        self.rect.top = area.rect.top + \
            self.starting_position[1]    # place y

    def update(self, area, objects, player, current_time):
            # updates moving npcs
        if self.moving:
            # check collisions with maps
            if (self.going
                 and (collision_room(self, area, 10) or collision_map(self, area, 10))):
                self.going = randint(1,4)
            # next check for collisions with objects
            elif self.going:
                for a in objects:
                    if collision_ob(self, a, 12):
                        self.going = randint(1,4)
                        break
                if collision_ob(self, player, 12):
                    self.going = False
            # function to control sprite switching, movement and collisions
            control_ob(
                self,
                objects,
                player,
                area,
                current_time)
            # randomly selects movement direction every 2 seconds.
            # if not moving then it randomly selects a facing direction
            if self.next_update_time < current_time:
                track(self, player)
                self.facing = self.going
                self.next_update_time = current_time + 1200/self.speed
                # seperates times at which npc randomly decide to move by 0.4
                # seconds

    def enemy_attack(self, player, inventory, current_time):
        # if there are enemies in the room
        if self.next_attack_time < current_time:
            damage.play()
            inventory.health[0] -= (4*self.strength*randint(5, 8)+randint(1, 4))/inventory.defence
            if android:
                android.vibrate(0.1)
            self.next_attack_time = current_time + 1200
            self.display_time = current_time + 600
        if current_time < self.display_time:
            text = TextBox(
                (55, 30), (player.rect.left + 5, player.rect.top + 20), GREEN, fonts[0], 15)
            text.setText(str(inventory.health[0]))
            text2 = TextBox(
                (55, 30), (self.rect.left - 10, self.rect.top - 10), RED, fonts[0], 15)
            text2.setText(str(self.health))
            damage_rect.top = player.rect.top + 2
            damage_rect.left = player.rect.left + 15
            g.screen.blit(damage_image, damage_rect)

    def animate_ability(self):
        text2 = TextBox(
            (55, 30), (self.rect.left - 10, self.rect.top - 10), RED, fonts[0], 15)
        text2.setText(str(self.health))


class story_object(object):

    """This object is used to update the area. This doesn't necissarly mean change to a new map
    area. New areas can be the samelace but with different objects. An example is that npc dialogue
    could change"""

    def __init__(self):
        self.position = []
        self.image = None
        self.rect = None                  # Object image
        self.new_area = None             # The are which the object moves you too
        # The conversation Bob has with the npc

    def load(self, area, array):
        self.image = load_png(os.path.join('data', 'story', 'images', array[0]))
        self.rect = self.image.get_rect()
        self.position = array[1]
        self.new_area = array[2]
        self.rect.left = area.rect.left + self.position[0]  # place x
        self.rect.top = area.rect.top + self.position[1]    # place y
        self.keyitem = array[3][0]
        array[3].pop(0)  # Remove the item part of the array.
        self.info_string = array[3]  # A string of info on what item is needed
        self.song = array[4]
        self.haveitem = False
        self.background_images = []
        self.background_rects = []
        self.dialogues = []
        for i in range(5, len(array)):
            # Load up story line images and names
            self.background_images.append(load_jpg(os.path.join('data', 'story', 'images', array[i][0])))
            self.background_rects.append(self.background_images[i-5].get_rect())
            array[i].pop(0)
            self.dialogues.append(array[i])

    def reset_wedding_rint(self, inventory):
        # After Norman gets the bad news at the start give the wedding ring negative power
        if self.keyitem == 'Dukes letter':
            for accessory in inventory.accessories:
                if accessory.name == 'Wedding ring':
                    accessory.power = -3
                    inventory.update_equipment()

    def interact(self, area, player, inventory):
        """This cycles through images and text to further the storyline the player posses
        the correct key_item"""
        for item in inventory.keyitems:
            # Check if the player posses the necassary key item and set the have item attribute
            if item.name == self.keyitem and item.posses is True:
                self.haveitem = True
                self.reset_wedding_rint(inventory)
                break
        if self.haveitem is True:
        # If we have the key item
        # First fade the screen to black
            if self.song[0] == 'None':
                fade_black(1500)
            else:
                fade_out(1500)
                play_music(self.song[0], self.song[1], 0.7)

            for i in range(0,len(self.background_images)):
                if 9*self.background_rects[i].height > 10*g.ysize + 1:
                    self.background_images[i] = pygame.transform.scale(self.background_images[i],
                                                                       (14*self.background_rects[i].width*g.ysize/(13*self.background_rects[i].height),
                                                                        14*self.background_rects[i].height*g.ysize/(13*self.background_rects[i].height)))
                    self.background_rects[i] = self.background_images[i].get_rect()

            for i in range(0, len(self.background_images)):
                # Cycle true images
                exit_menu.update()
                g.screen.fill((0, 0, 0))
                self.background_rects[i].center = (g.xsize/2, g.ysize/2)
                g.screen.blit(self.background_images[i], self.background_rects[i])
                space_loop(player)
                for sentance in self.dialogues[i]:
                    exit_menu.update()
                    # cycle true dialogue
                    g.screen.fill((0, 0, 0))
                    g.screen.blit(self.background_images[i], self.background_rects[i])
                    pygame.display.flip()
                    wait(player, 500)
                    boxposx = 28+randint(0, 1)*(g.xsize-586)
                    boxposy = 24+randint(0, 1)*(g.ysize-168)  # same
                    # player.investigate = False
                    # loops through dialogue

                    text = TextBox((530, 125), (boxposx, boxposy), GREY, fonts[3], 29)
                    text.wait = True
                    text.setText(sentance)
                    # Loops on each dialogue entry until the player presses space bar
                    player.investigate = False
                    space_loop(player)
                if self.new_area != 'Credits' or len(self.dialogues[i]) != 2:
                    # fades out every image except for the final one
                    fade_black(1000)
            player.investigate = False
            player.rect.topleft = [g.xsize/2, g.ysize/2]
            if self.new_area == 'Credits':
                inventory.credits = True
            else:
                area.change_area(self.new_area)
                area.room_change = True

        else:
            boxposx = 28+randint(0, 1)*(g.xsize-576)
            boxposy = 24+randint(0, 1)*(g.ysize-168)  # same
            # player.investigate = False
            # loops through dialogue
            dim(100)  # DIm the screen by 55 %
            for info in self.info_string:
                # loops through dialogue
                text = TextBox((450, 110), (boxposx, boxposy), BLUE, fonts[1], 28)
                text.wait = True
                text.setText(info)
                player.investigate = False
                # Loops on each dialogue entry until the player presses space bar
                space_loop(player)
            # after space loop need to reset player.investigate
            player.investigate = False


class Boss(Enemy):

    """Boss class. An Enemy which spawns smaller enemies at various time.
    Killing the boss loads a new area"""

    def __init__(self, name):
        Enemy.__init__(self, name)
        self.defeated = False
        self.next_sound_time = 0

    def load(self, area, array):
        Enemy.load(self, area, array)
        self.new_area = array[7][0]
        self.sound = mixer.Sound(os.path.join('data', 'sounds',array[8][0]))
    def update(self, area, objects, player, current_time):
        Enemy.update(self, area, objects, player, current_time)

    def enemy_attack(self, player, inventory, current_time):
        Enemy.enemy_attack(self, player, inventory, current_time)

    def animate_ability(self):
        Enemy.animate_ability(self)

    def load_spawn(self, area, array):
        self.spawn = Enemy('spawn')
        self.spawn.load(area, array)
        self.spawn_health = self.spawn.health
        self.next_spawn_time = 0

    def spawn_enemy(self, interobjects, player, current_time):
        if current_time > self.next_sound_time:
            self.sound.play()
            self.next_sound_time = current_time + 10000
        if current_time > self.next_spawn_time and self.spawn not in interobjects.enemies:
            self.next_spawn_time = current_time + 15000
            self.spawn.health = self.spawn_health
            self.spawn.rect.center = (self.rect.center[0]+
                                      (player.rect.center[0]-self.rect.center[0])/2,
                                       self.rect.center[1]+
                                      (player.rect.center[1]-self.rect.center[1])/2)
            interobjects.objects.append(self.spawn)
            interobjects.enemies.append(self.spawn)

    def defeat(self, current_time):
        g.boss_defeated = True
        mixer.music.stop()
        explosion.play()
        boss_defeated.play()
        pygame.time.wait(1000)
        self.victory_time = current_time + 10000
        self.defeated = True

    def victory(self, area, player, current_time):
        dim(190)
        text = TextBox(
            (240,
                100),
            ((g.xsize-240)/2,
                (g.ysize-100)/2),
            BLUE,
            fonts[3],
            32)
        text.setText('Vanquished '+' '+self.name)
        levelup.play()
        if android:
            android.vibrate(0.6)
        boss_victory.play()
        g.boss_defeated = False
        pygame.display.update()
        pygame.time.wait(3000)
        fade_out(1000)
        player.rect.topleft = [g.xsize/2, g.ysize/2]
        area.change_area(self.new_area)
        area.room_change = True


class Interactable_Objects(object):

    """This collects together all of the other objects that can be intereacted with
        This includes npcs enemies, chest and others"""

    def __init__(self):
        self.next_update_time = 0
        self.next_fight_time = 0
        self.ability_animate_time = 0
        self.fighting = False
        # list of objects, all objects in a room are loaded to this list when player enters room
        self.objects = []  # Used to detec collisons between objects and players
        self.enemies = []
        self.npcs = []
        self.text_dis = []
        self.chests = []
        self.stories = []
        self.boss = False
        # used store where the player is with respect to the object: u, d, l, or r

    def load_Npcs(self, area):
        """Loads up the npc's of the current room when"""
        # in order to create npc objects we create a dictionary to store load them with names
        npcs = {}
        for root, dirs, files in os.walk(os.path.join('data', 'npc', area.name, str(area.current_room))):
            for name in files:
                filename = os.path.join(root, name)
                if str(filename).find("txt") != -1:
                    # get the npc attributes
                    array = load_npc_array(filename)
                    # create the dictionary entry with the name as the key
                    npcs[filename] = Npc(filename)
                    # Load up the npc attributes from its text file: include dialogue, images etc
                    npcs[filename].load(area, array)
                    self.objects.append(npcs[filename])  # add the npc to objects list
                    self.npcs.append(npcs[filename])  # add to the npc list

    def load_Text(self, area):
        self.tetdis = []
        text_dis = {}
        for root, dirs, files in os.walk(os.path.join('data', 'text', area.name, str(area.current_room))):
            for name in files:
                filename = os.path.join(root, name)
                array = load_text_array(filename)
                # create the dictionary entry with the name as the key
                text_dis[filename] = Text_dis(array[0])
                # load up the text display object
                text_dis[filename].load(area, array)
                self.objects.append(text_dis[filename])  # add the text display to the objects
                # add the text display to the list of text displays
                self.text_dis.append(text_dis[filename])

    def load_Chests(self, area):
        """Loads up the chests in the current room"""
        chests = {}  # use dictionary to load chests dictionaried to there names
        for root, dirs, files in os.walk(os.path.join('data', 'chest', area.name, str(area.current_room))):
            for name in files:
                filename = os.path.join(root, name)
                # get the chest attributes
                array = load_chest_array(filename)
                # create the chest object to its name
                chests[array[0]] = Chest(array[0])
                # lOad its attributes
                chests[array[0]].load(area, array)
                self.objects.append(chests[array[0]])   # add it to the list of objects
                self.chests.append(chests[array[0]])

    def load_Enemies(self, area):
        """LOad up the enemies in the current room"""
        enemys = {}
        for root, dirs, files in os.walk(os.path.join('data' ,'enemy', area.name, str(area.current_room))):
            for name in files:
                filename = os.path.join(root, name)
                if str(filename).find("txt") != -1:
                    # get the enemy attributes
                    array = load_enemy_array(filename)
                    # create the dictionary entry with the name as the key
                    # and the enemy object as its value
                    enemys[array[0]] = Enemy(array[0])
                    # load its attributes: health, seed, poition, image...etc
                    enemys[array[0]].load(area, array)
                    self.objects.append(enemys[array[0]])  # add to objects
                    self.enemies.append(enemys[array[0]])

    def load_Boss(self, area):
        for root, dirs, files in os.walk(os.path.join('data', 'boss', area.name, str(area.current_room))):
            for name in files:
                filename = os.path.join(root, name)
                if str(filename).find("boss.txt") != -1:
                    # get the enemy attributes
                    mixer.music.stop()
                    play_music('boss.ogg', 0, 0.9)
                    array = load_enemy_array(filename)
                    self.boss = Boss(array[0])
                    self.boss.load(area, array)
                    self.enemies.append(self.boss)
                    self.objects.append(self.boss)
                    array = load_enemy_array(os.path.join(root, 'spawn'))
                    self.boss.load_spawn(area, array)

    def load_story_objects(self, area):
        """Load up the story line objects in a room"""
        story = {}
        for root, dirs, files in os.walk(os.path.join('data', 'story', area.name, str(area.current_room))):
            for name in files:
                filename = os.path.join(root, name)
                array = load_story_array(filename)
                story[array[0]] = story_object()
                story[array[0]].load(area, array)
                self.objects.append(story[array[0]])
                self.stories.append(story[array[0]])

    def melee_fight(self, area, player, inventory, current_time):
        # Battle enemies within melee range
        self.fighting = False
        for enemy in self.enemies:
                # first check if player is close to an enemy and if that object is an enemy
            if proximity(player, enemy, 15):
                if (player.investigate and current_time > self.next_fight_time
                   and fight_enemy(player, enemy)):
                    self.next_fight_time = current_time + 24*inventory.stats[5].quantity
                    # damages the enemy
                    attack.play()
                    player.animate_attack(enemy, inventory)   # Animate players attack
                    enemy.health -= (inventory.attack*randint(3, 6)+randint(0, 4))/4
                    if enemy.health <= 0 and enemy != self.boss:
                        enemy_dead.play()
                        if android:
                            android.vibrate(0.3)
                        inventory.exp -= enemy.strength*3
                        self.objects.remove(enemy)
                        self.enemies.remove(enemy)
                        inventory.level_up()
                    elif enemy.health <= 0 and enemy == self.boss:
                        if android:
                            android.vibrate(1.2)
                        inventory.exp -= enemy.strength*7
                        enemy.defeat(current_time)
                        inventory.level_up()
                        self.objects.remove(enemy)
                        self.enemies.remove(enemy)
                    player.investigate = False
                # Enemy damages Norman
                self.fighting = True
                enemy.enemy_attack(player, inventory, current_time)

    def ability_fight(self, area, player, inventory, current_time):
        """Fight using ability. Only works when no enemies are in Melee range.
        Can hit multiple enemies"""
        if self.fighting is False and current_time > self.next_fight_time and player.investigate:
            self.hit_enemies = []
            for enemy in self.enemies:
                if proximity(player, enemy, 15+5+inventory.ability.power*7):
                    self.next_fight_time = current_time + 24*inventory.stats[5].quantity
                    self.ability_animate_time = current_time + 600
                    self.hit_enemies.append(enemy)
                    enemy.health -= (inventory.confidence*randint(3, 6)+randint(0, 4))/4
                    ability.play()
                    player.investigate = False
                    if enemy.health <= 0 and enemy != self.boss:
                        enemy_dead.play()
                        if android:
                            android.vibrate(0.3)
                        inventory.exp -= enemy.strength*3
                        self.objects.remove(enemy)
                        self.enemies.remove(enemy)
                        inventory.level_up()
                    elif enemy.health <= 0 and enemy == self.boss:
                        if android:
                            android.vibrate(1.2)
                        inventory.exp -= enemy.strength*7
                        enemy.defeat(current_time)
                        inventory.level_up()
                        self.objects.remove(enemy)
                        self.enemies.remove(enemy)

        if current_time < self.ability_animate_time:
            inventory.ability.animate(player.rect.center)
            for enemy in self.hit_enemies:
                enemy.animate_ability()

    def pop_up_text(self, player, area, current_time):
        for text_dis in self.text_dis:
            # If we approach the object, start interacting
            if proximity(player, text_dis, 128):
                text_dis.interacting = True

            # when finished remove from objects
            if ((text_dis.finished) and not area.room_change):
                self.objects.remove(text_dis)
                self.text_dis.remove(text_dis)
                break

            text_dis.interact(current_time, area)

    def interact_npc_chest_story(self, player, inventory, area):
        if player.investigate is True:
            # If the player is investigating check check for interactions with npc's or chests

            for npc in self.npcs:
                if talk_npc(player, npc):
                    npc.interact(area, player)

            for chest in self.chests:
                if open_chest(player, chest):
                    chest.interact(area, inventory, player)

            for story in self.stories:
                if proximity(player, story, 15) and abs(g.mouse_position[0] - story.rect.center[0]) < 74 and abs(g.mouse_position[1] - story.rect.center[1]) < 74:
                    player.going = False
                    story.interact(area, player, inventory)

    def update(self, area, player, current_time):
        """if we change rooms, loads up the new objects, otherwise just updates the
        positions of the current objects"""
        if area.room_change:
            area.room_change = False
            # FIst empty all the object lists
            self.objects, self.enemies, self.npcs, self.chests, self.stories, self.text_dis = [
                ], [], [], [], [], []
            self.load_Chests(area)
            self.load_Npcs(area)
            self.load_Text(area)
            self.load_Enemies(area)
            self.load_Boss(area)
            self.load_story_objects(area)

        for a in self.enemies + self.npcs:
            a.update(area, self.objects, player, current_time)

    def interact_objects(self, player, area, inventory, current_time):
        # interacts with interactable objects
        # First fight any enemies
        if self.boss is not False:
            # If there is a boss spawn extran enemies or display vitory
            if self.boss.defeated is False:
                self.boss.spawn_enemy(self, player, current_time)
            elif self.boss.defeated is True:
                if current_time > self.boss.victory_time:
                    self.boss.victory(area, player, current_time)
                    self.boss = False
        self.melee_fight(area, player, inventory, current_time)
        self.ability_fight(area, player, inventory, current_time)
        # Then pop up text
        self.pop_up_text(player, area, current_time)
        # finally interact with chests npc's and story objects
        self.interact_npc_chest_story(player, inventory, area)
        player.investigate = False


# using a list to keep track of weather the chests are open or not for want of a better method
# can possiby write an os.walk method for producing this list when the
# game is started
# only 2 images so permanently load them
chest_images = [load_png(os.path.join('data' , 'chest.png')), load_png(os.path.join('data', 'chest_open.png'))]
text_image = load_png(os.path.join('data', 'text.png'))
damage_image = load_png(os.path.join('data', 'enemy', 'images', 'damage.png'))
damage_rect = damage_image.get_rect()
