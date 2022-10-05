import random, sys, pygame, time, copy
from pygame.locals import *
from configparser import ConfigParser
config = ConfigParser()


def main():
    global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE

    pygame.init()
    MAINCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((config.getint('svars' ,'WINDOWWIDTH'), config.getint('svars' ,'WINDOWHEIGHT')))
    pygame.display.set_caption('Flippy')
    FONT = pygame.font.Font('freesansbold.ttf', 16)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 32)

    boardImage = pygame.image.load('flippyboard.png')
    boardImage = pygame.transform.smoothscale(boardImage, (config.getint('svars' ,'BOARDWIDTH ') * config.getint('svars' ,'SPACESIZE'), config.getint('svars' ,'BOARDHEIGHT ') * config.getint('svars' ,'SPACESIZE')))
    boardImageRect = boardImage.get_rect()
    boardImageRect.topleft = (config.getint('svars' ,'XMARGIN'), config.getint('svars' ,'YMARGIN'))
    BGIMAGE = pygame.image.load('flippybackground.png')
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (config.getint('svars' ,'WINDOWWIDTH'), config.getint('svars' ,'WINDOWHEIGHT')))
    BGIMAGE.blit(boardImage, boardImageRect)

    while True:
        if runGame() == False:
            break


def runGame():

    mainBoard = getNewBoard()
    resetBoard(mainBoard)
    showHints = False
    turn = random.choice(['computer', 'player'])

    drawBoard(mainBoard)
    playerTile, computerTile = enterPlayerTile()

    newGameSurf = FONT.render('New Game', True, config.get('svars' ,'TEXTCOLOR'), config.get('svars' ,'TEXTBGCOLOR2'))
    newGameRect = newGameSurf.get_rect()
    newGameRect.topright = (config.getint('svars' ,'WINDOWWIDTH ') - 8, 10)
    hintsSurf = FONT.render('Hints', True, config.get('svars' ,'TEXTCOLOR'), config.get('svars' ,'TEXTBGCOLOR2'))
    hintsRect = hintsSurf.get_rect()
    hintsRect.topright = (config.getint('svars' ,'WINDOWWIDTH ') - 8, 40)

    while True:
        if turn == 'player':
            if getValidMoves(mainBoard, playerTile) == []:
                break
            movexy = None
            while movexy == None:

                if showHints:
                    boardToDraw = getBoardWithValidMoves(mainBoard, playerTile)
                else:
                    boardToDraw = mainBoard

                checkForQuit()
                for event in pygame.event.get(): # event handling loop
                    if event.type == MOUSEBUTTONUP:
                        mousex, mousey = event.pos
                        if newGameRect.collidepoint( (mousex, mousey) ):
                            return True
                        elif hintsRect.collidepoint( (mousex, mousey) ):
                            showHints = not showHints
                        movexy = getSpaceClicked(mousex, mousey)
                        if movexy != None and not isValidMove(mainBoard, playerTile, movexy[0], movexy[1]):
                            movexy = None

                drawBoard(boardToDraw)
                drawInfo(boardToDraw, playerTile, computerTile, turn)

                DISPLAYSURF.blit(newGameSurf, newGameRect)
                DISPLAYSURF.blit(hintsSurf, hintsRect)

                MAINCLOCK.tick(config.getint('svars' ,'FPS'))
                pygame.display.update()

            makeMove(mainBoard, playerTile, movexy[0], movexy[1], True)
            if getValidMoves(mainBoard, computerTile) != []:
                turn = 'computer'

        else:
            if getValidMoves(mainBoard, computerTile) == []:
                break

            drawBoard(mainBoard)
            drawInfo(mainBoard, playerTile, computerTile, turn)

            DISPLAYSURF.blit(newGameSurf, newGameRect)
            DISPLAYSURF.blit(hintsSurf, hintsRect)

            pauseUntil = time.time() + random.randint(5, 15) * 0.1
            while time.time() < pauseUntil:
                pygame.display.update()

            x, y = getComputerMove(mainBoard, computerTile)
            makeMove(mainBoard, computerTile, x, y, True)
            if getValidMoves(mainBoard, playerTile) != []:
                turn = 'player'

    drawBoard(mainBoard)
    scores = getScoreOfBoard(mainBoard)

    if scores[playerTile] > scores[computerTile]:
        text = 'You beat the computer by %s points! Congratulations!' % \
               (scores[playerTile] - scores[computerTile])
    elif scores[playerTile] < scores[computerTile]:
        text = 'You lost. The computer beat you by %s points.' % \
               (scores[computerTile] - scores[playerTile])
    else:
        text = 'The game was a tie!'

    textSurf = FONT.render(text, True, config.get('svars' ,'TEXTCOLOR'), config.get('svars' ,'TEXTBGCOLOR1'))
    textRect = textSurf.get_rect()
    textRect.center = (int(config.getint('svars' ,'WINDOWWIDTH ') / 2), int(config.getint('svars' ,'WINDOWHEIGHT ') / 2))
    DISPLAYSURF.blit(textSurf, textRect)

    text2Surf = BIGFONT.render('Play again?', True, config.getint('svars' ,'TEXTCOLOR'), config.get('svars' ,'TEXTBGCOLOR1'))
    text2Rect = text2Surf.get_rect()
    text2Rect.center = (int(config.getint('svars' ,'WINDOWWIDTH ') / 2), int(config.getint('svars' ,'WINDOWHEIGHT') / 2) + 50)

    yesSurf = BIGFONT.render('Yes', True, config.get('svars' ,'TEXTCOLOR'), config.get('svars' ,'TEXTBGCOLOR1'))
    yesRect = yesSurf.get_rect()
    yesRect.center = (int(config.getint('svars' ,'WINDOWWIDTH') / 2) - 60, int(config.getint('svars' ,'WINDOWHEIGHT') / 2) + 90)

    # Make "No" button.
    noSurf = BIGFONT.render('No', True, config.get('svars' ,'TEXTCOLOR'), config.get('svars' ,'TEXTBGCOLOR1'))
    noRect = noSurf.get_rect()
    noRect.center = (int(config.getint('svars' ,'WINDOWWIDTH') / 2) + 60, int(config.getint('svars' ,'WINDOWHEIGHT') / 2) + 90)

    while True:
        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if yesRect.collidepoint( (mousex, mousey) ):
                    return True
                elif noRect.collidepoint( (mousex, mousey) ):
                    return False
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(text2Surf, text2Rect)
        DISPLAYSURF.blit(yesSurf, yesRect)
        DISPLAYSURF.blit(noSurf, noRect)
        pygame.display.update()
        MAINCLOCK.tick(config.getint('svars' ,'FPS'))


