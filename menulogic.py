import pygame
import pygame.freetype
import pygame_menu
import sys
import pickle
from gameobjects import *
from gamesettings import *


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Highscore():
    def __init__(self, score, name):
        self._score = score
        self._name = name

    def __str__(self):
        return str(self._score) + " " + self._name

    def get_score(self):
        return self._score

    def __lt__(self, otherscore):
        return self._score < otherscore.get_score()


class MenuFactory():
    def __init__(self, game):
        self._game = game
        self._theme = self.create_theme()

    def create_start_menu(self):
        menu = pygame_menu.Menu(
            '', SCREENWIDTH, SCREENHEIGHT, theme=self._theme)
        menu.add.button('Play', self._game.start_game)
        menu.add.button('Highscores', self._game.scoreboard_menu)
        menu.add.button('Exit', pygame_menu.events.EXIT)
        return menu

    def create_end_menu(self, lastscore):
        menu = pygame_menu.Menu(
            '', SCREENWIDTH, SCREENHEIGHT, theme=self._theme)
        menu.add.button('Play again', self._game.start_game)
        menu.add.button('Highscores', self._game.scoreboard_menu)
        menu.add.button('Exit', pygame_menu.events.EXIT)
        menu.add.label("Your score: " + str(lastscore), font_color=(255, 255, 255))
        return menu

    def create_save_menu(self, scorelist):
        menu = pygame_menu.Menu('', SCREENWIDTH, SCREENHEIGHT,
                                theme=self._theme, onclose=pygame_menu.events.BACK)
        menu.add.text_input(
            'Name: ', onreturn=self._game.save_record, scoreboard=scorelist)
        menu.add.button('Return', menu.close)
        return menu

    def create_scoreboard_menu(self, scorelist):
        menu = pygame_menu.Menu('', SCREENWIDTH, SCREENHEIGHT,
                                theme=self._theme, onclose=pygame_menu.events.BACK)
        for highscore in scorelist:
            menu.add.label(highscore, font_color=(255, 255, 255))
        menu.add.button('Return', menu.close)
        return menu

    def create_theme(self):
        mytheme = pygame_menu.Theme()
        mytheme.background_color = pygame_menu.BaseImage(
            image_path="./data/endscreen.png",
            drawing_mode=pygame_menu.baseimage.IMAGE_MODE_SIMPLE
        )
        mytheme.widget_font = pygame_menu.font.FONT_MUNRO
        mytheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
        return mytheme


class ScoreboardCaretaker():
    def __init__(self, game):
        self._game = game
    
    def restore(self):
        try:
            with open('./highscores/highscores.pkl', 'rb') as f:
                scoreboard = pickle.load(f)
        except FileNotFoundError:
            scoreboard = []
            for _ in range(5):
                scoreboard.append(Highscore(0, "None"))
        return scoreboard

    def create(self, scoreboard):
        with open('./highscores/highscores.pkl', 'wb') as f:
            pickle.dump(scoreboard, f)


class Game(metaclass = Singleton):
    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self._font = pygame.freetype.Font("./data/Connection.otf", 24)
        pygame.display.set_caption("Frogger Game")
        self._icon = pygame.image.load("./data/frog1.png")
        pygame.display.set_icon(self._icon)
        self._clock = pygame.time.Clock()
        self._caretaker = ScoreboardCaretaker(self)
        self._menu_creator = MenuFactory(self)
        self.start_menu()

    def start_menu(self):
        start_menu = self._menu_creator.create_start_menu()
        start_menu.mainloop(self._screen)

    def start_game(self):
        self._objects_list = ScreenObjects(self._screen, self._font)
        self._player = PlayerCharacter(267, 657, 4)
        self._lastscore = 0
        self.populate_screen()
        self.game_loop()

    def populate_screen(self):
        self._objects_list.set_player(self._player)
        self._objects_list.add_drawable(self._player)
        self._objects_list.add_drawable(Background())
        self._objects_list.add_collidable(Water())
        for i in range(4):
            self._objects_list.add_collidable(House(i))
        for i in range(5):
            for j in range(2):
                self._objects_list.add_movable(Car(i, j))
        for i in range(2, 5):
            for j in range(2):
                self._objects_list.add_movable(WoodenLog(i, j))
        for i in range(2):
            self._objects_list.add_movable(Manatees(i))

    def game_loop(self):
        running = True
        while running:
            running = self.game_tick()
            self._clock.tick(FPS)
            pygame.display.update()
        self.game_end()

    def game_tick(self):
        self._objects_list.move_objects()
        self._objects_list.draw_objects()
        player_collisions = self._objects_list.collide_objects()
        if player_collisions != None:
            if player_collisions == -1:
                return False
            else:
                self._lastscore = player_collisions
                return False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_game()
        keys = pygame.key.get_pressed()
        arrows = [keys[pygame.K_UP], keys[pygame.K_DOWN],
                  keys[pygame.K_LEFT], keys[pygame.K_RIGHT]]
        self._player.move(arrows)
        return True

    def game_end(self):
        end_menu = self._menu_creator.create_end_menu(self._lastscore)
        scoreboard = self.load_scoreboard()
        if scoreboard[-1].get_score() < self._lastscore:
            end_menu.add.label("A new record!", font_color=(255, 255, 255))
            end_menu.add.button(
                'Save record', self.save_record_screen, scoreboard)
        end_menu.mainloop(self._screen)

    def scoreboard_menu(self):
        scoreboard_screen = self._menu_creator.create_scoreboard_menu(
            self.load_scoreboard())
        scoreboard_screen.mainloop(self._screen)

    def load_scoreboard(self):
        return self._caretaker.restore()

    def save_record_screen(self, scoreboard):
        save_menu = self._menu_creator.create_save_menu(scoreboard)
        save_menu.mainloop(self._screen)

    def save_record(self, name, scoreboard):
        scoreboard[4] = Highscore(self._lastscore, name)
        scoreboard.sort(reverse=True)
        self._caretaker.create(scoreboard)
        self.start_menu()

    def exit_game(self):
        pygame.display.quit()
        pygame.quit()
        sys.exit()
