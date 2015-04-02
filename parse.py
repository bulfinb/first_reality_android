import pygame.image
import os
import globals as g
from constants import direction
"""functions for parsing text files used for various game objects
Including npc's enemies chests and hopefully map files too   """

try:
    import pygame.mixer as mixer
    mixer.init()
except ImportError:
    import mixer

def parse_txt_files(filename):
    # parse / delimeted files and write to array for npc
    lines = []
    data = []
    f = open(filename)
    for line in f:
        lines.append(line)

    for l in lines:
        # divides lines into strings / and writes them to the array data
        l = l.strip().split("/")
        data.append(l)
    return data


def load_npc_array(filename):
    data = parse_txt_files(filename)
    data[0] = data[0][0]          # num
    data[1] = int(data[1][0])     # moving
    data[2] = int(data[2][0])     # facing
    data[3] = int(data[3][0])     # speed
    data[4][0] = int(data[4][0])  # position
    data[4][1] = int(data[4][1])
    return data


def load_text_array(filename):
    data = parse_txt_files(filename)
    data[0] = int(data[0][0])          # name
    data[1] = int(data[1][0])  # font
    data[2][0] = int(data[2][0])  # position
    data[2][1] = int(data[2][1])
    return data


def load_enemy_array(filename):
    data = parse_txt_files(filename)
    data[0] = data[0][0]          # name
    data[1] = int(data[1][0])     # moving
    data[2] = int(data[2][0])     # health
    data[3] = int(data[3][0])     # strength
    data[4] = int(data[4][0])     # speed
    data[5][0] = int(data[5][0])  # position
    data[5][1] = int(data[5][1])
    data[6] = data[6][0]
    return data


def load_chest_array(filename):
    data = parse_txt_files(filename)
    data[0] = int(data[0][0])  # number
    data[1][0] = int(data[1][0])
    data[1][1] = int(data[1][1])
    data[2] = data[2][0]
    return data


def load_story_array(filename):
    data = parse_txt_files(filename)
    data[0] = data[0][0]  # number
    data[1][0] = int(data[1][0])
    data[1][1] = int(data[1][1])
    data[2] = data[2][0]
    data[3] = data[3]
    data[4][1] = int(data[4][1])
    return data


def load_tile_table(filename, x_sections, y_sections):
    # Breaks a table of nine images up into individuals. FOr Npc's and enemies
    image = pygame.image.load(filename).convert_alpha()
    image_width, image_height = image.get_size()
    tile_table = []
    for tile_x in range(0, x_sections):
        line = []
        tile_table.append(line)
        for tile_y in range(0, y_sections):
            rect = (
                tile_x *
                image_width /
                float(x_sections),
                tile_y *
                image_height /
                y_sections,
                image_width /
                float(x_sections),
                image_height /
                y_sections)
            line.append(image.subsurface(rect))
    return tile_table


def load_area(filename):
    data = parse_txt_files(filename)
    data[0] = str(data[0][0])
    data[1] = int(data[1][0])
    data[2][0] = int(data[2][0])  # position
    data[2][1] = int(data[2][1])
    data[3][1] = int(data[3][1])
    return data


def load_doors(filename):
    data = parse_txt_files(filename)
    for i in range(0, len(data)-1):
        data[i+1][0] = int(data[i+1][0])
        data[i+1][1] = int(data[i+1][1])
        data[i+1][2] = int(data[i+1][2])
        data[i+1][3] = direction[data[i+1][3]]
    return data


def load_equipment(filename):
    data = parse_txt_files(filename)
    for a in data:
        a[1] = bool(int(a[1]))
        a[2] = bool(int(a[2]))
        a[3] = int(a[3])
    return data


def load_items(filename):
    data = parse_txt_files(filename)
    for a in data:
        a[1] = int(a[1])
    return data


def load_key_items(filename):
    data = parse_txt_files(filename)
    for a in data:
        a[1] = bool(int(a[1]))
    return data


def load_png(filename):
    return pygame.image.load(filename).convert_alpha()


def load_jpg(filename):
    return pygame.image.load(filename).convert()


def play_music(filename, time, volume):
    g.current_song = os.path.join('data', 'music', filename)
    mixer.music.load(os.path.join('data', 'music', filename))
    mixer.music.set_volume(volume)
    mixer.music.play(-1)
    if g.current_area != 'Tower0':
        mixer.music.queue(os.path.join('data', 'music', filename))
        mixer.music.queue(os.path.join('data', 'music', filename))