def translateBoardToPixelCoord(x, y):
    return config.getint('svars' ,'XMARGIN') + x * config.getint('svars' ,'SPACESIZE') + int(config.getint('svars' ,'SPACESIZE') / 2), config.getint('svars' ,'YMARGIN') + y * config.getint('svars' ,'SPACESIZE') + int(config.getint('svars' ,'SPACESIZE') / 2)


def animateTileChange(tilesToFlip, tileColor, additionalTile):
    if tileColor == config.get('svars' ,'WHITE_TILE'):
        additionalTileColor = config.get('svars' ,'WHITE')
    else:
        additionalTileColor = config.get('svars' ,'BLACK')
    additionalTileX, additionalTileY = translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
    pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(config.getint('svars' ,'SPACESIZE') / 2) - 4)
    pygame.display.update()

    for rgbValues in range(0, 255, int(config.getint('svars' ,'ANIMATIONSPEED') * 2.55)):
        if rgbValues > 255:
            rgbValues = 255
        elif rgbValues < 0:
            rgbValues = 0

        if tileColor == config.get('svars' ,'WHITE_TILE'):
            color = tuple([rgbValues] * 3)
        elif tileColor == config.get('svars' ,'BLACK_TILE'):
            color = tuple([255 - rgbValues] * 3)

        for x, y in tilesToFlip:
            centerx, centery = translateBoardToPixelCoord(x, y)
            pygame.draw.circle(DISPLAYSURF, color, (centerx, centery), int(config.getint('svars' ,'SPACESIZE') / 2) - 4)
        pygame.display.update()
        MAINCLOCK.tick(config.getint('svars' ,'FPS'))
        checkForQuit()


