from constants import u, d, r, l
import globals as g
"""control various collisions between objects"""


def proximity(ob1, ob2, distance):
    # checks if two objects are within distance d of one another
    if (-(distance + ob1.rect.width/2 + ob2.rect.width/2) < ob1.rect.center[0] - ob2.rect.center[0]
            < (distance + ob1.rect.width/2 + ob2.rect.width/2) and
            -(distance + ob1.rect.height/2 + ob2.rect.height/2) <
            ob1.rect.center[1] - ob2.rect.center[1]
            < (distance + ob1.rect.height/2 + ob2.rect.height/2)):
        return True


def talk_npc(player, npc):
    # if player is close to the npc check
    if proximity(player, npc, 14) is True and abs(g.mouse_position[0] - npc.rect.center[0]) < 74 and abs(g.mouse_position[1] - npc.rect.center[1]) < 74:
        # if ist below on the right or left and if its facing the npc return True
        if player.rect.center[1]+20-npc.rect.bottom > 0 and player.facing == u:
            player.position = d
            return True
        elif npc.rect.left + 20 - player.rect.left > 0 and player.facing == r:
            player.position = l
            return True
        elif player.rect.right - npc.rect.right > 0 and player.facing == l:
            player.position = r
            return True
        elif npc.rect.top + 20 - player.rect.bottom > 0 and player.facing == d:
            player.position = u
            return True


def fight_enemy(player, npc):
    # if ist below on the right or left and if its facing the npc return True
    if player.rect.top+42-npc.rect.bottom > 0 and player.facing == u:
        return True
    elif npc.rect.left + 32 - player.rect.right > 0 and player.facing == r:
        return True
    elif player.rect.left + 32 - npc.rect.right > 0 and player.facing == l:
        return True
    elif npc.rect.top+42 - player.rect.bottom > 0 and player.facing == d:
        return True


def open_chest(player, chest):
    if proximity(player, chest, 20) is True:
        # if ist below on the chest and facing it open it
        if player.rect.center[1]+20-chest.rect.bottom > 0 and player.facing == u:
            return True
        elif chest.rect.left + 20 - player.rect.left > 0 and player.facing == r:
            return True
        elif player.rect.right - chest.rect.right > 0 and player.facing == l:
            return True


def collision_ob(ob1, ob2, gap):
        # returns true if ob1 has collided ob2 used to stop objects from moving
            # uses distance 'gap' to seperat objects. Most seperation in motion dir
    if (ob1.going == u and ob2.rect.right + gap/2 > ob1.rect.left
            and ob1.rect.right > ob2.rect.left-gap/2
            and ob2.rect.top < ob1.rect.top < ob2.rect.bottom+gap):
        return True
    elif (ob1.going == r and ob2.rect.bottom + gap/2 > ob1.rect.top
          and ob1.rect.bottom > ob2.rect.top-gap/2
          and ob2.rect.left-gap < ob1.rect.right < ob2.rect.right):
        return True
    elif (ob1.going == l and ob2.rect.bottom + gap/2 > ob1.rect.top
          and ob1.rect.bottom > ob2.rect.top-gap/2
          and ob2.rect.left < ob1.rect.left < ob2.rect.right+gap):
        return True
    elif (ob1.going == d and ob2.rect.right + gap/2 > ob1.rect.left
          and ob1.rect.right > ob2.rect.left-gap/2
          and ob2.rect.bottom > ob1.rect.bottom > ob2.rect.top-gap):
        return True


def collision_ply(ply, ob, gap):
    # player collisions are slightly different in that goin up player can partly cover an object
    # returns true if ply has collided ob used to stop objects from moving
    # uses distance 'gap' to seperat objects. Most seperation in motion dir
    if (ply.going == u and ob.rect.right + gap/5 > ply.rect.left
            and ply.rect.right > ob.rect.left-gap/5
            and ob.rect.bottom-gap*2 < ply.rect.center[1] < ob.rect.bottom):
        return True
    elif (ply.going == r and ob.rect.center[1] - 2*gap > ply.rect.top
          and ply.rect.bottom > ob.rect.top-gap/5
          and ob.rect.left-gap < ply.rect.right < ob.rect.left+2*gap):
        return True
    elif (ply.going == l and ob.rect.center[1] - 2*gap > ply.rect.top
          and ply.rect.bottom > ob.rect.top-gap/5
          and ob.rect.right-2*gap < ply.rect.left < ob.rect.right+gap):
        return True
    elif (ply.going == d and ob.rect.right + gap/5 > ply.rect.left
          and ply.rect.right > ob.rect.left-gap/5
          and ob.rect.top+gap > ply.rect.bottom > ob.rect.top-gap):
        return True


