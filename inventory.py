import pygame
import pickle
import os.path
import globals as g
from sounds import select2, select, buckfast, levelup, equip
from text_box import TextBox
from controls import space_loop, dim
from constants import *
from parse import load_items, load_key_items, load_equipment, load_jpg
from menus import Menu
try:
    import android
    android.init()
except ImportError:
    android = None

try:
    import pygame.mixer as mixer
except ImportError:
    import mixer

class Item(object):

    """Items that can be used in the game"""

    def __init__(self, name):
        self.name = name
        self.quantity = 0  # How many of the item do we have
        self.string = "String"  # String describing the item
        self.posses = False  # Just here so that all item types have attribute posses

    def set_item(self, array):
        self.quantity = array[1]
        self.string = array[2]

    def use_item(self, inventory):
        if self.name == 'Buckfast':
            # if health is less than half use item
            if inventory.health[0] <= inventory.health[1]/2:
                buckfast.play()
                inventory.health[0] = inventory.health[1]
                text = TextBox(
                    (165, 42), (410, 100), (20, 20, 200), fonts[0], 24)  # Display Game Saved!
                text.setText('HP Restored')
                self.quantity -= 1
            else:
                text = TextBox(
                    (200, 85), (410, 100), (20, 20, 200), fonts[0], 24)  # Display Game Saved!
                text.setText('HP must be less than half')

        elif self.name == 'Difibulator':
            text = TextBox(
                (200, 85), (410, 130), (20, 20, 200), fonts[0], 24)  # Display Game Saved!
            text.setText('Revives Norman from death')

        pygame.display.update()     # Blit Game Saved
        pygame.time.wait(800)

              # write code for what happens -- healed


class Equipment(object):

    """Used for weapon armor and accessory classes"""

    def __init__(self, name):
        self.name = name
        self.posses = False  # Does the inventory contain the item
        self.equiped = False  # Is it equiped
        self.power = 0  # the strength of the equipment
        self.string = "string"  # string describing the equipment(currently unused)

    def set_attributes(self, array):
        # Sets attributes from the list of weapon attributes
        self.posses = bool(array[1])
        self.equiped = array[2]
        self.power = array[3]


class Weapon(Equipment):

    """Used for weapons"""

    def __init__(self, name):
        Equipment.__init__(self, name)

    def set_attributes(self, array):
        Equipment.set_attributes(self, array)


class Armor(Equipment):

    """Used for armor"""

    def __init__(self, name):
        Equipment.__init__(self, name)

    def set_attributes(self, array):
        Equipment.set_attributes(self, array)


class Accessory(Equipment):

    """Used for accessories"""

    def __init__(self, name):
        Equipment.__init__(self, name)

    def set_attributes(self, array):
        Equipment.set_attributes(self, array)


class Ability(Equipment):

    """Abilities"""

    def __init__(self, name):
        Equipment.__init__(self, name)

    def set_attributes(self, array):
        Equipment.set_attributes(self, array)

    def animate(self, position):
        self.surface = pygame.Surface((2*self.power*12+150, 2*self.power*12+150))
        self.surface.set_colorkey((255, 255, 255))
        self.surface.fill((255, 255, 255))
        pygame.draw.circle(self.surface, (0, 0, 50, 0),
                           (self.power*12+75, self.power*12+75), self.power*12+75, self.power*12)
        self.surface.set_alpha(100)
        g.screen.blit(self.surface, (position[0] - (self.power*12+75),
                                     position[1] - (self.power*12+75)))


class Key_item(object):

    """Used for key items which can be used to drive the story line. When they are investigated in the
    manu they both just display some descriptive text"""

    def __init__(self, name):
        self.name = name
        self.posses = False  # Is the item in the inventory
        self.string = "String"  # Tring describing the key item to be blitted

    def set_item(self, array):
        self.posses = array[1]
        self.string = array[2]

    def investigated(self):
        text = TextBox(
            (370, 75), (25, 150), RED, fonts[0], 20)
        text.setText(self.string)
        self.investigate = False
        space_loop(self)


