from abc import ABC, abstractmethod
import pygame
import random
import math

from ScreenEngine import EndWindow


def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite

class AbstractObject(ABC):

    @abstractmethod
    def __init__(self):
        pass

    def draw(self, display):
        min_x, min_y = display.get_hero_position()
        display.blit(self.sprite, (((self.position[0] - min_x)* display.game_engine.sprite_size),
                           ((self.position[1] - min_y) * display.game_engine.sprite_size)))

class Interactive(ABC):

    @abstractmethod
    def interact(self, engine, hero):
        pass


class Ally(AbstractObject, Interactive):

    def __init__(self, icon, action, position):
        self.sprite = icon
        self.action = action
        self.position = position

    def interact(self, engine, hero):
        self.action(engine, hero)


class Creature(AbstractObject):

    def __init__(self, icon, stats, position):
        self.sprite = icon
        self.stats = stats
        self.position = position
        self.calc_max_HP()
        self.hp = self.max_hp

    def calc_max_HP(self):
        self.max_hp = 5 + self.stats["endurance"] * 2


class Hero(Creature):

    def __init__(self, stats, icon):
        pos = [1, 1]
        self.level = 1
        self.exp = 0
        self.gold = 0
        super().__init__(icon, stats, pos)

    def level_up(self):
        """генератор lelel up"""
        while self.exp >= 100 * (2 ** (self.level - 1)):
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            tmp = self
            while hasattr(tmp, 'base'):
                """сохраняем результат после снятия эффектов"""
                tmp.base.stats["strength"] += 2
                tmp.base.stats["endurance"] += 2
                tmp = tmp.base
            self.calc_max_HP()
            self.hp = self.max_hp
            self.exp -= 100
            yield "level up!"


class Effect(Hero):

    def __init__(self, base):
        self.base = base # декоратор
        self.stats = self.base.stats.copy()
        self.apply_effect()

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @abstractmethod
    def apply_effect(self):
        pass


class Enemy(Creature):
    
    def __init__(self, icon, stats, xp, position, name =""):
        '''переопределяем из-за отличия в присвоении хp'''
        self.exp = xp
        self.name = name
        super().__init__(icon, stats, position)

    def interact(self, engine, hero):
        '''fight with a enemy'''
        engine.notify(f"You were engaged in a fight with a {self.name}")
        while (hero.hp > 0) and (self.hp > 0):

            if hero.stats['endurance']*10 < int(math.log10(hero.stats['endurance'])*1000):
                power = random.randrange(hero.stats['endurance']*10, int(math.log10(hero.stats['endurance'])*1000))/1000
            else: power = random.randrange(int(math.log10(hero.stats['endurance']*1000)), hero.stats['endurance']*10)/1000

            if (random.randrange(0, 15) + 0.5) < math.log10(hero.stats['luck'] + hero.stats['intelligence']):
                power *= math.log10(hero.stats['luck']) + 1
                # engine.notify(f"You've made powershot")
            
            self.hp -= int(hero.stats['strength'] * power)

            if self.hp < 0:
                engine.notify(f"You won battle with a {self.name}")
                hero.exp += self.exp
                while hero.exp >= 100 * (2 ** (hero.level - 1)):
                    try:
                        engine.notify(next(hero.level_up()))
                    except StopIteration:
                        break
                break

            if self.stats['endurance'] < int(math.log10(self.stats['endurance'])*1000):
                power = random.randrange(self.stats['endurance'], int(math.log10(self.stats['endurance'])*1000))/1000
            else: power = random.randrange(int(math.log10(self.stats['endurance']*1000), self.stats['endurance']))/1000

            if (random.randrange(0, 50) + 0.5) < math.log10(self.stats['luck'] + self.stats['intelligence']):
                power *= math.log10(self.stats['luck']) + 1
                # engine.notify(f"You've got powershot")

            hero.hp -= int(self.stats['strength'] * power)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    pygame.time.wait(200)
                    continue
        if hero.hp <= 0:
            engine.notify(f"You were kiled by a {self.name}, sorry")
            # engine.show_end = True


class Berserk(Effect):
    
    def apply_effect(self):
        self.stats['strength'] += 7
        self.stats['endurance'] += 7
        self.stats['intelligence'] -=4
        self.stats['luck'] += 7

class Blessing(Effect):
    
    def apply_effect(self):
        self.stats['strength'] += 4
        self.stats['endurance'] += 4
        self.stats['intelligence'] +=4
        self.stats['luck'] += 4

class Weakness(Effect):
    
    def apply_effect(self):
        self.stats['strength'] -= 4
        self.stats['endurance'] -= 4
        self.stats['intelligence'] -=4
        self.stats['luck'] -= 4

class IDDQD(Effect):

    def apply_effect(self):
        self.hp += 500
        self.max_hp += 500
        self.stats['strength'] += 777
        self.stats['endurance'] += 777
        self.stats['intelligence'] +=777
        self.stats['luck'] += 777