def collision_room(ob, room, gap):
    # detects collisions with the outside wall of rooms
    # returns true if the ob.rect comes within 'gap' of the outer wall
    # room is th current map room
    if ob.rect.bottom >= room.rect.bottom - gap and ob.going == d:
        return True
    elif ob.rect.top <= room.rect.top+gap and ob.going == u:
        return True
    elif ob.rect.left <= room.rect.left+gap and ob.going == l:
        return True
    elif ob.rect.right >= room.rect.right - gap and ob.going == r:
        return True


def collision_map(ob, room, gap):
    # detect collisions with map backround fil
    if (ob.going == d and
            room.room_map[(-room.rect.topleft[1]+ob.rect.bottom+gap)/64]
            [(-room.rect.topleft[0]+ob.rect.center[0])/64] == '0'):
        return True

    elif (ob.going == u and
          room.room_map[(-room.rect.topleft[1]+ob.rect.center[1]-gap)/64]
          [(-room.rect.topleft[0]+ob.rect.center[0])/64] == '0'):
        return True

    elif (ob.going == r and
          room.room_map[(-room.rect.topleft[1]+ob.rect.center[1])/64]
          [(-room.rect.topleft[0]+ob.rect.right+gap)/64] == '0'):
        return True

    elif (ob.going == l and
          room.room_map[(-room.rect.topleft[1]+ob.rect.center[1])/64]
          [(-room.rect.topleft[0]+ob.rect.left-gap)/64] == '0'):
        return True


def collision_door(player, door, room, gap):
    # detects if a player walks through a door
    if ((player.going == door[3] or player.facing == door[3])
       and door[1] - gap < player.rect.center[0] - room.rect.left < door[1] + gap
       and door[2] - gap < player.rect.center[1] - room.rect.top < door[2] + gap):
        return True


def track(enemy, player):
    sep = [player.rect.left - enemy.rect.left, player.rect.top - enemy.rect.top]
    if abs(sep[0]) >= abs(sep[1]) and sep[0] > 0:
        enemy.going = r
    elif abs(sep[1]) > abs(sep[0]) and sep[1] < 0:
        enemy.going = u
    elif abs(sep[0]) >= abs(sep[1]) and sep[0] < 0:
        enemy.going = l
    elif abs(sep[1]) > abs(sep[0]) and sep[1] > 0:
        enemy.going = d


def track_mouse(player, mouse_pos):
    sep = [- player.rect.center[0] + mouse_pos[0], - player.rect.center[1] + mouse_pos[1]]
    if abs(sep[0])+abs(sep[1]) > g.xsize/10 and mouse_pos[0] != 0:
        if abs(sep[0]) >= abs(sep[1]) and sep[0] > 0:
            player.going = r
            player.facing = r
        elif abs(sep[1]) > abs(sep[0]) and sep[1] < 0:
            player.going = u
            player.facing = u
        elif abs(sep[0]) >= abs(sep[1]) and sep[0] < 0:
            player.going = l
            player.facing = l
        elif abs(sep[1]) > abs(sep[0]) and sep[1] > 0:
            player.going = d
            player.facing = d
        else:
            player.going = False

    else:
        player.going = False


def track_mouse_menu(player, mouse_pos):
    sep = [- player.rect.center[0] + mouse_pos[0], - player.rect.center[1] + mouse_pos[1]]
    if abs(sep[0])+abs(sep[1]) > 44 and mouse_pos[0] != 0:
        if abs(sep[0]) >= abs(sep[1]) and sep[0] > 0:
            player.going = r
            player.facing = r
        elif abs(sep[1]) > abs(sep[0]) and sep[1] < 0:
            player.going = u
            player.facing = u
        elif abs(sep[0]) >= abs(sep[1]) and sep[0] < 0:
            player.going = l
            player.facing = l
        elif abs(sep[1]) > abs(sep[0]) and sep[1] > 0:
            player.going = d
            player.facing = d
        else:
            player.going = False

    else:
        player.going = False