class Stat(Item):

    """Stats inherit the item class as they have the same basic format
    Name some quantity and a string"""

    def __init__(self, name):
        Item.__init__(self, name)

    def set_stat(self, array):
        Item.set_item(self, array)

    def investigated(self):
        text = TextBox(
            (370, 75), (25, 150), RED, fonts[0], 20)
        text.setText(self.string)
        self.investigate = False
        space_loop(self)


class Inventory(object):

    """This is th inventory itself which collects together all of the different items
    and has a number of functions used to control how the inventory is displayed in the menu"""

    def __init__(self):
        self.weapons = []
        self.armors = []
        self.accessories = []
        self.items = []
        self.abilities = []         # Abilities have not been used yet
        self.keyitems = []
        # Stats are currently stored in a dictionary
        self.slots = []
        self.stats = []
        # The initial inventory choices in the game menu
        self.menu_choices = ['Items', 'Weapons', 'Armour', 'Accessories', 'Abilities',
                             'Stats', 'Key Items', 'Save Game']
        # Dictionary with the lists of items corresponding to each menu
        # entry
        self.dictionary = {
            'Weapons': self.weapons,
            'Items': self.items,
            'Armour': self.armors,
            'Accessories': self.accessories,
            'Key Items': self.keyitems,
            'Abilities': self.abilities,
            'Stats': self.stats,
            'Save Game': self.slots}
        self.health = [364, 364]    # The players health
        self.weapon = None          # currently equiped weapon armor and accessory
        self.armor = None
        self.accessory = None
        self.ability = None
        self.moneys = 2000
        self.confidence = 0         # Set upon loading the inventory
        self.attack = 0            # Same
        self.defence = 0            # Same
        self.all_items = []         # List of all items, used for updating inventory
        self.new_choices = []       # These are the new choices for the menu if an menu us selected
        self.menu_strings = []      # These are the strings of the choices to be passed to the menu
        self.exp = 18               # Normans EXP
        self.save_list = []
        self.counter = 0
        self.credits = False  # used to role credits

    def load_inventory(self):
        """Loads up the inventory from the files in the Inventory folder"""
        # Load up arrays of the items
        weapons = load_equipment(os.path.join('data', 'Inventory', 'Weapons'))
        armors = load_equipment(os.path.join('data', 'Inventory', 'Armors'))
        accessories = load_equipment(os.path.join('data', 'Inventory', 'Accessories'))
        abilities = load_equipment(os.path.join('data', 'Inventory', 'Abilities'))
        items = load_items(os.path.join('data', 'Inventory', 'Items'))
        key_items = load_key_items(os.path.join('data', 'Inventory', 'Key_Items'))
        stats = load_items(
            os.path.join(
                'data',
                'Inventory',
                'Stats'))  # Loads the same as Key Items
        # Dictionaries used for making instances of each item object dictionaried to the names
        dict_weapons = {}
        dict_armors = {}
        dict_accessories = {}
        dict_abilities = {}
        dict_items = {}
        dict_keyitems = {}
        dict_stats = {}
        dict_abilities = {}
        for item in items:
            # load up items
            dict_items[item[0]] = Item(item[0])  # make an instance of the object
            dict_items[item[0]].set_item(item)
            self.items.append(dict_items[item[0]])  # add it to the item

        for stat in stats:
            # load up stats
            dict_stats[stat[0]] = Stat(stat[0])  # make an instance of the object
            dict_stats[stat[0]].set_stat(stat)
            self.stats.append(dict_stats[stat[0]])  # add it to the stats

        for key_item in key_items:
            # load up key items, see above
            dict_keyitems[key_item[0]] = Key_item(key_item[0])
            dict_keyitems[key_item[0]].set_item(key_item)
            self.keyitems.append(dict_keyitems[key_item[0]])

        for weapon in weapons:
            # Load up the weapons
            # we make an instance of the object which is dictionaried to the objects name weapon[0]
            dict_weapons[weapon[0]] = Weapon(weapon[0])         # Make an Instance of the object
            dict_weapons[weapon[0]].set_attributes(weapon)      # set its attributes from the file
            self.weapons.append(
                dict_weapons[
                    weapon[0]])        # add the weapon to the list weapons
            if dict_weapons[weapon[0]].equiped is True:         # if the weapon equiped set attack
                self.weapon = dict_weapons[weapon[0]]
                self.attack = self.stats[4].quantity + self.weapon.power  # stats[4] is will power

        for armor in armors:
            # See weapon loading above
            dict_armors[armor[0]] = Armor(armor[0])
            dict_armors[armor[0]].set_attributes(armor)
            self.armors.append(dict_armors[armor[0]])
            if dict_armors[armor[0]].equiped is True:
                self.armor = dict_armors[armor[0]]
                self.defence = self.stats[3].quantity + self.armor.power   # stats[3] is tubbernous

        for accessory in accessories:
            # See weapon loading above
            dict_accessories[accessory[0]] = Accessory(accessory[0])
            dict_accessories[accessory[0]].set_attributes(accessory)
            self.accessories.append(dict_accessories[accessory[0]])
            if dict_accessories[accessory[0]].equiped is True:
                self.accessory = dict_accessories[accessory[0]]
                self.confidence = self.stats[2].quantity + self.accessory.power

        for ability in abilities:
            # See weapon loading above
            dict_abilities[ability[0]] = Ability(ability[0])
            dict_abilities[ability[0]].set_attributes(ability)
            self.abilities.append(dict_abilities[ability[0]])
            if dict_abilities[ability[0]].equiped is True:
                self.ability = dict_abilities[ability[0]]

        # Make the list of all the items
        self.all_items = (self.items + self.weapons + self.armors + self.accessories +
                          self.abilities + self.keyitems)

    def empty(self):
        self.items = []
        self.abilities = []
        self.accessories = []
        self.armors = []
        self.weapons = []
        self.stats = []
        self.keyitems = []
        self.all_items = []
        self.health = [564, 564]
        self.dictionary = {
            'Weapons': self.weapons,
            'Items': self.items,
            'Armor': self.armors,
            'Accessories': self.accessories,
            'Key Items': self.keyitems,
            'Abilities': self.abilities,
            'Stats': self.stats,
            'Save Game': self.slots}

    def update_inventory(self, item):
        """ When a chest is opened or an item is recieved update the inventory accordingly"""
        for entry in self.all_items:
            # Walk through all items
            self.found = False    # used to keep track of weather item is found
            # updates if item is armor weapon accessory or keyitem
            if ((entry.name == item and (type(entry).__name__ == 'Weapon' or
                                         type(entry).__name__ == 'Accessory' or
                                         type(entry).__name__ == 'Armor')) or
                    (entry.name == item and type(entry).__name__ == 'Key_item')):
                entry.posses = True
                self.found = True
                break
            # updates if item is item
            elif entry.name == item and type(entry).__name__ == 'Item':
                entry.quantity += 1
                self.found = True

        if self.found is False:
            # if Item is still not found check if its money which is a string like "100 Moneys"
            try:
                is_money = item.split()
                if is_money[1] == 'Moneys':
                    self.moneys += int(is_money[0])

            # If its doesn't update return an error
            except:
                print 'oops inventory not updated, check item string'

    def update_equipment(self):
        """Used to update attack etc when a new weapon is equiped"""
        for a in self.weapons:
            if a.equiped is True:
                self.weapon = a
                self.attack = self.stats[4].quantity + self.weapon.power
                break

        for a in self.armors:
            if a.equiped is True:
                self.armor = a
                self.defence = self.stats[3].quantity + self.armor.power
                break

        for a in self.accessories:
            if a.equiped is True:
                self.accessory = a
                self.confidence = self.stats[2].quantity + self.accessory.power
                break

        for a in self.abilities:
            if a.equiped is True:
                self.ability = a
                break

    def level_up(self):
        if self.exp <= 0:
            self.counter += 1
            self.exp = 30 + 50*self.counter + 5*self.counter ^ 2
            self.stats[0].quantity += 1
            self.stats[2].quantity += 2
            self.stats[3].quantity += 2
            self.stats[4].quantity += 2
            self.stats[5].quantity -= 2
            self.health[1] = self.health[1] + self.health[1]/6
            self.health[0] += (self.health[1] - self.health[0])/4
            self.attack = self.stats[4].quantity + self.weapon.power
            self.defence = self.stats[3].quantity + self.armor.power
            self.confidence = self.stats[2].quantity + self.accessory.power
            dim(190)
            text = TextBox(
                (190,
                 60),
                ((g.xsize-180)/2,
                 (g.ysize-60)/2),
                GREEN,
                fonts[3],
                30)  # Display Equiped!
            text.setText('LEVEL UP')
            if android:
                android.vibrate(0.6)
            levelup.play()
            pygame.display.update()
            pygame.time.wait(2000)
            if self.stats[0].quantity % 3 == 0:
                for ability in self.abilities:
                    if ability.posses != True:
                        ability.posses = True
                        text = TextBox(
                            (290,
                             50),
                            ((g.xsize-290)/2,
                             (g.ysize-190)/2),
                            BLUE,
                            fonts[3],
                            28)  # Display Equiped!
                        text.setText('Learned: '+ability.name)
                        levelup.play()
                        pygame.display.update()
                        pygame.time.wait(2000)
                        break

    def make_choices(self, index):
        """ For the menu we need a list of strings to pass to the Menu object
        We also need a list of the objects so that we can interact and change them
        depending on the selection"""
        self.menu_strings = []  # List of strings for menu
        self.new_choices = []   # List of objects for performing some changes to the objects
        for a in self.dictionary[self.menu_choices[index]]:
            if type(a).__name__ == 'Item' and a.quantity > 0:
                # If its an item and we have one or more add it to the list
                self.menu_strings.append(str(a.quantity) + ' ' + a.name)
                self.new_choices.append(a)

            elif type(a).__name__ == 'Stat':
                # if its a stat add it to thelist with its number
                self.menu_strings.append(a.name + ':  '+str(a.quantity))
                self.new_choices.append(a)

            elif a.posses is True:
                # If its a weapon, armor, accessory or key item add it to the list if we posses it
                self.menu_strings.append(a.name)
                self.new_choices.append(a)

    def save_game(self):
        self.save_list = []
        self.save_list.append(self.items)
        self.save_list.append(self.armors)
        self.save_list.append(self.weapons)
        self.save_list.append(self.accessories)
        self.save_list.append(self.abilities)
        self.save_list.append(self.stats)
        self.save_list.append(self.keyitems)
        self.save_list.append(self.health)
        self.save_list.append(self.exp)
        pickle.dump(
            self.save_list,
            open(os.path.join('data',
                              "save_game_inventory.p"),
                 "wb"),
            protocol=-
            1)  # Save the inventory

    def load_game(self):
        self.save_list = pickle.load(open(os.path.join('data', "save_game_inventory.p"), "rb"))
        self.items = self.save_list[0]
        self.armors = self.save_list[1]
        self.weapons = self.save_list[2]
        self.accessories = self.save_list[3]
        self.abilities = self.save_list[4]
        self.stats = self.save_list[5]
        self.keyitems = self.save_list[6]
        self.health = self.save_list[7]
        self.exp = self.save_list[8]
        self.all_items = (self.items + self.weapons + self.armors + self.accessories +
                          self.abilities + self.keyitems)
        self.dictionary = {
            'Weapons': self.weapons,
            'Items': self.items,
            'Armour': self.armors,
            'Accessories': self.accessories,
            'Key Items': self.keyitems,
            'Abilities': self.abilities,
            'Stats': self.stats,
            'Save Game': self.slots}
        self.update_equipment()


