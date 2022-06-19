import pygame
import collections
# import Service
from Service import wall, floor1, floor2, floor3

colors = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "wooden": (153, 92, 0, 255),
}

tuman = False


class ScreenHandle(pygame.Surface):
    """обработчик цепочки"""
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            self.successor = args[-1]
            self.next_coord = args[-2]
            args = args[:-2]
        else:
            self.successor = None
            self.next_coord = (0, 0)
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"]) # ?

    def draw(self, canvas):
        if self.successor is not None:
            canvas.blit(self.successor, self.next_coord)
            self.successor.draw(canvas)

    def connect_engine(self, engine):
        if self.successor is not None:
            self.successor.connect_engine(engine)



class GameSurface(ScreenHandle):

    def __init__(self, *args, **kwargs):
        self.offset = (0, 0) # смещение полотна
        super().__init__(*args, **kwargs)

    def connect_engine(self, engine): 
        #  save engine and send it to next in chain
        self.game_engine = engine
        super().connect_engine(self.game_engine)

    def draw_hero(self):
        self.game_engine.hero.draw(self)

    def draw_map(self):

        # calculate (min_x,min_y) - left top corner

        min_x, min_y = self.get_hero_position()

        if self.game_engine.map:
            for i in range(len(self.game_engine.map[0]) - min_x):
                for j in range(len(self.game_engine.map) - min_y):
                    self.blit(self.game_engine.map[min_y + j][min_x + i][
                              0], (i * self.game_engine.sprite_size, j * self.game_engine.sprite_size))
        else:
            self.fill(colors["white"])

    def draw_object(self, sprite, coord):
        size = self.game_engine.sprite_size
        # calculate (min_x,min_y) - left top corner
        min_x, min_y = self.get_hero_position()
        self.blit(sprite, ((coord[0] - min_x) * self.game_engine.sprite_size,
                           (coord[1] - min_y) * self.game_engine.sprite_size))

    def draw(self, canvas):
        size = self.game_engine.sprite_size
        min_x, min_y = self.get_hero_position()
       
        self.draw_map()
        for obj in self.game_engine.objects:
            self.blit(obj.sprite[0], ((obj.position[0] - min_x) * self.game_engine.sprite_size,
                                      (obj.position[1] - min_y) * self.game_engine.sprite_size))
        self.draw_hero()

        # draw next surface in chain
        super().draw(canvas)

    def get_hero_position(self):
        """Сдвигаем карту при приближении героя к ее границе"""
        dist = 2
        if ((self.get_width()/self.game_engine.sprite_size) - 
            self.game_engine.hero.position[0] + self.offset[0]) < dist:
            self.offset = (self.offset[0] + 1, self.offset[1])
        elif (self.game_engine.hero.position[0] - self.offset[0]) < dist:
            self.offset = (self.offset[0] - 1, self.offset[1])
        if ((self.get_height()/self.game_engine.sprite_size) - 
            self.game_engine.hero.position[1] + self.offset[1]) < dist:
            self.offset = (self.offset[0], self.offset[1] + 1)
        elif (self.game_engine.hero.position[1] - self.offset[1]) < dist:
            self.offset = (self.offset[0], self.offset[1] - 1)
        return self.offset[0], self.offset[1]

