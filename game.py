import random
import pygame
from eventlistener import Subject, Event
from enum import IntEnum
from color import Color
from itertools import product

class Tile:
    def __init__(self, rect):
        self.o_neighbors = []
        self.d_neighbors = []
        self.rect = rect
        self.is_revealed = False
        self.is_mine = False
        self.is_marked = False
        self.type = 0
        self.nearby_mines = 0
        self.mine_probability = 100

class Game(Subject):
    def __init__(self, grid_width, grid_height, mine_count, clock):
        Subject.__init__(self)
        random.seed()
        self.tiles = []
        self.game_symbols = []
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.mine_count = mine_count
        self.game_timer = clock
        self.elapsed_time = 0
        self.moves = 0
        self.marked_tiles = 0
        self.game_screen = pygame.display.set_mode((100+self.grid_width*25, 100+self.grid_height*25))
        pygame.display.set_caption("Minesweeper")
        self.game_active = True
        self.timer_enabled = False
        self.font_medium = pygame.font.Font(None, 32)
        font_mediumlarge = pygame.font.Font(None, 35)
        font_large = pygame.font.Font(None, 72)
        self.game_symbols.append(self.font_medium.render(" 0", 1, Color.GREY))
        self.game_symbols.append(self.font_medium.render(" 1", 1, Color.BLUE))
        self.game_symbols.append(self.font_medium.render(" 2", 1, Color.GREEN))
        self.game_symbols.append(self.font_medium.render(" 3", 1, Color.RED))
        self.game_symbols.append(self.font_medium.render(" 4", 1, Color.PURPLE))
        self.game_symbols.append(self.font_medium.render(" 5", 1, Color.DARK_RED))
        self.game_symbols.append(self.font_medium.render(" 6", 1, Color.BLUE_GREY))
        self.game_symbols.append(self.font_medium.render(" 7", 1, Color.BLACK))
        self.game_symbols.append(self.font_medium.render(" 8", 1, Color.DARK_PURPLE))
        self.game_symbols.append(font_large.render("*", 1, Color.BLACK))
        self.game_symbols.append(font_mediumlarge.render(" l", 1, Color.BLACK))
        self.game_symbols.append(font_mediumlarge.render(" >", 1, Color.RED))
        self.init_grid()
        self.game_screen.fill(Color.GREY)
        self.draw_tiles()

    def init_grid(self):
        """
        Luo kaksiulotteisen ruudukon annettujen arvojen mukaan ja täyttää ne Tile-objekteilla.
        """
        for x in range(self.grid_width):
            self.tiles.append([])
            for y in range(self.grid_height):
                self.tiles[x].append(Tile(pygame.Rect(50+x*25, 50+y*25, 25, 25)))
        self.assign_neighbors()
        self.place_mines()
        self.count_nearby_mines()

    def place_mines(self):
        """
        Asettaa kentälle miinojal, jokaisella ruudulla on alussa todennäköisyys 100 (1/10 todellinen mahdollisuus) olla miina,
        jokainen vieressä oleva miina puolittaa sen ruudun todennäköisyyden olla miina.
        Esim. ruudulla jolla on 2 naapuroivaa miinaa on 100/2^2 == 25 todennäköisyys, jolloin todellinen
        mahdollisuus olla miina on 1/(110-25) eli 1/85.
        """
        placed_mines = 0
        while (placed_mines < self.mine_count):
            for x, y in product(range(self.grid_width), range(self.grid_height)):
                if random.randint(1, (110-int(self.tiles[x][y].mine_probability))) == 5 and not self.tiles[x][y].is_mine and placed_mines < self.mine_count:
                    for n in self.tiles[x][y].o_neighbors:
                        self.tiles[n[0]][n[1]].mine_probability /= 2
                    for n in self.tiles[x][y].d_neighbors:
                        self.tiles[n[0]][n[1]].mine_probability /= 2
                    self.tiles[x][y].type = 9
                    self.tiles[x][y].is_mine = True
                    placed_mines += 1
    
    def assign_neighbors(self):
        """
        Luo jokaiselle ruudulle listan sen naapureista kaikissa suunnissa.
        """
        for x, y in product(range(self.grid_width), range(self.grid_height)):
            self.tiles[x][y].o_neighbors = self.get_orthogonal_neighbors((x, y))
            self.tiles[x][y].d_neighbors = self.get_diagonal_neighbors((x, y))
            
    def count_nearby_mines(self):
        """
        Laskee ruutuja ympäröivät miinat ja asettaa niiden tyypin miinojen lukumäärän mukaan.
        """
        for x, y in product(range(self.grid_width), range(self.grid_height)):
            current_tile = self.tiles[x][y]
            if not current_tile.is_mine:
                for neighbor in current_tile.o_neighbors:
                    if self.tiles[neighbor[0]][neighbor[1]].is_mine:
                        current_tile.nearby_mines += 1
                for neighbor in current_tile.d_neighbors:
                    if self.tiles[neighbor[0]][neighbor[1]].is_mine:
                        current_tile.nearby_mines += 1
                current_tile.type = current_tile.nearby_mines

    def check_tile(self, mouse_pos):
        """
        Tarkistaa ja avaa kursorin alla olevan ruudun, häviää pelin jos ruutu on miina.
        """
        if self.mouse_inside_grid(mouse_pos):
            if not self.game_active:
                return
            if not self.timer_enabled:
                self.timer_enabled = True
            grid_x = int((mouse_pos[0] - 50) / 25)
            grid_y = int((mouse_pos[1] - 50) / 25)
            current_tile = self.tiles[grid_x][grid_y]
            if not current_tile.is_revealed and not current_tile.is_mine:
                self.moves += 1
            if current_tile.is_mine:
                for x, y in product(range(self.grid_width), range(self.grid_height)):
                    if self.tiles[x][y].is_mine:
                        self.reveal_tile((x, y))
                self.lose_game()
            self.reveal_tile((grid_x, grid_y))
            self.check_victory()
            self.draw_tiles()

    def mark_tile(self, mouse_pos):
        """
        Merkitsee paljastamattoman ruudun, jolloin sen päälle piirretään lippu draw_tiles funktiossa.
        """
        if not self.game_active:
            return
        if not self.timer_enabled:
            self.timer_enabled = True
        if self.mouse_inside_grid(mouse_pos):
            grid_x = int((mouse_pos[0] - 50) / 25)
            grid_y = int((mouse_pos[1] - 50) / 25)
            current_tile = self.tiles[grid_x][grid_y]
            if not current_tile.is_revealed:
                current_tile.is_marked = not current_tile.is_marked
                if current_tile.is_marked:
                    self.marked_tiles += 1
                else:
                    self.marked_tiles -= 1
            self.draw_tiles()

    def mouse_inside_grid(self, mouse_pos):
        """
        Tarkistaa, onko annettu piste kentän rajojen sisällä.
        """
        if mouse_pos[0] > 50 and mouse_pos[0] < (50 + self.grid_width * 25):
            if mouse_pos[1] > 50 and mouse_pos[1] < (50 + self.grid_height * 25):
                return True
        return False

    def reveal_tile(self, pos):
        """
        Paljastaa ruudun pisteessä pos=(x, y), mikäli ruudun tyyppi on 0 (ei miinoja vieressä), paljastaa
        viereisiä ruutuja niin kauan että saavutaan miinakentän rajalle.
        """
        tile = self.tiles[pos[0]][pos[1]]
        if tile.is_revealed or tile.is_marked:
            return
        unrevealed = []
        unrevealed.append(tile)
        while len(unrevealed) > 0:
            cur = unrevealed.pop()
            cur.is_revealed = True
            if cur.type == 0:
                for n in cur.o_neighbors:
                    if not self.tiles[n[0]][n[1]].is_revealed:
                        unrevealed.append(self.tiles[n[0]][n[1]])

    def get_orthogonal_neighbors(self, tile):
        """
        Kokoaa ja palauttaa listan jonkun pisteen (X) viereisistä (pysty- ja sivusuunnassa) pisteistä (O)
        DOD
        OXO
        DOD
        """
        neighbors = []
        if self.valid_tile((tile[0]-1, tile[1])):
            neighbors.append((tile[0]-1, tile[1]))#W
        if self.valid_tile((tile[0], tile[1]-1)):
            neighbors.append((tile[0], tile[1]-1))#N
        if self.valid_tile((tile[0], tile[1]+1)):
            neighbors.append((tile[0], tile[1]+1))#S
        if self.valid_tile((tile[0]+1, tile[1])):
            neighbors.append((tile[0]+1, tile[1]))#E
        return neighbors

    def get_diagonal_neighbors(self, tile):
        """
        Kokoaa ja palauttaa listan jonkun pisteen (X) viereisistä (vinottain) pisteistä  (D)
        DOD
        OXO
        DOD
        """
        neighbors = []
        if self.valid_tile((tile[0]-1, tile[1]-1)):
            neighbors.append((tile[0]-1, tile[1]-1))#NW
        if self.valid_tile((tile[0]-1, tile[1]+1)):
            neighbors.append((tile[0]-1, tile[1]+1))#SW
        if self.valid_tile((tile[0]+1, tile[1]-1)):
            neighbors.append((tile[0]+1, tile[1]-1))#NE
        if self.valid_tile((tile[0]+1, tile[1]+1)):
            neighbors.append((tile[0]+1, tile[1]+1))#SE
        return neighbors

    def valid_tile(self, tile):
        """
        Tarkistaa, onko annettu ruutu kentän sisällä.
        """
        if tile[0] >= 0 and tile[0] < self.grid_width:
            if tile[1] >= 0 and tile[1] < self.grid_height:
                return True
        return False

    def check_victory(self):
        """
        Tarkistaa onko pelaaja voittanut pelin etsimällä paljastamattomia ruutuja, jotka eivät ole miinoja.
        """
        unrevealed_tiles = 0
        for x, y in product(range(self.grid_width), range(self.grid_height)):
            if not self.tiles[x][y].is_mine and not self.tiles[x][y].is_revealed:
                unrevealed_tiles += 1
        if unrevealed_tiles == 0:
            self.win_game()

    def win_game(self):
        """
        Ilmoittaa kuuntelijoille pelin voittamisesta, pysäyttää pelin ja piirtää voittotekstin ylhäälle.
        """
        self.notify_listeners(Event.GAME_WON)
        self.game_active = False
        self.timer_enabled = False
        win_text = self.font_medium.render("You won the game!", 1, Color.GREEN, Color.GREY)
        self.game_screen.blit(win_text, (0, 0))

    def lose_game(self):
        """
        Ilmoittaa kuuntelijoille pelin häviämisestä, pysäyttää pelin ja piirtää häviötekstin ylhäälle.
        """
        self.notify_listeners(Event.GAME_LOST)
        self.game_active = False
        self.timer_enabled = False
        loss_text = self.font_medium.render("You lost the game.", 1, Color.RED, Color.GREY)
        self.game_screen.blit(loss_text, (0, 0))

    def update(self):
        """
        Päivittää ajastimen, piirtää ajan ja merkitsemättömien miinojen määrän.
        """
        if self.timer_enabled:
            self.elapsed_time += self.game_timer.get_time()
            self.time_text = self.font_medium.render(" {} ".format(int(self.elapsed_time / 1000)), 1, Color.BLACK, Color.GREY)
            self.game_screen.blit(self.time_text, (45, 50+self.grid_height*25, 0, 0))
        self.mine_count_text = self.font_medium.render(" {}  ".format(self.mine_count - self.marked_tiles), 1, Color.BLACK, Color.GREY)
        self.game_screen.blit(self.mine_count_text, (20+self.grid_width*25, 50+self.grid_height*25, 0, 0))
        pygame.display.update()

    def draw_tiles(self):
        """
        Piirtää kaikki ruudut, numerot, liput ja mahdolliset miinat.
        """
        for x, y in product(range(self.grid_width), range(self.grid_height)):
            current_tile = self.tiles[x][y]
            if current_tile.is_revealed:
                if current_tile.is_mine:
                    pygame.draw.rect(self.game_screen, Color.RED, current_tile.rect)
                else:
                    pygame.draw.rect(self.game_screen, Color.GREY, current_tile.rect)
                pygame.draw.rect(self.game_screen, Color.BLACK, current_tile.rect, 1)
                if not current_tile.type == 0:
                    self.game_screen.blit(self.game_symbols[current_tile.type], current_tile.rect)
            else:
                pygame.draw.rect(self.game_screen, Color.DARK_GREY, current_tile.rect)
                pygame.draw.rect(self.game_screen, Color.BLACK, current_tile.rect, 1)
                if self.tiles[x][y].is_marked:
                    self.game_screen.blit(self.game_symbols[10], (current_tile.rect[0]-3, current_tile.rect[1]))
                    self.game_screen.blit(self.game_symbols[11], (current_tile.rect[0]+1, current_tile.rect[1]-7))