class Inventory_Menu(Menu):

    """This is the Inventory Menu. It inherits the Menu class which controls how
    the list of strings are displayed and the navigation between different entries in the menu.
    It also displays various other information like health, location, Money and a nice picture of
    the character. It Runs essentially as a sub game loop which is entered if the player presses
    the menu butten "z", which also exits or moves back up one menu """

    def __init__(self, color, inventory):
        # INitiate the menu inheritance
        Menu.__init__(self, fonts[0], 20)
        # Main game menu which displays inventory
        self.color = color
        self.investigate = False   # used for investigating items
        self.initial_choices = inventory.menu_choices  # initial menu options
        self.picture = load_jpg(
            os.path.join(
                'data',
                'player',
                'player.jpg'))  # Nice drawing of player
        self.picture_rect = self.picture.get_rect()
        self.picture_rect.top = 37                  # Position it in the top corner
        self.heading = 'Menu'                       # The heading
        self.backround = pygame.Surface((240, 480))  # sets backround surface
        self.backround.fill(color)
        self.backrect = self.backround.get_rect()
        self.backrect.topleft = (
            400,
            0)  # positions on the right hand side of the screen
        self.choices = self.initial_choices  # Set choices to be initial choices
        # Used to collect the objects associated with the choices
        self.choices_ob = []

    def blit_equipment(self, inventory):
        """When armor accessories or weapons is selected we want to blit the current
        Equiped Items to the screen with a headine 'Equiped'"""
        text = TextBox((240, 40), (0, 40), self.color, fonts[0], 24)  # Heading
        text.setText('Equiped')
        # finds which weapon is equipped and diplays it
        text = TextBox((150, 35), (0, 80), self.color, fonts[0], 20)   # Weapon
        text.setText(inventory.weapon.name)
        text = TextBox((90, 35), (150, 80), self.color, fonts[0], 20)
        text.setText('Atk'+' '+str(inventory.attack))       # Attack strngth

        # finds which armor is equiped and dipla
        text = TextBox((150, 35), (0, 115), self.color, fonts[0], 20)  # Armor
        text.setText(inventory.armor.name)
        text = TextBox((90, 35), (150, 115), self.color, fonts[0], 20)  # Defence
        text.setText('Def'+' '+str(inventory.defence))

        # finds wgich accessory is equipped and displays it

        text = TextBox((150, 35), (0, 150), self.color, fonts[0], 20)  # Accessory
        text.setText(inventory.accessory.name)
        text = TextBox((90, 35), (150, 150), self.color, fonts[0], 20)  # Confidence
        text.setText('Cnf'+' '+str(inventory.confidence))

        text = TextBox((240, 35), (0, 185), self.color, fonts[0], 20)  # Accessory
        text.setText('Ability: ' + inventory.ability.name)
        text = TextBox((240, 35), (0, 220), self.color, fonts[0], 20)  # Accessory
        text.setText('Ability range: '+str(inventory.ability.power))

    def blit_backround(self, inventory, area):
        """Blits various backround information to the screen. This includes the heading,
        the current loaction, Health, Moneys"""
        if self.choices == self.initial_choices:
            g.screen.fill(self.color)
            # Blit the player picture only if we are in the initial choices screen
            g.screen.blit(self.picture, self.picture_rect)
        # Blits heading, health, moneys, area.name and backround to the screen
        text = TextBox((400, 40), (0, 0), self.color, fonts[0], 26)
        text.setText(self.heading)
        text = TextBox((400, 40), (0, g.ysize-40), self.color, fonts[0], 24)
        text.setText(
            'Health' + ' ' + str(inventory.health[0]) + '/' +
            str(inventory.health[1]))
        text = TextBox((400, 40), (0, g.ysize-80), self.color, fonts[0], 24)
        text.setText('Location : '+area.menu_name)
        g.screen.blit(self.backround, self.backrect)
        money = TextBox((180, 30), (450, g.ysize-40), self.color, fonts[0], 24)
        money.setText('Moneys'+' '+str(inventory.moneys))

    def menu_select(self, inventory, area):
        """If we investigate one of the main menu choices this updates the menu to
        the new set of choices, be it armor items etx"""
        self.investigate = False
        self.touched = False
        # Firstly if we choose save game we have to save the game
        if self.index == 7:
            select.play()
            text = TextBox(
                (165, 45), (410, 300), (200, 20, 20), fonts[0], 24)  # Display Game Saved!
            text.setText('Game Saved!')
            pygame.display.update()     # Blit Game Saved
            inventory.save_game()
            pickle.dump(
                area.name,
                open(
                    os.path.join(
                        'data',
                        "save_game_area.p"),
                    "wb"))  # Save the area
            pickle.dump(
                area.chests,
                open(
                    os.path.join(
                        'data',
                        "save_game_chests.p"),
                    "wb"))  # Save the state of chests
            pygame.time.wait(1200)

        else:
            select2.play()
            pygame.time.wait(500)
            inventory.make_choices(self.index)  # Make the new choices from the inventory
            self.heading = self.choices[self.index]  # change heading
            self.choices = inventory.menu_strings  # change choices
            self.choices_ob = inventory.new_choices  # Load objects

            # if we choose equipment this displays equiped items
            if 5 > self.index > 0:
                # Equipment is any of the entries with index 1,2 or 3
                self.blit_equipment(inventory)  # Blit equipment

            self.index = 0  # resets selection to zero

    def equipment_select(self, inventory):
        """If we select a pice of equipment this equips it and updates the players attack
        defence and confidence stats"""
        self.investigate = False
        for a in self.choices_ob:
            # First unequip all others
            a.equiped = False
        equip.play()
        self.choices_ob[self.index].equiped = True  # Equip item
        inventory.update_equipment()                # update inventory
        self.blit_equipment(inventory)              # Blit new equipment
        text = TextBox(
            (120, 45), (450, 200), (100, 100, 100), fonts[0], 24)  # Display Equiped!
        text.setText('Equiped!')
        pygame.display.update()     # Blit equiped! to the screen and then wait for 0.6 seconds
        pygame.time.wait(600)
        self.investigate = False    # required to exit space loop

    def update(self, player, inventory, area):
        """This is essentially a sub game loop that runs and when the player enters the menu
        It essentially pauses the main game and starts this loop"""

        while player.menu:
            if android:
                if android.check_pause():
                    mixer.music.pause()
                    android.wait_for_resume()
                    mixer.music.unpause()
            """Menu Loop"""
            time = pygame.time.get_ticks()
            self.blit_backround(inventory, area)
            Menu.menu_control(self, self.choices, 440, 10, self.color)  # Control Menu
            # if we are in itial choices update our choices depending
            if self.investigate and self.choices == self.initial_choices:
                self.menu_select(inventory, area)
                self.index = 0
                self.touched = False

            # If a piece of equipment is selected: equips it and updates displayed equiped items
            elif ((self.investigate and type(self.choices_ob[0]).__name__ == 'Armor')
                  or (self.investigate and type(self.choices_ob[0]).__name__ == 'Accessory')
                  or (self.investigate and type(self.choices_ob[0]).__name__ == 'Ability')
                  or (self.investigate and type(self.choices_ob[0]).__name__ == 'Weapon')):
                self.equipment_select(inventory)

            # If we select a key item or Stat blit info about it
            elif self.investigate and (type(self.choices_ob[0]).__name__ == 'Key_item' or
                                       type(self.choices_ob[0]).__name__ == 'Stat'):
                # Blit info about item to screen then when exited blit background
                self.choices_ob[self.index].investigated()
                self.investigate = False
                g.screen.blit(self.picture, self.picture_rect)

            # If we select a item use the item
            elif self.investigate and type(self.choices_ob[0]).__name__ == 'Item':
                # Use the item and then update the item list
                self.choices_ob[self.index].use_item(inventory)
                inventory.make_choices(0)
                self.choices = inventory.menu_strings  # change choices
                self.choices_ob = inventory.new_choices  # Load objects
                self.investigate = False

            if self.menu:
                # If the menu button is pressed move back up one menu or exit
                # menu
                self.index = 0

                # exits back to game
                if self.choices == self.initial_choices:
                    self.choices == self.initial_choices
                    self.menu = False
                    player.menu = False
                # Or move back to starting menu
                else:
                    self.heading = 'Menu'
                    self.choices = self.initial_choices
                    self.menu = False

            # updates display
            pygame.display.update()
            pygame.time.wait(50)  # Reduce the cpu load waiting for 50 miliseconds every loop
