import Service
import random


class GameEngine:
    objects = []
    map = None
    hero = None
    level = -1
    working = True
    mini_size = 4
    subscribers = set()
    score = 0.
    game_process = True
    show_help = False
    show_end = False

    def subscribe(self, obj):
        self.subscribers.add(obj)

    def unsubscribe(self, obj):
        if obj in self.subscribers:
            self.subscribers.remove(obj)

    def notify(self, message):
        """message to InfoWindow"""
        for i in self.subscribers:
            i.update(message)

    # HERO
    def add_hero(self, hero):
        self.hero = hero

    def interact(self):
        for obj in self.objects:
            if list(obj.position) == self.hero.position:
                self.delete_object(obj)
                obj.interact(self, self.hero)

    # MOVEMENT
    def move_up(self):
        self.score -= 0.02
        if self.map[self.hero.position[1] - 1][self.hero.position[0]] == Service.wall:
            return
        self.hero.position[1] -= 1
        self.interact()
        self.npc_move()
        self.interact()

    def move_down(self):
        self.score -= 0.02
        if self.map[self.hero.position[1] + 1][self.hero.position[0]] == Service.wall:
            return
        self.hero.position[1] += 1
        self.interact()
        self.npc_move()
        self.interact()

    def move_left(self):
        self.score -= 0.02
        if self.map[self.hero.position[1]][self.hero.position[0] - 1] == Service.wall:
            return
        self.hero.position[0] -= 1
        self.interact()
        self.npc_move()
        self.interact()

    def move_right(self):
        self.score -= 0.02
        if self.map[self.hero.position[1]][self.hero.position[0] + 1] == Service.wall:
            return
        self.hero.position[0] += 1
        self.interact()
        self.npc_move()
        self.interact()

    # MAP
    def load_map(self, game_map):
        self.map = game_map

    # OBJECTS
    def add_object(self, obj):
        self.objects.append(obj)

    def add_objects(self, objects):
        self.objects.extend(objects)

    def delete_object(self, obj):
        self.objects.remove(obj)

    def npc_move(self):
        for npc in self.objects:
            if str(npc.__class__) == "<class 'Objects.Enemy'>":
                # enemy move
                direct = random.randrange(0, 5, 1)
                x = npc.position[0]
                y = npc.position[1]
                if direct == 1:
                    if self.map[y][x+1] != Service.wall: x +=1
                elif direct == 2:
                    if self.map[y][x-1] != Service.wall: x -=1
                elif direct == 3:
                    if self.map[y+1][x] != Service.wall: y +=1
                elif direct == 4:
                    if self.map[y-1][x] != Service.wall: y -=1
                npc.position = (x, y)
