import pygame
import os.path
import pickle
from pygame.locals import *
import globals as g
from sounds import select, damage, revive
from constants import *
from text_box import Blitted_rect, TextBox
from controls import control_events, control_events_menu, wait, fade_black, fade_out, dim, space_loop
from parse import load_jpg, load_png, play_music
try:
    import android
    android.init()
except ImportError:
    android = None

try:
    import pygame.mixer as mixer
except ImportError:
    import mixer
# used for game menu, battle menu, dialogue options etc.


class Menu(object):

    """Used to control Menus. Given a list of choices this Blits the choices to the screen
    and allows scrolling through the choices"""

    def __init__(self, font, font_size):
        self.menu_entries = []  # menu options
        self.index = 0  # current selection
        self.icon_image = load_png(os.path.join('data', 'icon.png'))
        self.rect = self.icon_image.get_rect()
        self.font = font
        self.font_size = font_size
        self.going = False  # allows control events to work on the menu screen
        self.investigate = False
        self.menu = False
        self.next_update_time = 0
        self.choice = None
        self.touch_ypos = 0
        self.touched = False

    def menu_control(self, choices, x_pos, y_pos, color):
        # if it is not yet positioned, icon is postion in top left hand corner:
        # of the menu only
        if self.rect.topleft == (0, 0):
            self.rect.topleft = (x_pos-20, y_pos)

        self.initial_icon_position = y_pos  # used fro repositioning icon
        # control_events used to move icon and select items
        control_events_menu(self, x_pos, x_pos)
        if self.touched:
            self.touch_ypos = self.touch_ypos - y_pos
            self.touched = False
        self.total = 0
        # used to keep track of the length of the menu
        self.menu_entries = []
        for choice in choices:
            # take the list of choices
            self.total += 1
            self.menu_entries.append(choice)
            # cover old icons first with a rectangle
            text = Blitted_rect((60, 41), (x_pos-40, y_pos-5), color)
            text = TextBox((190, 41), (x_pos+20, y_pos-5), color, self.font, self.font_size)
            text.setText(choice)
            y_pos += 45

        #g.screen.blit(self.icon_image, self.rect)
        self.index = self.touch_ypos/45
        if self.index > self.total + 1:
            self.investigate = False
            self.index = 0
        elif self.index > self.total - 1:
            self.index = self.total - 1
        elif self.index < 0:
            self.index = 0

        # scrolls down through items

        self.rect.top = self.initial_icon_position + self.index*45   # repositions icon



class Exit_Menu(Menu):
    # For when the player presses escape
    def __init__(self, color):
        Menu.__init__(self, fonts[3], 23)
        # Main game menu which displays inventory
        self.choices = ['Quit Game', 'Continue']
        self.color = color

    def update(self):
        control_events_menu(self, g.xsize, g.ysize)
        #wait(self,3000)
        self.investigate = False
        while g.exit_menu_on is True:
            if android:
                if android.check_pause():
                    mixer.music.pause()
                    android.wait_for_resume()
                    mixer.music.unpause()
            # Menu Loop
            # passes choices and menu position to menu control
            text = Blitted_rect((270, 105), (g.xsize/2 - 145, g.ysize/2-45), self.color)
            Menu.menu_control(
                self,
                self.choices,
                g.xsize/2 - 95,
                g.ysize/2-40,
                self.color)  # Control Menu

            # if we are in itial choices update our choices depending
            if self.investigate and self.index == 0:
                exit()

            elif self.investigate and self.index == 1:
                g.exit_menu_on = False
                self.index = 0

            pygame.display.update()
            pygame.time.wait(50)  # Reduce the cpu load waiting for 50 miliseconds every loop


exit_menu = Exit_Menu(BLACK)

