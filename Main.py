"""В данной игре необходимо играть за рыцаря, который путешествует 
по многоэтажному подземелью, борется с врагами и собирает сокровища.

"""
"""Сделано дополнительно:
* Перемещение героя зажатием клавиш
* Союзник и эффект IDDQD добавлен
* Миникарта реализована (красная точка - герой, объекты не выведены специально ("туман"))
* Добавлен противник Маг
* Реализована логика схватки
* Самостоятельное перемещение противников
"""

from numpy import True_
import pygame
import os

from pygame import key
import Objects
import ScreenEngine
import Logic
import Service


SCREEN_DIM = (800, 600)

pygame.init()
gameDisplay = pygame.display.set_mode(SCREEN_DIM)
pygame.display.set_caption("MyRPG")
KEYBOARD_CONTROL = True
clock = pygame.time.Clock()

if not KEYBOARD_CONTROL:
    import numpy as np
    answer = np.zeros(4, dtype=float)

base_stats = {
    "strength": 20,
    "endurance": 20,
    "intelligence": 5,
    "luck": 5
}

hero = engine = drawer = iteration = None # инициализирование неопределенных глобальных переменных

def create_game(sprite_size, is_new):
    """основной движок игры"""
    global hero, engine, drawer, iteration
    if is_new:
        hero = Objects.Hero(base_stats, Service.create_sprite(
            os.path.join("texture", "Hero.png"), sprite_size))
        engine = Logic.GameEngine()
        Service.service_init(sprite_size)
        Service.reload_game(engine, hero)
        # with ScreenEngine as SE: #???
        SE = ScreenEngine
        # создаем цепочку вложенных полотен для отображения игрового процесса
        drawer = SE.GameSurface((640, 480), pygame.SRCALPHA, (0, 480),
                                SE.ProgressBar((640, 120), (640, 0),
                                                SE.InfoWindow((160, 480), (640, 480),
                                                            SE.MiniGameSurface((160,120), pygame.SRCALPHA, (50, 50),
                                                                            SE.HelpWindow((700, 500), pygame.SRCALPHA, (150, 150),
                                                                                            SE.EndWindow((500, 300), pygame.SRCALPHA, (0, 0),
                                                                                                            SE.ScreenHandle((0, 0)
                                                                                                            )))))))
    else:
        engine.sprite_size = sprite_size
        hero.sprite = Service.create_sprite(
            os.path.join("texture", "Hero.png"), sprite_size)
        Service.service_init(sprite_size, False)

    Logic.GameEngine.sprite_size = sprite_size
    Logic.GameEngine.mini_size = mini_size

    drawer.connect_engine(engine)

    iteration = 0


size = 60 # default: 60
mini_size = 4
create_game(size, True)

move = False

while engine.working:
    # move = False
    if KEYBOARD_CONTROL:
        if engine.game_process:
            # обрабатываем как однократное нажатие, так и зажатие стрелок управления
            keys = pygame.key.get_pressed()
            if move == False and engine.show_end == False:
                if keys[pygame.K_UP]:
                    engine.move_up()
                    iteration += 1
                    move = True
                elif keys[pygame.K_DOWN]:
                    engine.move_down()
                    iteration += 1
                    move = True
                elif keys[pygame.K_RIGHT]:
                    engine.move_right()
                    iteration += 1
                    move = True
                elif keys[pygame.K_LEFT]:
                    engine.move_left()
                    iteration += 1
                    move = True
            else: move = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    engine.show_help = not engine.show_help
                if event.key == pygame.K_m:
                    ScreenEngine.tuman = not ScreenEngine.tuman
                if event.key == pygame.K_KP_PLUS:
                    if size <= 100: size = size + 1
                    create_game(size, False)
                if event.key == pygame.K_KP_MINUS:
                    if size >= 17: size = size - 1
                    create_game(size, False)
                if event.key == pygame.K_r:
                    create_game(size, True)
                if event.key == pygame.K_ESCAPE:
                    engine.working = False
                if engine.game_process and move == False and engine.show_end == False:
                    if event.key == pygame.K_UP:
                        engine.move_up()
                        iteration += 1
                        move = True
                        pygame.time.wait(200)                        
                    elif event.key == pygame.K_DOWN:
                        engine.move_down()
                        iteration += 1
                        move = True
                        pygame.time.wait(200)
                    elif event.key == pygame.K_LEFT:
                        engine.move_left()
                        iteration += 1
                        move = True
                        # clock.tick(5)
                        pygame.time.wait(200)
                    elif event.key == pygame.K_RIGHT:
                        engine.move_right()
                        iteration += 1
                        move = True
                        pygame.time.wait(200)
                else:
                    if event.key == pygame.K_RETURN:
                        create_game()
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.working = False
        if engine.game_process:
            actions = [
                engine.move_right,
                engine.move_left,
                engine.move_up,
                engine.move_down,
            ]
            answer = np.random.randint(0, 100, 4)
            prev_score = engine.score
            move = actions[np.argmax(answer)]()
            state = pygame.surfarray.array3d(gameDisplay)
            reward = engine.score - prev_score
            print(reward)
        else:
            create_game()


    gameDisplay.blit(drawer, (0, 0))  
    drawer.draw(gameDisplay)
    pygame.display.update()

    if hero.hp <= 0:
        engine.show_end = True

    if move == True: clock.tick(3) # слегка замедлим передвижение героя при зажатой клавише

pygame.display.quit()
pygame.quit()
exit(0)