class MiniGameSurface(ScreenHandle):

    def __init__(self, *args, **kwargs):
        self.offset = (0, 0) # смещение полотна
        self.tuman = True
        super().__init__(*args, **kwargs)

    def connect_engine(self, engine):
        # save engine and send it to next in chain
        self.game_engine = engine
        super().connect_engine(self.game_engine)

    def draw_hero(self):
        # self.game_engine.hero.draw(self)
        min_x, min_y = self.get_hero_position()
        pygame.draw.rect(self, (255,0,0), ((self.game_engine.hero.position[0] - min_x) * self.game_engine.mini_size,
                                            (self.game_engine.hero.position[1] - min_y)* self.game_engine.mini_size,
                                            self.game_engine.mini_size, self.game_engine.mini_size), 10, 10)

    def draw_map(self):
        min_x, min_y = self.get_hero_position()
        if self.game_engine.map:
            for i in range(len(self.game_engine.map[0]) - min_x):
                for j in range(len(self.game_engine.map) - min_y):
                    map_paint = self.game_engine.map[min_y + j][min_x + i]
                    if self.game_engine.map[min_y + j][min_x + i] in [floor1, floor2, floor3]:
                        map_paint = floor1
                    self.blit(map_paint[
                              0], (i * self.game_engine.mini_size, j * self.game_engine.mini_size))
        else:
            self.fill(colors["white"])

    def draw_objects(self):
        min_x, min_y = self.get_hero_position()
        for obj in self.game_engine.objects:
            if str(obj.__class__) == "<class 'Objects.Enemy'>": color = (0, 0, 255)
            else: color = (0,255,0)
            pygame.draw.rect(self, color, ((obj.position[0] - min_x) * self.game_engine.mini_size,
                                            (obj.position[1] - min_y)* self.game_engine.mini_size,
                                            self.game_engine.mini_size, self.game_engine.mini_size), 10, 10)

    def draw(self, canvas):
        size = self.game_engine.sprite_size
        min_x, min_y = self.get_hero_position()
        self.draw_map()
        if not tuman:
            self.draw_objects()
        self.draw_hero()

    # draw next surface in chain
        super().draw(canvas)

    def get_hero_position(self):
        # return 0, 0
        """Сдвигаем карту при приближении героя к ее границе"""
        dist = 2
        if ((self.get_width()/self.game_engine.mini_size) - 
            self.game_engine.hero.position[0] + self.offset[0]) < dist:
            self.offset = (self.offset[0] + 1, self.offset[1])
        elif (self.game_engine.hero.position[0] - self.offset[0]) < dist:
            self.offset = (self.offset[0] - 1, self.offset[1])
        if ((self.get_height()/self.game_engine.mini_size) - 
            self.game_engine.hero.position[1] + self.offset[1]) < dist:
            self.offset = (self.offset[0], self.offset[1] + 1)
        elif (self.game_engine.hero.position[1] - self.offset[1]) < dist:
            self.offset = (self.offset[0], self.offset[1] - 1)
        return self.offset[0], self.offset[1]

