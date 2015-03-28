import pygame
import globals as g
from pygame.locals import *
from constants import *
from text_box import TextBox
from collisions import collision_map, collision_ob, collision_room, track_mouse, track_mouse_menu
try:
    import android
    android.init()
except ImportError:
    android = None


def control_events(p, amap, interobjects):
    # Controls the player checks what buttons were pressed and sets the
    # players attributes accordingly
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and abs(p.rect.center[0]-event.pos[0]) < 100 and abs(p.rect.center[1] - event.pos[1]) < 100:
                p.investigate = True
                g.mouse_position = event.pos
        if event.type == pygame.MOUSEMOTION:
            track_mouse(p, event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                g.exit_menu_on = True
            elif event.key == pygame.K_z:
                p.investigate = False
                p.going = False
                p.menu = True


def control_events_menu(p, amap, interobjects):
    # Controls the player checks what buttons were pressed and sets the
    # players attributes accordingly
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and abs(p.rect.center[0]-event.pos[0]) < 200:
                p.touch_ypos = event.pos[1]
                p.touched = True
                p.investigate = True
        elif event.type == pygame.MOUSEMOTION:
            track_mouse_menu(p, event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                p.investigate = False
                p.going = False
                p.menu = True
            elif event.key == pygame.K_z:
                p.investigate = False
                p.going = False
                p.menu = True


def space_loop(p):
    # used to lock computer in sub loop and stop game from running. Example is
    # while talking to npc it stops updates etc
    while p.investigate is False:
        if android:
            if android.check_pause():
                android.wait_for_resume()
        pygame.time.wait(50)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    p.investigate = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    g.exit_menu_on = True


def wait(player, time):
    for i in range(0, time/100):
        pygame.time.wait(100)
        control_events_menu(player, g.xsize, g.ysize)


def control_player(player, inter_objects, amap, current_time):
    # controls the player
    if player.going:
        # For moving player
        # repositions moving player depending on direction of travel
        if player.going == d:
            # if the player map runs off the screen scroll the map
            if (amap.rect.bottom > 5*g.ysize/6 and
                    player.rect.center[1] >= g.ysize/2-64 and player.going == d):
                amap.rect.bottom -= player.speed
                # reposition objects sprites as well as map
                for a in inter_objects:
                    a.rect.bottom -= player.speed
            # otherwise scrolls player
            elif player.going == d:
                player.rect.top += player.speed

            # flips betwee player images
            if current_time % 400 <= 200:
                player.image = player.images[1]
            else:
                player.image = player.images[2]

        elif player.going == u:
            if amap.rect.top < g.ysize/6 and player.rect.center[1] <= g.ysize/2 + 64 and player.going == u:
                amap.rect.bottom += player.speed
                for a in inter_objects:
                    a.rect.bottom += player.speed

            elif player.going == u:
                player.rect.top -= player.speed

            if current_time % 400 <= 200:
                player.image = player.images[4]

            else:
                player.image = player.images[5]

        elif player.going == r:
            if (amap.rect.right > 5*g.xsize/6 and
                    player.rect.center[0] >= g.ysize/2 - 64 and player.going == r):
                amap.rect.right -= player.speed
                for a in inter_objects:
                    a.rect.right -= player.speed

            elif player.going == r:
                player.rect.left += player.speed

            if current_time % 400 <= 200:
                player.image = player.images[6]
            else:
                player.image = player.images[7]

        elif player.going == l:
            if (amap.rect.left < g.xsize/6 and
                    player.rect.center[0] <= g.xsize/2 + 64 and player.going == l):
                amap.rect.right += player.speed
                for a in inter_objects:
                    a.rect.right += player.speed

            elif player.going == l:
                player.rect.left -= player.speed

            if current_time % 400 <= 200:
                player.image = player.images[8]
            else:
                player.image = player.images[9]
        # set the next update time

    elif player.going is False:
        # set the sprite to one of its facing directions
        if player.facing == d:
            player.image = player.images[0]
        elif player.facing == u:
            player.image = player.images[3]
        elif player.facing == r:
            player.image = player.images[6]
        elif player.facing == l:
            player.image = player.images[8]


def player_face_door(player, door):
    if door[3] == d:
        player.facing = u
        player.rect.center = [g.xsize/2, g.ysize/2 + g.ysize/4]
    elif door[3] == u:
        player.facing = d
        player.rect.center = [g.xsize/2, g.ysize/2 - g.ysize/4]
    elif door[3] == r:
        player.rect.center = [g.xsize/2 + g.xsize/4, g.ysize/2+g.ysize/6]
        player.facing = l
    elif door[3] == l:
        player.rect.center = [g.xsize/2 - g.xsize/4, g.ysize/2 + g.ysize/6]
        player.facing = r
    elif door[3] == 5:
        if player.facing == u:
            player.rect.center = [g.xsize/2, g.ysize/2 + g.ysize/4]
        elif player.facing == d:
            player.rect.center = [g.xsize/2, g.ysize/2 - g.ysize/4]
        elif player.facing == l:
            player.rect.center = [g.xsize/2 + g.xsize/4, g.ysize/2]
        elif player.facing == r:
            player.rect.center = [g.xsize/2 - g.xsize/4, g.ysize/2]
        # set the sprite to one of its facing directions
    if player.facing == d:
        player.image = player.images[0]
    elif player.facing == u:
        player.image = player.images[3]
    elif player.facing == r:
        player.image = player.images[6]
    elif player.facing == l:
        player.image = player.images[8]


def control_ob(ob, inter_objects, player, amap, current_time):
    # essentially the same as control player except for ob.s and enemies.

    # if the object is still moving control images and position
    if ob.going:
        if ob.going == d:
            ob.rect.top += ob.speed

            if current_time % (1600/ob.speed) <= 800/ob.speed:
                ob.image = ob.images[0][0]
            else:
                ob.image = ob.images[2][0]

        elif ob.going == u:
            ob.rect.top -= ob.speed
            if current_time % (1600/ob.speed) <= 800/ob.speed:
                ob.image = ob.images[0][3]
            else:
                ob.image = ob.images[2][3]

        elif ob.going == r:
            ob.rect.left += ob.speed

            if current_time % (1600/ob.speed) <= 800/ob.speed:
                ob.image = ob.images[0][2]
            else:
                ob.image = ob.images[2][2]

        elif ob.going == l:
            ob.rect.left -= ob.speed
            if current_time % (1600/ob.speed) <= 800/ob.speed:
                ob.image = ob.images[0][1]
            else:
                ob.image = ob.images[2][1]

    # if it is stopped moving set the facing direction
    elif ob.facing == d:
        ob.image = ob.images[1][0]
    elif ob.facing == u:
        ob.image = ob.images[1][3]
    elif ob.facing == r:
        ob.image = ob.images[1][2]
    elif ob.facing == l:
        ob.image = ob.images[1][1]


def fade_black(time):
    # fade screento black
    fade_in = pygame.Surface((g.xsize, g.ysize))
    fade_in.fill((0, 0, 0))
    fade_in.set_alpha(100)
    for i in range(0, 25):
        fade_in.set_alpha(100-i*4)
        g.screen.blit(fade_in, (0, 0))
        pygame.time.wait(time/25)
        pygame.display.update()


def fade_out(time):
    # fade screento black
    fade_in = pygame.Surface((g.xsize, g.ysize))
    fade_in.fill((0, 0, 0))
    fade_in.set_alpha(100)
    # pygame.mixer.music.fadeout(time)
    for i in range(0, 25):
        fade_in.set_alpha(100-i*4)
        g.screen.blit(fade_in, (0, 0))
        pygame.time.wait(time/25)
        pygame.display.update()


def dim(alpha):
    # dims screen by alpha percent
    fade_in = pygame.Surface((g.xsize, g.ysize))
    fade_in.fill((0, 0, 0))
    fade_in.set_alpha(alpha)
    g.screen.blit(fade_in, (0, 0))
