import pygame
from pygame.locals import *
import math
import random                                                           #引入各种库！

class Brick():
    def __init__(self, p_position, p_color):
        self.position = p_position
        self.color = p_color                                           #设置填充颜色   便于程序修改
        self.image = pygame.Surface([brick_width, brick_height])       #将self.img定义为一个方块 （以一个surface对象的形式）
        self.image.fill(self.color)
    
    def draw(self):                                                    #画图函数
        screen.blit(self.image, (self.position[0] * brick_width, self.position[1] * brick_height))

class Block():
    def __init__(self, p_bricks_layout, p_direction, p_color):
        self.bricks_layout = p_bricks_layout
        self.direction = p_direction
        self.cur_layout = self.bricks_layout[self.direction]
        self.position = cur_block_init_position
        self.stopped = False
        self.move_interval = 800
        self.bricks = []
        for (x, y) in self.cur_layout:
            self.bricks.append(Brick(
                (self.position[0] + x, self.position[1] + y),
                p_color))

    def setPosition(self, position):
        self.position = position
        self.refresh_bircks()

    def draw(self):                                                    #同理 Block的画图函数
        for brick in self.bricks:
            brick.draw()

    def isLegal(self, layout, position):                               #判断方块是否超出边界  未超出return true
        (x0, y0) = position
        for (x, y) in layout:
            if x + x0 < 0 or y + y0 < 0 or x + x0 >= field_width or y + y0 >= field_height:
                return False
            if field_map[y + y0][x + x0] != 0:
                return False
        return True

    def left(self):                                                     #向左
        new_position = (self.position[0] - 1, self.position[1])
        if self.isLegal(self.cur_layout, new_position):
            self.position = new_position                                #修改成为新位置
            self.refresh_bircks()                                       #调用refresh函数 修改位置

    def right(self):
        new_position = (self.position[0] + 1, self.position[1])
        if self.isLegal(self.cur_layout, new_position):
            self.position = new_position
            self.refresh_bircks()

    def down(self):
        (x, y) = (self.position[0], self.position[1] + 1)
        while self.isLegal(self.cur_layout, (x, y)):
            self.position = (x, y)
            self.refresh_bircks()
            y += 1

    def refresh_bircks(self):
        for (brick, (x, y)) in zip(self.bricks, self.cur_layout):           #用zip()打包成元组
            brick.position = (self.position[0] + x, self.position[1] + y)

    def stop(self):                                                         #每一个砖块触碰到“底”时停下
        global field_bricks
        global score
        self.stopped = True
        ys = []
        for brick in self.bricks:
            field_bricks.append(brick)
            (x, y) = brick.position
            if y not in ys:
                ys.append(y)                                               #加入这个停下的brick
            field_map[y][x] = 1

        eliminate_count = 0
        ys.sort()
        for y in ys:
            if 0 in field_map[y]:
                continue
            eliminate_count += 1
            for fy in range(y, 0, -1):
                field_map[fy] = field_map[fy - 1][:]
            field_map[0] = [0 for i in range(field_width)]

            tmp_field_bricks = []
            for fb in field_bricks:
                (fx, fy) = fb.position
                if fy < y:
                    fb.position = (fx, fy + 1)
                    tmp_field_bricks.append(fb)
                elif fy > y:
                    tmp_field_bricks.append(fb)
            field_bricks = tmp_field_bricks
        if eliminate_count == 1:                                            #修改得分
            score += 1
        elif eliminate_count == 2:
            score += 2
        elif eliminate_count == 3:
            score += 4
        elif eliminate_count == 4:
            score += 6

    def update(self, time):                                                 #不断刷新 移动砖块
        global last_move
        self.draw()
        if last_move == -1 or time - last_move >= self.move_interval:
            new_position = (self.position[0], self.position[1] + 1)
            if self.isLegal(self.cur_layout, new_position):
                self.position = new_position
                self.refresh_bircks()
                last_move = time
            else:
                self.stop()                                                 #到“底”就停下

    def rotate(self):                                                           #旋转方块
        new_direction = (self.direction + 1) % len(self.bricks_layout)
        new_layout = self.bricks_layout[new_direction]                          #换成新的layout形式
        if not self.isLegal(new_layout, self.position):
            return
        self.direction = new_direction
        self.cur_layout = new_layout
        for (brick, (x, y)) in zip(self.bricks, self.cur_layout):
            brick.position = (self.position[0] + x, self.position[1] + y)
        self.refresh_bircks()
        self.draw()

def drawField():
    for brick in field_bricks:
        brick.draw()

def drawInfoPanel():                                                               #打印游戏信息
    font = pygame.font.Font("myfont.TTF", 18)
    survivedtext = font.render('score: ' + str(score), True, (255, 255, 255))
    textRect = survivedtext.get_rect()
    textRect.topleft = ((field_width + 2) * brick_width, 10)
    screen.blit(survivedtext, textRect)

    next_block.draw()

def drawFrame():                                                                   #绘制游戏边界
    frame_color = pygame.Color(200, 200, 200)
    pygame.draw.line(screen, frame_color, (field_width * brick_width, field_height * brick_height), (field_width * brick_width, 0), 3)