class Intro_Menu(Menu):

    def __init__(self, color):
        Menu.__init__(self, fonts[3], 23)
        # Main game menu which displays inventory
        self.choices = ['New Game', 'Load Game']
        self.color = color
        self.menu_on = True
        self.first_start = True
        self.back_image = load_png(os.path.join('data', 'story', 'images', 'Sorceror.jpg'))
        self.back_rect = self.back_image.get_rect()
        self.back_rect.center = (g.xsize/2, g.ysize/2)
        self.menu = False

    def exit_menu_on(self):
        if self.menu is True:
            self.menu = False
            g.exit_menu_on = True
            exit_menu.update()

    def blit_information(self, size, time, width, height, textblit):
        text = TextBox(
            (width,
             height),
            ((g.xsize-width)/2,
             (g.ysize-height)/2),
            BLACK,
            fonts[3],
            size)
        text.space_centered_text(textblit, 14)
        pygame.display.update()
        wait(self,time)
        fade_black(1500)
        control_events_menu(self, g.xsize, g.ysize)
        self.exit_menu_on()

    def intro(self):
        play_music('main.ogg', 0, 1.0)
        wait(self,2000)
        text = TextBox(
            (900,
             90),
            (0,
             (g.ysize-70)/2-150),
            BLACK,
            fonts[3],
            40)
        text.space_centered_text('An Obedient Cat production', 14)
        self.background_image = load_png(os.path.join('data', 'catlogo.png'))
        self.background_rect = self.background_image.get_rect()
        self.background_rect.center = (g.xsize/2, g.ysize/2)
        text = TextBox(
            (900,
             90),
            (0,
             (g.ysize-70)/2+150),
            BLACK,
            fonts[0],
            25)
        text.space_centered_text('www.brendanbulfin.org/first-reality', 14)
        g.screen.blit(self.background_image, self.background_rect)
        pygame.display.flip()
        wait(self, 2000)
        fade_black(1500)
        control_events_menu(self, g.xsize, g.ysize)
        self.exit_menu_on()
        text = TextBox(
            (900,
             90),
            (0,
             (g.ysize-70)/2-150),
            BLACK,
            fonts[3],
            40)
        text.space_centered_text('In association with', 14)
        self.background_image = load_png(os.path.join('data', 'rainwater.png'))
        self.background_rect = self.background_image.get_rect()
        self.background_rect.center = (g.xsize/2, g.ysize/2)
        text = TextBox(
            (900,
             90),
            (0,
             (g.ysize-70)/2+150),
            BLACK,
            fonts[0],
            25)
        text.space_centered_text('www.rainwaterstudio.ie', 14)
        g.screen.blit(self.background_image, self.background_rect)
        pygame.display.flip()
        wait(self, 2000)
        fade_black(1500)
        control_events_menu(self, g.xsize, g.ysize)
        self.exit_menu_on()

        self.blit_information(60, 3000, 520, 90, 'First Reality XVII')

    def blit_credits(self, title, names, width):
        text = TextBox((900, 70), ((0, 70)), BLACK, fonts[3], 40)
        text.space_centered_text(title, 10)
        pos = 85
        for name in names:
            pos += 55
            text1 = TextBox((900, 70), ((g.xsize-width)/2 + 25, pos), BLACK, fonts[1], 35)
            text1.space_centered_text(name, 8)
        pygame.display.update()
        wait(self,6000)
        control_events_menu(self, g.xsize, g.ysize)
        self.exit_menu_on()
        fade_black(1500)
        control_events_menu(self, g.xsize, g.ysize)
        self.exit_menu_on()

    def blit_image(self, image):
        self.background_image = load_jpg(os.path.join('data', 'story', 'images', image))
        self.background_rect = self.background_image.get_rect()
        if 9*self.background_rect.height > 10*g.ysize + 1:
            self.background_image = pygame.transform.scale(self.background_image,
                                                          (14*self.background_rect.width*g.ysize/(13*self.background_rect.height),
                                                           14*self.background_rect.height*g.ysize/(13*self.background_rect.height)))
            self.background_rect = self.background_image.get_rect()
        self.background_rect.center = (g.xsize/2, g.ysize/2)
        g.screen.blit(self.background_image, self.background_rect)
        pygame.display.flip()
        wait(self, 4000)
        fade_black(1500)
        control_events_menu(self, g.xsize, g.ysize)
        self.exit_menu_on()

    def role_credits(self):
        self.background_image = load_jpg(os.path.join('data', 'story', 'images', 'hung.jpg'))
        self.background_rect = self.background_image.get_rect()
        if 9*self.background_rect.height > 10*g.ysize + 1:
            self.background_image = pygame.transform.scale(self.background_image,
                                                          (14*self.background_rect.width*g.ysize/(13*self.background_rect.height),
                                                           14*self.background_rect.height*g.ysize/(13*self.background_rect.height)))
            self.background_rect = self.background_image.get_rect()
        self.background_rect.center = (g.xsize/2, g.ysize/2)
        g.screen.fill((0, 0, 0))
        g.screen.blit(self.background_image, self.background_rect)
        pygame.display.flip()
        wait(self,4000)
        wait(self, 3000)
        mixer.music.load(os.path.join('data', 'music', 'credits.ogg'))
        mixer.music.play(0)
        wait(self,18000)
        fade_black(3000)
        text = TextBox(
            (g.xsize - 220,
                g.ysize-370),
            ((g.xsize - 420)/2,
                (g.ysize-110)/2),
            BLACK,
            fonts[3],
            63)
        text.space_centered_text('THE END', 20)
        pygame.display.update()
        wait(self,3000)
        fade_black(1500)
        self.blit_information(50 ,3000, 500, 100, 'First Reality')
        self.blit_credits('Developer', ['Brendan Bulfin'], 350)
        self.blit_credits('Engine coding', ['Brendan Bulfin', 'with some help from', 'Kyle Ballantine'], 330)
        self.blit_credits('Ported to OS X by', ['Jack Hayes', 'and', 'Barry Murphy'], 330)

        self.blit_credits('Main Artists', ['Aoife Bulfin', 'Aveen Bulfin', 'Brendan Bulfin', 'Finn Nichol'], 300)
        self.blit_credits('Other Artists', ['Hugh Bulfin', 'Matilda Guffog'], 270)
        self.blit_credits('Other Artists', ['Dan Kirby', 'Kieran Brennan', 'Daniela Carta'], 270)
        self.blit_credits('Sprite Art', ['Brendan Bulfin'], 270)
        self.blit_credits('SFX Editor', ['James Garvey'], 270)


        self.blit_credits('Self Quotes', ['Cormac Mc Carthy', 'Mary Shelly', 'Dr. Zeus','' ], 280)

        self.blit_credits('Composers', ['Aidan Guilfoyle', 'James Garvey', 'Marty Walsh', 'Patrick McGlynn (Dr. Mindflip)'], 320)
        self.blit_credits('Aidan Guilfoyle', ['Main theme', 'Drakmoor', 'Tower of Trials (Dr. Mindflip)'], 340)
        self.blit_credits('James Garvey', ['Twilight', 'Swamp', 'Sex Scene'], 340)
        self.blit_credits('Marty Walsh', ['Horrors', 'Stone Alone'], 310)
        self.blit_credits('Dan Kirby', ['Bazookie riffs', 'Spanish vocals'], 280)
        self.blit_credits('freesound.org', ['sepal', 'joshuaempyre','edtijo'], 280)


        self.blit_information(50, 3000, 410, 100, 'Credits Song')
        self.blit_credits('Stars Align', ['The Ballad of Norman'], 380)
        self.blit_credits('Composed by', ['Aidan Guilfoyle', 'Dan Kirby', "Colin O'Brien"], 330)
        self.blit_credits('Recording and Mastering', ['Rainwater Studio', 'Kilbeggan', "Co. Westmeath"],560)
        self.blit_credits('Aidan Guilfoyle', ['Production', 'Mixing', 'Bass', 'Rythm Guitar', "Acoustic Guitar"], 380)
        self.blit_credits('Patrick McGlynn (Dr. Mindflip)', ['Mastering', 'Mellotron', "Synth"], 560)
        self.blit_credits("Colin O'Brien", ['Percussion'], 350)
        self.blit_credits("James Garvey", ['Tin Whistle', 'Vocal Harmonies'], 350)
        self.blit_credits("Colm Rogan", ['Lead Guitar'], 350)


        self.blit_information(50, 3000, 500, 110, 'Thanks for playing')
        self.blit_image('ruins.jpg')
        self.blit_image('behemoth.jpg')
        self.blit_image('duke.jpg')
        self.blit_image('homeward.jpg')
        self.blit_image('badnews.jpg')
        self.blit_image('pub.jpg')
        self.blit_image('wake2.jpg')
        self.blit_image('burn.jpg')
        self.blit_image('family.jpg')
        self.blit_image('Seifer.jpg')
        self.blit_image('Temple.jpg')
        self.blit_image('turnip.jpg')
        self.blit_image('sexy.jpg')
        self.blit_image('face_turnip.jpg')
        self.blit_image('Tw1.jpg')
        self.blit_image('Sorceror.jpg')
        self.blit_image('hanging.jpg')
        self.blit_image('hung.jpg')

    def update(self, inventory, world, player):
        if self.first_start:
            self.intro()
            self.first_start = False
        if self.back_rect.height > g.ysize:
            self.back_image = pygame.transform.scale( self.back_image,
                                                                (self.back_rect.width*g.ysize/self.back_rect.height,
                                                                self.back_rect.height*g.ysize/self.back_rect.height))
            self.back_rect = self.back_image.get_rect()
        self.back_rect.center = (g.xsize/2, g.ysize/2)
        g.screen.blit(self.back_image, self.back_rect)
        pygame.display.update()
        control_events_menu(self, g.xsize, g.ysize)
        self.exit_menu_on()
        wait(self, 2000)
        self.investigate = False
        while self.menu_on is True:
            if android:
                if android.check_pause():
                    mixer.music.pause()
                    android.wait_for_resume()
                    mixer.music.unpause()
            # Menu Loop
            # passes choices and menu position to menu control
            #self.back_rect.center = (g.xsize/2, g.ysize/2+(g.ysize-500)/2)
            self.back_rect.center = (g.xsize/2, g.ysize/2)
            g.screen.blit(self.back_image, self.back_rect)
            text = Blitted_rect((270, 100), (g.xsize/2 - 145, g.ysize/2-45), self.color)
            Menu.menu_control(
                self,
                self.choices,
                g.xsize/2 - 100,
                g.ysize/2-40,
                self.color)  # Control Menu
            self.exit_menu_on()

            # if we are in itial choices update our choices depending
            if self.investigate and self.index == 0:
                select.play()
                self.investigate = False
                self.menu_on = False
                player.rect.topleft = [g.xsize/2, g.ysize/2]
                world.load_all()
                inventory.load_inventory()
                fade_black(2000)
                pygame.display.flip()
                #wait(self, 3000)
                #fade_out(2000)
                g.mouse = False
                world.load_current_area()
                world.room_change = True

            elif self.investigate and self.index == 1:
                try:
                    self.investigate = False
                    player.rect.topleft = [g.xsize/2, g.ysize/2]
                    world.load_all()
                    inventory.load_game()
                    select.play()
                    world.current_area = pickle.load(
                        open(
                            os.path.join(
                                'data',
                                "save_game_area.p"),
                            "rb"))
                    world.chests = pickle.load(
                        open(
                            os.path.join(
                                'data',
                                "save_game_chests.p"),
                            "rb"))
                    fade_out(2000)
                    world.load_current_area()
                    world.room_change = True
                    self.menu_on = False
                    g.mouse = False
                except:
                    damage.play()

            pygame.display.update()
            pygame.time.wait(50)  # Reduce the cpu load waiting for 50 miliseconds every loop

    def game_over(self, inventory, world, player, interobjects):
        if inventory.health[0] <= 0 and inventory.items[1].quantity > 0:
            player.going = False
            inventory.items[1].quantity -= 1
            inventory.health[0] = inventory.health[1]/2
            dim(200)
            text = TextBox(
                (200,
                 45),
                ((g.xsize-200)/2,
                 (g.ysize-45)/2),
                BLUE,
                fonts[0],
                24)  # Display Equiped!
            text.setText('Used Difibulator')
            if android:
                android.vibrate(0.8)
            pygame.display.flip()
            pygame.time.wait(200)
            revive.play()
            wait(self,1400)
        elif inventory.health[0] <= 0:
            if android:
                android.vibrate(2)
            fade_out(2000)
            player.going = False
            self.back_rect.center = (g.xsize/2, g.ysize/2+55)
            play_music('main.ogg', 0, 1.0)
            text = TextBox(
                (g.xsize - 220,
                 g.ysize-370),
                ((g.xsize - 420)/2,
                 (g.ysize-110)/2),
                BLACK,
                fonts[3],
                63)
            interobjects.boss = False
            text.setTextspace('Game Over', 20)
            pygame.display.update()
            wait(self,3000)
            self.investigate = False
            self.menu_on = True
            player.rect.topleft = [g.xsize/2, g.ysize/2]
            inventory.empty()
            self.rect.topleft = (0, 0)
            self.update(inventory, world, player)

        elif inventory.credits is True:
            inventory.credits = False
            self.role_credits()
            play_music('main.ogg', 0, 1.0)
            self.investigate = False
            self.menu_on = True
            player.rect.topleft = [g.xsize/2, g.ysize/2]
            inventory.empty()
            self.rect.topleft = (0, 0)
            self.update(inventory, world, player)