def drawBoard(board):
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())

    for x in range(config.getint('svars' ,'BOARDWIDTH') + 1):
        startx = (x * config.getint('svars' ,'SPACESIZE')) + config.getint('svars' ,'XMARGIN')
        starty = config.getint('svars' ,'YMARGIN')
        endx = (x * config.getint('svars' ,'SPACESIZE')) + config.getint('svars' ,'XMARGIN')
        endy = config.getint('svars' ,'YMARGIN') + (config.getint('svars' ,'BOARDHEIGHT') * config.getint('svars' ,'SPACESIZE'))
        pygame.draw.line(DISPLAYSURF, config.get('svars' ,'GRIDLINECOLOR'), (startx, starty), (endx, endy))
    for y in range(config.getint('svars' ,'BOARDHEIGHT') + 1):
        startx = config.getint('svars' ,'XMARGIN')
        starty = (y * config.getint('svars' ,'SPACESIZE')) + config.getint('svars' ,'YMARGIN')
        endx = config.getint('svars' ,'XMARGIN') + (config.getint('svars' ,'BOARDWIDTH') * config.getint('svars' ,'SPACESIZE'))
        endy = (y * config.getint('svars' ,'SPACESIZE')) + config.getint('svars' ,'YMARGIN') 
        pygame.draw.line(DISPLAYSURF, config.get('svars' ,'GRIDLINECOLOR'), (startx, starty), (endx, endy))

    for x in range(config.getint('svars' ,'BOARDWIDTH')):
        for y in range(config.getint('svars' ,'BOARDHEIGHT')):
            centerx, centery = translateBoardToPixelCoord(x, y)
            if board[x][y] == config.get('svars' ,'WHITE_TILE') or board[x][y] == config.get('svars' ,'BLACK_TILE'):
                if board[x][y] == config.get('svars' ,'WHITE_TILE'):
                    tileColor = config.get('svars' ,'WHITE')
                else:
                    tileColor = config.get('svars' ,'BLACK')
                pygame.draw.circle(DISPLAYSURF, tileColor, (centerx, centery), int(config.getint('svars' ,'SPACESIZE') / 2) - 4)
            if board[x][y] == config.get('svars' ,'HINT_TILE'):
                pygame.draw.rect(DISPLAYSURF, config.get('svars' ,'HINTCOLOR'), (centerx - 4, centery - 4, 8, 8))


def getSpaceClicked(mousex, mousey):
    for x in range(config.getint('svars' ,'BOARDWIDTH')):
        for y in range(config.getint('svars' ,'BOARDHEIGHT')):
            if mousex > x *config.getint('svars' ,' SPACESIZE') + config.getint('svars' ,'XMARGIN') and \
               mousex < (x + 1) *config.getint('svars' ,' SPACESIZE') + config.getint('svars' ,'XMARGIN') and \
               mousey > y * config.getint('svars' ,'SPACESIZE') + config.getint('svars' ,'YMARGIN') and \
               mousey < (y + 1) * config.getint('svars' ,'SPACESIZE') + config.getint('svars' ,'YMARGIN'):
                return (x, y)
    return None


def drawInfo(board, playerTile, computerTile, turn):
    scores = getScoreOfBoard(board)
    scoreSurf = FONT.render("Player Score: %s    Computer Score: %s    %s's Turn" % (str(scores[playerTile]), str(scores[computerTile]), turn.title()), True, config.get('svars' ,'TEXTCOLOR'))
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomleft = (10, config.getint('svars' ,'WINDOWHEIGHT') - 5)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def resetBoard(board):
    for x in range(config.getint('svars' ,'(BOARDWIDTH')):
        for y in range(config.getint('svars' ,'BOARDHEIGHT')):
            board[x][y] = config.get('svars' ,'EMPTY_SPACE')

    board[3][3] = config.get('svars' ,'WHITE_TILE')
    board[3][4] = config.get('svars' ,'BLACK_TILE')
    board[4][3] = config.get('svars' ,'BLACK_TILE')
    board[4][4] = config.get('svars' ,'WHITE_TILE')


def getNewBoard():
    board = []
    for i in range(config.getint('svars' ,'BOARDWIDTH')):
        board.append([config.get('svars' ,'EMPTY_SPACE')] * config.getint('svars' ,'BOARDHEIGHT'))

    return board


def isValidMove(board, tile, xstart, ystart):
    if board[xstart][ystart] != config.get('svars' ,'EMPTY_SPACE') or not isOnBoard(xstart, ystart):
        return False

    board[xstart][ystart] = tile

    if tile == config.get('svars' ,'WHITE_TILE'):
        otherTile = config.get('svars' ,'BLACK_TILE')
    else:
        otherTile = config.get('svars' ,'WHITE_TILE')

    tilesToFlip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if isOnBoard(x, y) and board[x][y] == otherTile:
            x += xdirection
            y += ydirection
            if not isOnBoard(x, y):
                continue
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not isOnBoard(x, y):
                    break
            if not isOnBoard(x, y):
                continue
            if board[x][y] == tile:
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append([x, y])

    board[xstart][ystart] = config.get('svars' ,'EMPTY_SPACE')
    if len(tilesToFlip) == 0:
        return False
    return tilesToFlip