def getBlock():                                                                    #每次随机生成方块（6选1）
    block_type = random.randint(0, 6)
    if block_type == 0:
        return Block(bricks_layout_0, random.randint(0, len(bricks_layout_0) - 1), colors_for_bricks[0])
    elif block_type == 1:
        return Block(bricks_layout_1, random.randint(0, len(bricks_layout_1) - 1), colors_for_bricks[1])
    elif block_type == 2:
        return Block(bricks_layout_2, random.randint(0, len(bricks_layout_2) - 1), colors_for_bricks[2])
    elif block_type == 3:
        return Block(bricks_layout_3, random.randint(0, len(bricks_layout_3) - 1), colors_for_bricks[3])
    elif block_type == 4:
        return Block(bricks_layout_4, random.randint(0, len(bricks_layout_4) - 1), colors_for_bricks[4])
    elif block_type == 5:
        return Block(bricks_layout_5, random.randint(0, len(bricks_layout_5) - 1), colors_for_bricks[5])
    elif block_type == 6:
        return Block(bricks_layout_6, random.randint(0, len(bricks_layout_6) - 1), colors_for_bricks[6])

#预先设置好砖块的形态  这里设置了6种砖块
bricks_layout_0 = (
        ((0, 0), (0, 1), (0, 2), (0, 3)),
        ((0, 1), (1, 1), (2, 1), (3, 1)))
bricks_layout_1 = (
        ((1, 0), (2, 0), (1, 1), (2, 1)),
        )
bricks_layout_2 = (
        ((1, 0), (0, 1), (1, 1), (2, 1)),
        ((0, 1), (1, 0), (1, 1), (1, 2)),
        ((1, 2), (0, 1), (1, 1), (2, 1)),
        ((2, 1), (1, 0), (1, 1), (1, 2)),
        )
bricks_layout_3 = (
        ((0, 1), (1, 1), (1, 0), (2, 0)),
        ((0, 0), (0, 1), (1, 1), (1, 2)),
        )
bricks_layout_4 = (
        ((0, 0), (1, 0), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (0, 1), (0, 2)),
        )
bricks_layout_5 = (
        ((0, 0), (1, 0), (1, 1), (1, 2)),
        ((0, 2), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (1, 2), (2, 2)),
        ((2, 0), (2, 1), (1, 1), (0, 1)),
        )
bricks_layout_6 = (
        ((2, 0), (1, 0), (1, 1), (1, 2)),
        ((0, 0), (0, 1), (1, 1), (2, 1)),
        ((0, 2), (1, 2), (1, 1), (1, 0)),
        ((2, 2), (2, 1), (1, 1), (0, 1)),
        )

colors_for_bricks = (
        pygame.Color(255, 0, 0), pygame.Color(0, 255, 0), pygame.Color(0, 0, 255),
        pygame.Color(100, 100, 100), pygame.Color(120, 200, 0), pygame.Color(100, 0, 200),
        pygame.Color(10, 100, 30))
                                                                                #预先设定好颜色组合，也可以用random 改成随机颜色~
field_width, field_height = 12, 17                                              #同理   预设各种数值
cur_block_init_position = (4, 0)
info_panel_width = 8
next_block_init_position = (field_width + 3, 5)
field_map = [[0 for i in range(field_width)] for i in range(field_height)]

game_over_img = pygame.image.load("gameover.png")                               #为结束图片赋值

running = True
score = 0
brick_width, brick_height = 30, 30
field_bricks = []                                                             #将所有的砖块定义为一个列表，方便循环的时候全部打印

next_block = None
last_move = -1

pygame.init()
screen = pygame.display.set_mode(((field_width + info_panel_width) * brick_width, field_height * brick_height), 0, 32)
pygame.display.set_caption('Tetris')

while running:                                                                #循环游戏  （大循环）
    if next_block == None:
        cur_block = getBlock()
    else:
        cur_block = next_block
        cur_block.setPosition(cur_block_init_position)
    next_block = getBlock()
    next_block.setPosition(next_block_init_position)

    if not cur_block.isLegal(cur_block.cur_layout, cur_block.position):         #若是不在边界内  跳出循环
        cur_block.draw()
        running = False
        continue
    while not cur_block.stopped:
        screen.fill(0)
        drawFrame()
        time = pygame.time.get_ticks()
        cur_block.update(time)
        drawField()
        drawInfoPanel()

        pygame.display.flip()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:                                       #判断是否游戏结束
                pygame.quit()
                exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == K_w or event.key == K_UP:
                    cur_block.rotate()
                    last_move = time
                elif event.key == K_a or event.key == K_LEFT:
                    cur_block.left()
                elif event.key == K_d or event.key == K_RIGHT:
                    cur_block.right()
                elif event.key == K_s or event.key == K_DOWN:
                    cur_block.down()
                    last_move = time - 500

screen.blit(game_over_img, (0, 0))          #显示结束页面
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()
    pygame.display.update()
