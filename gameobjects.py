import pygame
import random
from gamesettings import *


class IDrawableObject():
    def draw(self, screen):
        pass


class ICollidableObject(IDrawableObject):
    def check_collisions(self, player):
        pass


class IMovableObject(ICollidableObject):
    def move(self):
        pass


class PlayerCharacter(IMovableObject):
    def __init__(self, x, y, speed):
        self._picture = pygame.image.load("./data/frog1_alfa.png")
        self._surface = pygame.Surface(
            (self._picture.get_width(), self._picture.get_height()))
        self._rect = self._surface.get_rect(topleft=(x, y))
        self._speed = speed
        self._surface_count = 0
        self._surface_speed = 0
        # self._movetick = 4 #alternative movement mode

    def get_rect(self):
        return self._rect

    def get_standing(self):
        return self._surface_count

    def go_home(self):
        self._rect.update(288, 670, self._rect.width, self._rect.height)
        # self._rect.update(288, 16, self._rect.width, self._rect.height) #cheat

    def surface_count_delta(self, delta):
        self._surface_count += delta

    def surface_speed_delta(self, delta):
        self._surface_speed += delta

    def draw(self, screen):
        screen.blit(self._picture, self._rect)

    def move(self, arrows):
        if self._rect.right < SCREENWIDTH and self._rect.left > 0:
            self._rect.move_ip(self._surface_speed, 0)
        """ alternative movement mode
        self.movetick += 1     
        if self.movetick == 5: 
            self.movetick = 0  
        """ 
        if self._rect.top > self._speed:
            if arrows[0]:
                self._rect.move_ip(0, -self._speed)
                return
        if self._rect.bottom < SCREENHEIGHT - self._speed - 64:
            if arrows[1]:
                self._rect.move_ip(0, self._speed)
                return
        if self._rect.left > self._speed:
            if arrows[2]:
                self._rect.move_ip(-self._speed, 0)
                return
        if self._rect.right < SCREENWIDTH-self._speed:
            if arrows[3]:
                self._rect.move_ip(self._speed, 0)
                return

    def check_collisions(self, player):
        return 0


class Car(IMovableObject):
    def __init__(self, row, offset):
        self._sprite_name = random.choice(
            ["./data/car1.png", "./data/car2.png", "./data/car3.png"])
        self._picture = pygame.image.load(self._sprite_name)
        self._goesLeft = False
        if row % 2 == 0:
            self._goesLeft = True
        if self._goesLeft:
            self._picture = pygame.transform.flip(self._picture, True, False)
        self._surface = pygame.Surface(
            (self._picture.get_width(), self._picture.get_height()))
        self._rect = self._surface.get_rect(
            topleft=(offset*0.5*SCREENWIDTH, 400 + 40 * row))
        self._speed = 1 + row % 3

    def draw(self, surface):
        surface.blit(self._picture, self._rect)

    def move(self):
        if self._goesLeft:
            self._rect.move_ip(-self._speed, 0)
            if self._rect.right < 0:
                self._rect.move_ip(SCREENWIDTH + 80, 0)
        else:
            self._rect.move_ip(self._speed, 0)
            if self._rect.left > SCREENWIDTH + self._rect.width:
                self._rect.move_ip(-SCREENWIDTH - 80, 0)

    def check_collisions(self, player):
        if self._rect.colliderect(player.get_rect()):
            return -1


class House(ICollidableObject):
    def __init__(self, offset):
        self._picture = pygame.image.load("./data/smolfrog.png")
        self._surface = pygame.Surface(
            (self._picture.get_width(), self._picture.get_height()))
        self._rect = self._surface.get_rect(topleft=(72+128*offset, 28))
        self._visible = False

    def draw(self, surface):
        if self._visible == True:
            surface.blit(self._picture, self._rect)

    def check_collisions(self, player):
        if self._visible == False:
            if self._rect.colliderect(player.get_rect()):
                self._visible = True
                return 1
        return 0


