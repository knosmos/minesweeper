import pygame, pygame.gfxdraw
from random import randint
from pygame.locals import *
pygame.init()

rows = 20
columns = 20

grid = [[0 for i in range(rows)] for i in range(columns)] 
revealed = [[0 for i in range(rows)] for i in range(columns)] 
flags = [[0 for i in range(rows)] for i in range(columns)]

numFlags = 0

screen = pygame.display.set_mode((rows*30,columns*30+60))
pygame.display.set_caption('Minesweeper Prototype')

win = False
lose = False

explodeCtr = 1

try:
    defaultFont = pygame.font.SysFont('verdana',20)
    titleFont = pygame.font.SysFont('cambria',30)
except:
    defaultFont = pygame.font.Font(None,30)
    titleFont = pygame.font.Font(None,50)

def makeBombs(numBombs):
    global grid, rows, columns
    bombsCreated = 0
    while bombsCreated < numBombs:
        x = randint(0, rows-1)
        y = randint(0, columns-1)
        if grid[y][x]==0:
            grid[y][x] = 10
            bombsCreated += 1

def getNumbers():
    global grid
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if grid[y][x] != 10:
                surroundingBombs = 0
                for i in [-1,0,1]:
                    for j in [-1,0,1]:
                        if y+i >= 0 and y+i < len(grid) and x+j >= 0 and x+j < len(grid[y]):
                            if grid[y+i][x+j]==10:
                                surroundingBombs+=1
                grid[y][x]=surroundingBombs

def drawGrid():
    global grid
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if revealed[y][x]:
                if grid[y][x] == 10:
                    c = (255,50,50)
                elif grid[y][x] == 0:
                    c = (255,255,255)
                else:
                    c = (255,255,50)
                text = defaultFont.render(str(grid[y][x]),1,c)
                screen.blit(text,(x*30+5,y*30+5+60))
            else:
                pygame.draw.rect(screen,(100,200,100),(x*30,y*30+60,30,30))
                if flags[y][x]:
                    pygame.draw.rect(screen,(255,50,50),(x*30+5,y*30+5+60,20,20))
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        if event.type == MOUSEBUTTONDOWN:
            handleMouse(event.button)

def handleMouse(button):
    global numFlags, lose, win
    if button==1:
        x,y = pygame.mouse.get_pos()
        if revealed[int(round((y-60)/30))][int(round(x/30))] == 0 and flags[int(round((y-60)/30))][int(round(x/30))] == 0:
            revealed[int(round((y-60)/30))][int(round(x/30))] = 1
    if button==3:
        x,y = pygame.mouse.get_pos()
        if flags[int(round((y-60)/30))][int(round(x/30))] == 0:
            if(revealed[int(round((y-60)/30))][int(round(x/30))] == 0):
                flags[int(round((y-60)/30))][int(round(x/30))] = 1
                numFlags+=1
        else:
            flags[int(round((y-60)/30))][int(round(x/30))] = 0
            numFlags-=1
    hollowZeroes()
    removeFlags()
    if(determineLoss()):
        lose = True
    if(determineWin()):
        win = True

def hollowZeroes():
    global grid
    for k in range(rows):
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if grid[y][x] == 0 and revealed[y][x] == True:
                    for i in [-1,0,1]:
                        for j in [-1,0,1]:
                            if y+i >= 0 and y+i < len(grid) and x+j >= 0 and x+j < len(grid[y]):
                                revealed[y+i][x+j] = True

def removeFlags():
    global flags, revealed, numFlags
    for i in range(len(flags)):
        for j in range(len(flags)):
            if flags[i][j] and revealed[i][j]:
                flags[i][j] = 0
                numFlags -= 1

def uncoverFirstZero():
    global grid, revealed
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == 0:
                revealed[i][j] = True
                hollowZeroes()
                return

def determineLoss():
    global grid, revealed
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == 10 and revealed[i][j]:
                return True
    return False

def determineWin():
    global grid, revealed, numFlags
    if numFlags != 50:
        return False
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == 10 and flags[i][j] == 0:
                return False
            elif grid[i][j] != 10 and not revealed[i][j]:
                return False
    return True

def drawExplodingBombs():
    global explodeCtr
    global grid
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if grid[y][x] == 10:
                pygame.gfxdraw.aacircle(screen, x*30+15,y*30+60+15,int(explodeCtr),(255,255,100))
                pygame.draw.circle(screen,(255,250,100),(x*30+15,y*30+60+15),int(explodeCtr))
    explodeCtr*=1.01
    pygame.display.update()

def signalLoss():
    if explodeCtr < 20:
        drawExplodingBombs()
    else:
        x,y = pygame.mouse.get_pos()
        box = pygame.rect.Rect(int(rows*30/4),100,int(rows*30/2),200)
        if box.collidepoint(x,y):
            c = (200, 200, 200)
        else:
            c = (255, 25, 106)
        pygame.draw.rect(screen,c,box)
        text = titleFont.render('Kaboom!',1,(0,0,0))
        screen.blit(text,(int(rows*30/4)+20,120))
        text = defaultFont.render('Press to retry',1,(0,0,0))
        screen.blit(text,(int(rows*30/4)+20,160))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                reset()

def signalWin():
    x,y = pygame.mouse.get_pos()
    box = pygame.rect.Rect(int(rows*30/4),100,int(rows*30/2),200)
    if box.collidepoint(x,y):
        c = (200, 200, 200)
    else:
        c = (35, 211, 217)
    pygame.draw.rect(screen,c,box)
    text = titleFont.render('All Clear!',1,(0,0,0))
    screen.blit(text,(int(rows*30/4)+20,120))
    text = defaultFont.render('Press to play again',1,(0,0,0))
    screen.blit(text,(int(rows*30/4)+20,160))
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        if event.type == MOUSEBUTTONDOWN:
            reset()

def reset():
    global grid, revealed, flags, numFlags, win, lose, explodeCtr
    grid = [[0 for i in range(rows)] for i in range(columns)] 
    revealed = [[0 for i in range(rows)] for i in range(columns)] 
    flags = [[0 for i in range(rows)] for i in range(columns)]
    numFlags = 0
    win = False
    lose = False
    explodeCtr = 1
    makeBombs(50)
    getNumbers()
    uncoverFirstZero()

def showStats():
    pygame.draw.rect(screen,(255,255,255),(0,0,rows*30,60))
    titletext = titleFont.render('Minesweeper',1,(0,0,0))
    screen.blit(titletext,(10,10))
    flagtext = titleFont.render(str(numFlags)+'/50',1,(100,100,100))
    screen.blit(flagtext,(rows*30-100,10))

def main():
    global win, lose, screen
    makeBombs(50)
    getNumbers()
    uncoverFirstZero()
    t = pygame.time.Clock()
    while True:
        if win:
            signalWin()
        elif lose:
            signalLoss()
        else:
            screen.fill((0,0,0))
            showStats()
            drawGrid()
            t.tick(10)

if __name__ == '__main__':
    main()