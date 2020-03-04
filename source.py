import pygame
from random import randint
from random import seed
from enum import Enum

seed()

pygame.init()


class Terrain(Enum):
    Ocean = 0
    Coast = 1
    Grass = 2
    Lake = 3
    LakeFront = 4
    Gravel = 5

#
# COLOR VALUES
C_GRASS = (0, 128, 0)
C_WATER = (0, 0, 128)
C_BEACH = (255, 210, 127)
C_GRAVEL = (0, 100, 0)

# MAP DIMENSIONS
width = 200
height = 200
cellSize = 5

win = pygame.display.set_mode((height * cellSize, width * cellSize))

win.fill(C_WATER)


class WorldMap:

    terrain = [[Terrain.Ocean for x in range(0, width)] for y in range(0, height)]

    LAND_VOLUME = .80
    LANDMASS = int(width * height * LAND_VOLUME)
    BEACH_THRESHOLD = .1

    coast = []
    dryCoast = []
    inland = []
    lake = []
    lakeFront = []

    WEIGHT_COAST = 1000    # Chance of selecting a piece of beach and growing a landmass
    WEIGHT_OCEAN = 3        # Chance of selecting a piece of ocean and creating a new landmass
    WEIGHT_INLAND = 0       # Chance of selecting a piece of inland and creating a new lakefront
    WEIGHT_LAKEFRONT = 10    # Chance of selecting a piece of lakefront and growing a lake
    WEIGHT_DRYCOAST = 10     # Chance of drying up a beach

    TOTAL_WEIGHT = WEIGHT_COAST + WEIGHT_INLAND + WEIGHT_LAKEFRONT + WEIGHT_OCEAN + WEIGHT_DRYCOAST

    def landLocked(self, c):
        if self.terrain[(c[0] + 1) % height][c[1]] == Terrain.Ocean:
            return False
        if self.terrain[(c[0] - 1) % height][c[1]] == Terrain.Ocean:
            return False
        if self.terrain[c[0]][(c[1] + 1) % width] == Terrain.Ocean:
            return False
        if self.terrain[c[0]][(c[1] - 1) % width] == Terrain.Ocean:
            return False
        return True

    def growLand(self):     # REQUIRES coast != []
        if len(self.coast) == 0:
            print("ERROR: No land to grow")
            return
        index = randint(0, len(self.coast) - 1)
        selection = self.coast[index]  # select a set of coastal coordinates
#       print(selection)
        x = randint(-1, 1)
        y = randint(-1, 1)

        if self.terrain[(selection[0] + y) % height][(selection[1] + x) % width] == Terrain.Ocean:  # if we hit water

            self.terrain[(selection[0] + y) % height][(selection[1] + x) % width] = Terrain.Coast  # make it coast
            self.coast.append(
                ((selection[0] + y) % height, (selection[1] + x) % width))  # add new coast to coast list

            for c in self.coast:  # a tad inefficient but it works - for now.
                if self.landLocked(c):
                    self.inland.append(c)
                    self.coast.remove(c)
                    self.terrain[c[0]][c[1]] = Terrain.Grass

        # else:
        #     print("selected type", self.terrain[(selection[0] + y) % height][(selection[1] + x) % width])
            # self.growLand()  # try again

        self.render()  # debug
        pygame.display.update()  # debug

    def newLand(self):
        candidateY = randint(0, height - 1)
        candidateX = randint(0, width - 1)
        if self.terrain[candidateY][candidateX] == Terrain.Ocean:
            self.terrain[candidateY][candidateX] = Terrain.Coast
            self.coast.append((candidateY, candidateX))
        else:
            self.newLand()  # try again

    def dryBeach(self):

        for g in self.dryCoast:  # a tad inefficient but it works - for now.
            if self.landLocked(g):
                self.dryCoast.remove(g)
                self.inland.append(g)
                self.terrain[g[0]][g[1]] = Terrain.Grass

        print(len(self.coast))
        print(len(self.dryCoast) * self.BEACH_THRESHOLD * 2)
        if len(self.dryCoast) * self.BEACH_THRESHOLD * 2 > len(self.coast):
            return
        dried = self.coast[randint(0, len(self.coast) - 1)]
        self.coast.remove(dried)
        self.terrain[dried[0]][dried[1]] = Terrain.Gravel
        self.dryCoast.append(dried)



        toDry = []
        for g in self.dryCoast:
            for y in range(-1, 1):
                for x in range(-1, 1):
                    if self.terrain[(g[0] + y) % height][(g[1] + x) % width] == Terrain.Coast:
                        for c in self.coast:
                            if c == ((g[0] + y) % height, (g[1] + x) % width):
                                self.coast.remove(c)
                                self.terrain[(g[0] + y) % height][(g[1] + x) % width] = Terrain.Gravel
                                toDry.append(c)
        if len(toDry) > 0:
            self.dryCoast.extend(toDry)

    def generate(self):
        coast_ocean = 0 + self.WEIGHT_COAST
        ocean_inland = coast_ocean + self.WEIGHT_OCEAN
        inland_lakefront = ocean_inland + self.WEIGHT_INLAND
        lakefront_drybeach = inland_lakefront + self.WEIGHT_DRYCOAST

        self.newLand()  # need at least one island to start
        for i in range(0, self.LANDMASS - 1):
            roll = randint(1, self.TOTAL_WEIGHT)
            if 0 < roll <= coast_ocean:
                self.growLand()
            if coast_ocean < roll <= ocean_inland:
                print("new land")
                self.newLand()
            if ocean_inland < roll <= inland_lakefront:
                print("new land")
                self.newLand()
            if inland_lakefront < roll <= lakefront_drybeach:
                self.growLand()
            if lakefront_drybeach < roll <= self.TOTAL_WEIGHT:
                self.dryBeach()
                print("drying beach")

    def render(self):
        for x in self.inland:
            pygame.draw.rect(win, C_GRASS, (x[0] * cellSize, x[1] * cellSize, cellSize, cellSize))
        for x in self.coast:
            pygame.draw.rect(win, C_BEACH, (x[0] * cellSize, x[1] * cellSize, cellSize, cellSize))
        for x in self.dryCoast:
            pygame.draw.rect(win, C_GRAVEL, (x[0] * cellSize, x[1] * cellSize, cellSize, cellSize))


world = WorldMap()
world.generate()
world.render()
run = True

while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)

    pygame.display.update()

# world = [[False for x in range(0, width)] for y in range(0, height)]
#
# worldSize = 5000
#
# landmass = 0
# changes = 0
# run = True
#
# while run:
#
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             exit(0)
#
#     if landmass < worldSize:
#         selectH = randint(0, height - 1)
#         selectW = randint(0, width - 1)
#         if world[selectH][selectW]:
#             for i in range(-2, 2):
#                 for j in range(-2, 2):
#                     if 0 <= selectH + i <= height - 1 and 0 <= selectW + j <= width - 1:
#                         if not world[selectH + i][selectW + j]:
#                             world[selectH + i][selectW + j] = True
#                             landmass += 1
#                             changes += 1
#         else:
#             if randint(0, 20000) == 1:
#                 world[selectH][selectW] = True
#                 landmass += 1
#                 changes += 1
#     if changes > 5000 or landmass >= worldSize:
#         for y in range(0, height):
#             for x in range(width):
#                 if world[y][x] == 1:
#                     pygame.draw.rect(win, C_GRASS, (y * cellSize, x * cellSize, cellSize, cellSize))
#
#         pygame.display.update()
#         changes = 0
#
