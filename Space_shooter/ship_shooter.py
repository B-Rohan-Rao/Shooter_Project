import pygame
import os
import time
import random
pygame.font.init()      #Initializing font in pygame module.

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE SHOOTER")

# loading images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# player ship
YELLOW_PLAYER_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))



class Lasers:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask= pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img, (self.x, self.y))

    def move(self,vel):
        self.y += vel
            
    def offscreen(self,height):
        return not(self.y <= height and self.y >= 0)
    
    def collision(self,obj):
        return collide(self,obj)


class Ship:             #This is a general class, we are going to inherit from it and basically not use it
    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None   #This two lines helps in drawing the images.
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.offscreen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser= Lasers(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    # methods to get the height and width of the ship image
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_PLAYER_SHIP    #Therefore the two parameters with none in it has beeen defined.
        self.laser_img = YELLOW_LASER  #Creating a mask... a mask creates a  picture perfect collisions
        self.mask = pygame.mask.from_surface(self.ship_img)  #It means that take the surface that is the ship image and create a mask. mask tells us where pixels are and where they are not so that when we do a collision we know that we have hit it.
        self.max_heath = health    #This tells that whatever health we start with, it is going to be tha max health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.offscreen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self,window):
        pygame.draw.rect(window, (255,0,0),(self.x, self.y+self.ship_img.get_height() + 10, self.ship_img.get_width(),10))
        pygame.draw.rect(window, (0,255,0),(self.x, self.y+self.ship_img.get_height() + 10, self.ship_img.get_width()*(self.health/self.max_heath), 10))     
        #Mathematical equation to get the percentage of health that we are on resulting in the remaining health and that will be the width of the green rect.

    def draw(self,window):
        super().draw(window)
        self.healthbar(window)

class Enemy(Ship):
    # here we will create a dictionary that can understandthe colors as we will pass the colors like a string.so dictionary can understand
    COLOR_MAP={
                "red":(RED_SPACE_SHIP,RED_LASER),
                "green":(GREEN_SPACE_SHIP,GREEN_LASER),
                "blue":(BLUE_SPACE_SHIP,BLUE_LASER)
                }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser= Lasers(self.x-20,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x    #This will tell us the distance from object 1 to object 2 
    offset_y = obj2.y - obj1.y    #This will tell us the distance from object 1 to object 2
    return obj1.mask.overlap(obj2.mask, (offset_x,offset_y))!= None


def main():
    run = True
    FPS = 50
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

#Here we are creating a batch of enemies at random spots that will increse as the level gets on incresing.
    enemies = []
    wave_length = 5
    enemy_vel = 1


    #Defining the vekocity of the movement of the speed.
    player_vel = 5      #defining the speed with which the player can move.
    laser_vel = 9
    # creating the ship position
    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost=False
    lost_count=0
    
    def redraw_window():
        '''as we can see that this function is inside another function: def maun(),we can treat this like a regular function but only when we are in this function.ir also helps in keeping the logics separate as it is very easy to understand and will not mixed up with the rest of the logics'''
        WIN.blit(BG, (0, 0))
        # Draw text
        lives_label = main_font.render(f"Lives:{lives}", 1, (255, 255, 255)) #this will render the text in the comicsans font in white color
        level_label = main_font.render(f"Level:{level}", 1, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)    #The playership is being drawn in the main window of

        if lost:
            lost_label =  lost_font.render("You lost!!", 1, (255,255,255))
            WIN.blit(lost_label,(WIDTH/2-lost_label.get_width()/2, 350))   #This will blit the you lost messege at the center of the screen using WIDTH/2-lost_label.get_width()/2 this expression

        pygame.display.update()   #this will keep the screen updated.
         
        
    while run:
        clock.tick(FPS)
        redraw_window()

        if lives<=0  or player.health<=0:   
            lost=True
            lost_count += 1

            if lost:                #This loop will make sure that if the counting crosses a certein limit, then the game will stop or (else)it will keep running.
                if lost_count > FPS*3:  # This means if we have crossed our 3 second timer, quit the game.
                    run = False
                else:                   #This makes sure that when the messege is being displayed on the screen we will not be able to do any of the movement
                    continue

        if len(enemies)==0:  #The basic idea here is hat if the length in enemy list is 0 then the level will increse
            level+=1         #and with that the wave length of enimy will also increase.
            wave_length+=5
            for i in range(wave_length):                                     #We are swamping the enimies here
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red","blue","green"]))
                #We are just creating a batch of enimes that get swamped at the random positions that is and randomeandrange create the range between where the enimies can get swamped.
                # If the level is too high, there may be a case where there are too many enimies in such a short range of y..i.e.-1500 to -100 so to prevent it, we can actually wrie -1500*len\5 or something like that.
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: #left 
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  #Right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:    #Up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15< HEIGHT:  #Down
             player.y += player_vel
             #code after writing and statement is used to restrict the player to go offscrean
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:           #The enemy will start moving.  [:] is the copy so that it does not modify the list we are looping through 
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:   #shooting of enemy. 2*60 will give it the range in which it can shoot 2 times in each seconds or 60FPS
                enemy.shoot()

            if collide(enemy,player):
                player.health -= 10
                enemies.remove (enemy)
            elif enemy.y + enemy.get_height()>HEIGHT:   #The condion of checking the enemy off the screen will not be checked if it collides with player
                lives -= 1
                enemies.remove(enemy)               #This removes the enemy from the list when they creoss the bottom of the screen
            
            
        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 25)
    run=True
    while run:
        WIN.blit(BG, (0, 0))
        title_label= title_font.render("PRESS THE MOUSE TO BEGIN...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
            if event.type == pygame.MOUSEBUTTONDOWN: #It says that if we press the main any mouse buttn then enter the main loop and start the game again.
                main()

    pygame.quit()


main_menu()