def isOnBoard(x, y):
    return x >= 0 and x < config.getint('svars' ,'BOARDWIDTH') and y >= 0 and y < config.getint('svars', 'BOARDHEIGHT')

def getBoardWithValidMoves(board, tile):
    dupeBoard = copy.deepcopy(board)

    for x, y in getValidMoves(dupeBoard, tile):
        dupeBoard[x][y] = config.get('svars' ,'HINT_TILE')
    return dupeBoard


def getValidMoves(board, tile):
    validMoves = []

    for x in range(config.getint('svars' ,'BOARDWIDTH')):
        for y in range(config.getint('svars' ,'BOARDHEIGHT')):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append((x, y))
    return validMoves


def getScoreOfBoard(board):
    xscore = 0
    oscore = 0
    for x in range(config.getint('svars' ,'BOARDWIDTH')):
        for y in range(config.getint('svars' ,'BOARDHEIGHT')):
            if board[x][y] == config.get('svars' ,'WHITE_TILE'):
                xscore += 1
            if board[x][y] == config.get('svars' ,'BLACK_TILE'):
                oscore += 1
    return {config.get('svars' ,'WHITE_TILE'):xscore, config.get('svars' ,'BLACK_TILE'):oscore}

def enterPlayerTile():
    textSurf = FONT.render('Do you want to be white or black?', True, config.get('svars' ,'TEXTCOLOR'), config.get('svars' ,'TEXTBGCOLOR1'))
    textRect = textSurf.get_rect()
    textRect.center = (int(config.getint('svars' ,'WINDOWWIDTH') / 2), int(config.getint('svars' ,'WINDOWHEIGHT') / 2))

    xSurf = BIGFONT.render('White', True, config.get('svars' ,'TEXTCOLOR'), config.get('svars' ,'TEXTBGCOLOR1'))
    xRect = xSurf.get_rect()
    xRect.center = (int(config.getint('svars' ,'WINDOWWIDTH') / 2) - 60, int(config.getint('svars' ,'WINDOWHEIGHT') / 2) + 40)

    oSurf = BIGFONT.render('Black', True, config.get('svars' ,'TEXTCOLOR'), config.get('svars' ,'TEXTBGCOLOR1'))
    oRect = oSurf.get_rect()
    oRect.center = (int(config.getint('svars' ,'WINDOWWIDTH') / 2) + 60, int(config.getint('svars' ,'WINDOWHEIGHT') / 2) + 40)

    while True:
        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if xRect.collidepoint( (mousex, mousey) ):
                    return [config.get('svars' ,'WHITE_TILE'), config.get('svars' ,'BLACK_TILE')]
                elif oRect.collidepoint( (mousex, mousey) ):
                    return [config.get('svars' ,'BLACK_TILE'), config.get('svars' ,'WHITE_TILE')]

        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(xSurf, xRect)
        DISPLAYSURF.blit(oSurf, oRect)
        pygame.display.update()
        MAINCLOCK.tick(config.getint('svars' ,'FPS'))


def makeMove(board, tile, xstart, ystart, realMove=False):
    tilesToFlip = isValidMove(board, tile, xstart, ystart)

    if tilesToFlip == False:
        return False

    board[xstart][ystart] = tile

    if realMove:
        animateTileChange(tilesToFlip, tile, (xstart, ystart))

    for x, y in tilesToFlip:
        board[x][y] = tile
    return True


def isOnCorner(x, y):
    return (x == 0 and y == 0) or \
           (x == config.getint('svars' ,'BOARDWIDTH') and y == 0) or \
           (x == 0 and y == config.getint('svars' ,'BOARDHEIGHT')) or \
           (x == config.getint('svars' ,'BOARDWIDTH') and y == config.getint('svars' ,'BOARDHEIGHT'))


def getComputerMove(board, computerTile):
    possibleMoves = getValidMoves(board, computerTile)

    random.shuffle(possibleMoves)

    for x, y in possibleMoves:
        if isOnCorner(x, y):
            return [x, y]

    bestScore = -1
    for x, y in possibleMoves:
        dupeBoard = copy.deepcopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        score = getScoreOfBoard(dupeBoard)[computerTile]
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score
    return bestMove


def checkForQuit():
    for event in pygame.event.get((QUIT, KEYUP)): # event handling loop
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()


if __name__ == '__main__':
    main()