class WoodenLog(IMovableObject):
    def __init__(self, size, offset):
        if size == 4:
            self._picture = pygame.image.load("./data/log4x1.png")
            self._surface = pygame.Surface((256, 64))
            self._rect = self._surface.get_rect(
                topleft=(1.5*offset*self._picture.get_width(), 192))
            self._speed = 4
        elif size == 3:
            self._picture = pygame.image.load("./data/log3x1.png")
            self._surface = pygame.Surface((192, 64))
            self._rect = self._surface.get_rect(
                topleft=(1.5*offset*self._picture.get_width(), 64))
            self._speed = 3
        elif size == 2:
            self._picture = pygame.image.load("./data/log2x1.png")
            self._surface = pygame.Surface((128, 64))
            self._rect = self._surface.get_rect(
                topleft=(1.5*offset*self._picture.get_width(), 256))
            self._speed = 1
        self._stood_on = False

    def draw(self, screen):
        screen.blit(self._picture, self._rect)

    def check_collisions(self, player):
        if self._rect.colliderect(player.get_rect()):
            if self._stood_on == False:
                player.surface_count_delta(1)
                player.surface_speed_delta(self._speed)
                self._stood_on = True
        elif self._stood_on == True:
            player.surface_count_delta(-1)
            player.surface_speed_delta(-self._speed)
            self._stood_on = False
        return 0

    def move(self):
        self._rect.move_ip(self._speed, 0)
        if self._rect.left > SCREENWIDTH:
            self._rect.move_ip(-SCREENWIDTH - self._rect.width, 0)


class Manatees(IMovableObject):
    def __init__(self, offset):
        self._pictures = [pygame.image.load("./data/manatees1.png"), pygame.image.load(
            "./data/manatees2.png"), pygame.image.load("./data/manatees3.png"), pygame.image.load("./data/manatees4.png")]
        self._picture = self._pictures[0]
        self._surface = pygame.Surface((256, 64))
        self._rect = self._surface.get_rect(
            topleft=(SCREENWIDTH - 2.15*offset*self._picture.get_width(), 128))
        self._phase_ticks = 0 + 30*offset
        self._submerged = False
        self._stood_on = False
        self._speed = -3.5
        self._submerge_ticks = 60
        self.change_state(ManateeStateFloating())

    def draw(self, screen):
        self._state.draw_handle(screen)

    def check_collisions(self, player):
        return self._state.collision_handle(player)

    def move(self):
        self._rect.move_ip(self._speed, 0)
        if self._rect.right < 0:
            self._rect.move_ip(SCREENWIDTH + self._rect.width, 0)

    def change_state(self, state):
        self._state = state
        self._state.context = self


class ManateeState():
    def draw_handle(self, screen):
        pass
    def collision_handle(self, player):
        pass


class ManateeStateFloating(ManateeState):
    def draw_handle(self, screen):
        screen.blit(self.context._pictures[0], self.context._rect)
    def collision_handle(self, player):
        self.context._phase_ticks += 1
        if self.context._phase_ticks == 2 * self.context._submerge_ticks:
            self.context.change_state(ManateeStateSubmerging1())
        if self.context._rect.colliderect(player.get_rect()):
            if self.context._stood_on == False:
                player.surface_count_delta(1)
                player.surface_speed_delta(self.context._speed)
                self.context._stood_on = True
        elif self.context._stood_on == True:
            player.surface_count_delta(-1)
            player.surface_speed_delta(-self.context._speed)
            self.context._stood_on = False
        return 0


class ManateeStateSubmerging1(ManateeState):
    def draw_handle(self, screen):
        screen.blit(self.context._pictures[1], self.context._rect)
    def collision_handle(self, player):
        self.context._phase_ticks += 1
        if self.context._phase_ticks == 2.5 * self.context._submerge_ticks:
            self.context.change_state(ManateeStateSubmerging2())
        if self.context._rect.colliderect(player.get_rect()):
            if self.context._stood_on == False:
                player.surface_count_delta(1)
                player.surface_speed_delta(self.context._speed)
                self.context._stood_on = True
        elif self.context._stood_on == True:
            player.surface_count_delta(-1)
            player.surface_speed_delta(-self.context._speed)
            self.context._stood_on = False
        return 0