class ProgressBar(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def connect_engine(self, engine):
        #  save engine and send it to next in chain
        self.engine = engine
        super().connect_engine(self.engine)

    def draw(self, canvas):
        self.fill(colors["wooden"])
    
        pygame.draw.rect(self, colors["black"], (50, 30, 200, 30), 2)
        pygame.draw.rect(self, colors["black"], (50, 70, 200, 30), 2)

        pygame.draw.rect(self, colors[
                         "red"], (50, 30, 200 * self.engine.hero.hp / self.engine.hero.max_hp, 30))
        pygame.draw.rect(self, colors["green"], (50, 70,
                                                 200 * self.engine.hero.exp / (100 * (2**(self.engine.hero.level - 1))), 30))

        font = pygame.font.SysFont("comicsansms", 20)
        self.blit(font.render(f'Hero at {self.engine.hero.position}', True, colors["black"]),
                  (250, 0))

        self.blit(font.render(f'{self.engine.level} floor', True, colors["black"]),
                  (10, 0))

        self.blit(font.render(f'HP', True, colors["black"]),
                  (10, 30))
        self.blit(font.render(f'Exp', True, colors["black"]),
                  (10, 70))

        self.blit(font.render(f'{self.engine.hero.hp}/{self.engine.hero.max_hp}', True, colors["black"]),
                  (60, 30))
        self.blit(font.render(f'{self.engine.hero.exp}/{(100*(2**(self.engine.hero.level-1)))}', True, colors["black"]),
                  (60, 70))

        self.blit(font.render(f'Level', True, colors["black"]),
                  (300, 30))
        self.blit(font.render(f'Gold', True, colors["black"]),
                  (300, 70))

        self.blit(font.render(f'{self.engine.hero.level}', True, colors["black"]),
                  (360, 30))
        self.blit(font.render(f'{self.engine.hero.gold}', True, colors["black"]),
                  (360, 70))

        self.blit(font.render(f'Str', True, colors["black"]),
                  (420, 30))
        self.blit(font.render(f'Luck', True, colors["black"]),
                  (420, 70))

        self.blit(font.render(f'{self.engine.hero.stats["strength"]}', True, colors["black"]),
                  (480, 30))
        self.blit(font.render(f'{self.engine.hero.stats["luck"]}', True, colors["black"]),
                  (480, 70))

        self.blit(font.render(f'SCORE', True, colors["black"]),
                  (550, 30))
        self.blit(font.render(f'{self.engine.score:.4f}', True, colors["black"]),
                  (550, 70))

        # draw next surface in chain
        super().draw(canvas)

class InfoWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.name = "InfoWindow"

    def update(self, value):
        while len(value) > 20:
            space = value.rfind(" ", 0, 20)
            if space <=5: space = 20
            self.data.append(f"> {str(value[0:space])}")
            value = " " + value[space:]
        self.data.append(f"> {str(value)}")
        self.data.append("")

    def draw(self, canvas):
        self.fill(colors["wooden"])
        size = self.get_size()

        font = pygame.font.SysFont("comicsansms", 12)
        for i, text in enumerate(self.data):
            self.blit(font.render(text, True, colors["black"]),
                      (5, 20 + 15 * i))

        # draw next surface in chain
        super().draw(canvas)

    def connect_engine(self, engine):
        # set this class as Observer to engine and send it to next in
        # chain
        engine.subscribe(self)
        self.engine = engine
        super().connect_engine(self.engine)

    def get_size(self):
        return len(self.data) # ?

class HelpWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.data.append([" →", "Move Right"])
        self.data.append([" ←", "Move Left"])
        self.data.append([" ↑ ", "Move Top"])
        self.data.append([" ↓ ", "Move Bottom"])
        self.data.append([" H ", "Show Help"])
        self.data.append(["Num+", "Zoom +"])
        self.data.append(["Num-", "Zoom -"])
        self.data.append([" R ", "Restart Game"])
        self.data.append([" M ", "On/Off Fog"])
        # You can add some help information

    def connect_engine(self, engine):
        # save engine and send it to next in chain
        self.engine = engine
        super().connect_engine(self.engine)

    def draw(self, canvas):
        alpha = 0
        if self.engine.show_help:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        size = self.get_size()
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        if self.engine.show_help:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                              (0, 0), (700, 0), (700, 500), (0, 500)], 5)
            for i, text in enumerate(self.data):
                self.blit(font1.render(text[0], True, ((128, 128, 255))),
                          (50, 50 + 30 * i))
                self.blit(font2.render(text[1], True, ((128, 128, 255))),
                          (150, 50 + 30 * i))

        # draw next surface in chain
        super().draw(canvas)

class EndWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.name = "EndWindow"
        self.data.append(["You were killed"])
        self.data.append(["Please, press R to restart"])
        self.data.append(["Or ESC to exit"])
    
    def connect_engine(self, engine):
        self.engine = engine
        super().connect_engine(self.engine)

    def get_size(self):
        return len(self.data)

    def draw(self, canvas):
        alpha = 0
        if self.engine.show_end:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        size = self.get_size()
        font = pygame.font.SysFont("courier", 24)
        if self.engine.show_end:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                              (0, 0), (500, 0), (500, 300), (0, 300)], 5)
            for i, text in enumerate(self.data):
                self.blit(font.render(text[0], True, ((128, 128, 255))),
                          (50, 50 + 30 * i))
        super().draw(canvas)

        


