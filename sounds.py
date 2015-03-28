import os
try:
    import pygame.mixer as mixer
    mixer.init()
except ImportError:
    import android.mixer as mixer

select = mixer.Sound(os.path.join('data', 'sounds', 'select.ogg'))
select2 = mixer.Sound(os.path.join('data', 'sounds', 'select2.ogg'))
attack = mixer.Sound(os.path.join('data', 'sounds', 'attack.ogg'))
ability = mixer.Sound(os.path.join('data', 'sounds', 'ability.ogg'))
damage = mixer.Sound(os.path.join('data', 'sounds', 'damage.ogg'))
enemy_dead = mixer.Sound(os.path.join('data', 'sounds', 'enemy_dead.ogg'))
shock = mixer.Sound(os.path.join('data', 'sounds', 'revive.ogg'))
boss_victory = mixer.Sound(os.path.join('data', 'sounds', 'boss_victory.ogg'))
revive = mixer.Sound(os.path.join('data', 'sounds', 'smack.ogg'))
gasp = mixer.Sound(os.path.join('data', 'sounds', 'gasp.ogg'))
levelup = mixer.Sound(os.path.join('data', 'sounds', 'levelup.ogg'))
openc = mixer.Sound(os.path.join('data', 'sounds', 'open.ogg'))
buckfast = mixer.Sound(os.path.join('data', 'sounds', 'buckfast.ogg'))
equip = mixer.Sound(os.path.join('data', 'sounds', 'equip.ogg'))
explosion = mixer.Sound(os.path.join('data', 'sounds', 'explosion.ogg'))
boss_defeated = mixer.Sound(os.path.join('data', 'sounds', 'boss_defeated.ogg'))