class ManateeStateSubmerging2(ManateeState):
    def draw_handle(self, screen):
        screen.blit(self.context._pictures[2], self.context._rect)
    def collision_handle(self, player):
        self.context._phase_ticks += 1
        if self.context._phase_ticks == 3 * self.context._submerge_ticks:
            self.context.change_state(ManateeStateSubmerged())
        if self.context._rect.colliderect(player.get_rect()):
            if self.context._stood_on == False:
                player.surface_count_delta(1)
                player.surface_speed_delta(self.context._speed)
                self.context._stood_on = True
        elif self.context._stood_on == True:
            player.surface_count_delta(-1)
            player.surface_speed_delta(-self.context._speed)
            self.context._stood_on = False
        return 0


class ManateeStateSubmerged(ManateeState):
    def draw_handle(self, screen):
        screen.blit(self.context._pictures[3], self.context._rect)
    def collision_handle(self, player):
        self.context._phase_ticks += 1
        if self.context._phase_ticks == 4 * self.context._submerge_ticks:
            self.context._phase_ticks = 0
            self.context.change_state(ManateeStateFloating())
        if self.context._stood_on == True:
            player.surface_count_delta(-1)
            player.surface_speed_delta(-self.context._speed)
            self.context._stood_on = False
        return 0


class Water(ICollidableObject):
    def __init__(self):
        self._surface = pygame.Surface((576, 196))
        self._rect = self._surface.get_rect(topleft=(0, 104))

    def check_collisions(self, player):
        if self._rect.colliderect(player.get_rect()) and player.get_standing() == 0:
            return -1
        else:
            return 0

    def draw(self, screen):
        pass


class Background(IDrawableObject):
    def __init__(self):
        self._picture = pygame.image.load("./data/froggerbg.png")

    def draw(self, screen):
        screen.blit(self._picture, (0, 0))


class ScreenObjects():
    def __init__(self, screen, font):
        self._drawable_list = []
        self._movable_list = []
        self._collidable_list = []
        self._screen = screen
        self._font = font
        self._player = None
        self._lives = 4
        self._goals = 0
        self._score = 5000

    def add_drawable(self, object):
        self._drawable_list.append(object)

    def add_collidable(self, object):
        self._collidable_list.append(object)

    def add_movable(self, object):
        self._movable_list.append(object)

    def set_player(self, player):
        self._player = player

    def draw_objects(self):
        for object in [*self._drawable_list, *self._movable_list, *self._collidable_list]:
            object.draw(self._screen)
        self._player.draw(self._screen)
        self.draw_score()

    def draw_score(self):
        pygame.draw.rect(self._screen, (0, 0, 0), (0, 704, SCREENWIDTH, 64), 0)
        text_surface, rect = self._font.render(
            "Lives amount: " + str(self._lives), (255, 255, 255))
        rect = text_surface.get_rect(midtop = (SCREENWIDTH/3, 725))
        self._screen.blit(text_surface, rect)

        text_surface, rect = self._font.render(
            "Score: " + str(self._score), (255, 255, 255))
        rect = text_surface.get_rect(midtop = (2*SCREENWIDTH/3, 725))
        self._screen.blit(text_surface, rect)

        self._score -= 1

    def move_objects(self):
        for object in self._movable_list:
            object.move()

    def collide_objects(self):
        for object in [*self._collidable_list, *self._movable_list]:
            has_collided = object.check_collisions(self._player)
            if has_collided != 0:
                if has_collided == -1:
                    return self.damage_player()
                elif has_collided == 1:
                    return self.reward_player()

    def damage_player(self):
        self._player.go_home()
        self._lives -= 1
        if self._lives == 0:
            return -1
        return None

    def reward_player(self):
        self._player.go_home()
        self._goals += 1
        if self._goals == 4:
            return self._score + 1000 * (self._lives - 1)
        return None