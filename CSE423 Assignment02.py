from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random

#Window
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
FRAMES_PER_SECOND = 80

#Button
BUTTON_W = 50
BUTTON_H = 50

#Diamond
DIAMOND_SIZE = 20
DIAMOND_INITIAL_SPEED = 150
DIAMOND_ACCELERATION = 15

#Catcher
CATCHER_WIDTH = 100
CATCHER_HEIGHT = 10
CATCHER_SPEED = 400

#Color
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)
RED = (1.0, 0.0, 0.0)
TEAL = (0.251, 0.878, 0.816)
AMBER = (1.0, 0.75, 0.0)

#game beginning
Score = 0
game_state = "PLAYING"  
cheat_mode = False


#Catcher Position
catcher_x = SCREEN_WIDTH / 2 - CATCHER_WIDTH / 2
catcher_y = 10


#Diamond Position
diamond_x = SCREEN_WIDTH / 2
diamond_y = SCREEN_HEIGHT - 100
diamond_speed = DIAMOND_INITIAL_SPEED
diamond_color = WHITE

catcher_direction = 0    
last_time = 0


#Button
Restart_button = [20, SCREEN_HEIGHT - 50, BUTTON_W, BUTTON_H]
Pause_button = [SCREEN_WIDTH / 2 - BUTTON_W / 2 , SCREEN_HEIGHT - 50, BUTTON_W, BUTTON_H]
Exit_button = [SCREEN_WIDTH - 20 - BUTTON_W, SCREEN_HEIGHT - 50, BUTTON_W, BUTTON_H]


#Midpoint drawing
def plotPixel(x, y):
    glBegin(GL_POINTS)
    glVertex2i(int(round(x)), int(round(y)))
    glEnd()


def findZone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) >= abs(dy):
        if dx >= 0 and dy >= 0:
            return 0
        elif dx < 0 and dy >= 0:
            return 3
        elif dx < 0 and dy < 0:
            return 4
        else:
            return 7
    else:
        if dx >= 0 and dy >= 0:
            return 1
        elif dx < 0 and dy >= 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5
        else:
            return 6


def convertToZone0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y


def convertFromZone0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y


def drawLineZone0(x1, y1, x2, y2, original_zone):
    dx = int(round(x2 - x1))
    dy = int(round(y2 - y1))
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x = int(round(x1))
    y = int(round(y1))
    while x <= int(round(x2)):
        ox, oy = convertFromZone0(x, y, original_zone)
        plotPixel(ox, oy)
        if d > 0:
            d += incNE
            y += 1
        else:
            d += incE
        x += 1


def drawLine(x1, y1, x2, y2):
    zone = findZone(x1, y1, x2, y2)
    x1p, y1p = convertToZone0(x1, y1, zone)
    x2p, y2p = convertToZone0(x2, y2, zone)
    if x1p > x2p:
        x1p, x2p = x2p, x1p
        y1p, y2p = y2p, y1p
    drawLineZone0(x1p, y1p, x2p, y2p, zone)



def drawCatcher():
    if game_state == "GAME_OVER":
        glColor3f(*RED)
    else:
        glColor3f(*WHITE)
    inset = CATCHER_WIDTH * 0.10
    p_bl = (catcher_x + inset, catcher_y)
    p_br = (catcher_x + CATCHER_WIDTH - inset, catcher_y)
    p_tl = (catcher_x, catcher_y + CATCHER_HEIGHT)
    p_tr = (catcher_x + CATCHER_WIDTH, catcher_y + CATCHER_HEIGHT)
    drawLine(*p_bl, *p_br)
    drawLine(*p_br, *p_tr)
    drawLine(*p_tr, *p_tl)
    drawLine(*p_tl, *p_bl)


def drawDiamond():
    if game_state == "GAME_OVER":
        return
    glColor3f(*diamond_color)
    half_w = DIAMOND_SIZE / 2
    half_h = DIAMOND_SIZE / 2
    top = (diamond_x, diamond_y + half_h)
    right = (diamond_x + half_w, diamond_y)
    bottom = (diamond_x, diamond_y - half_h)
    left = (diamond_x - half_w, diamond_y)
    drawLine(*top, *right)
    drawLine(*right, *bottom)
    drawLine(*bottom, *left)
    drawLine(*left, *top)


def drawRestartButton():
    x, y, w, h = Restart_button
    glColor3f(*TEAL)
    mid_y = y + h / 2
    left_x = x + w * 0.25
    right_x = x + w * 0.75
    tip_x = x + w * 0.25
    head_x = x + w * 0.50
    drawLine(right_x, mid_y, left_x, mid_y)
    drawLine(tip_x, mid_y, head_x, mid_y + h * 0.20)
    drawLine(tip_x, mid_y, head_x, mid_y - h * 0.20)


def drawPausePlayButton():
    x, y, w, h = Pause_button
    glColor3f(*AMBER)
    top = y + h * 0.25
    bottom = y + h * 0.75
    if game_state == "PLAYING":
        left_bar = x + w * 0.40
        right_bar = x + w * 0.60
        drawLine(left_bar, top, left_bar, bottom)
        drawLine(right_bar, top, right_bar, bottom)
    else:
        left_x = x + w * 0.40
        tip_x = x + w * 0.65
        mid_y = y + h / 2
        drawLine(left_x, y + h * 0.25, tip_x, mid_y)
        drawLine(tip_x, mid_y, left_x, y + h * 0.75)
        drawLine(left_x, y + h * 0.75, left_x, y + h * 0.25)


def drawExitButton():
    x, y, w, h = Exit_button
    glColor3f(*RED)
    pad_x = w * 0.25
    pad_y = h * 0.25
    drawLine(x + pad_x, y + pad_y, x + w - pad_x, y + h - pad_y)
    drawLine(x + pad_x, y + h - pad_y, x + w - pad_x, y + pad_y)


def drawButtons():
    drawRestartButton()
    drawPausePlayButton()
    drawExitButton()


def pointBoundary(px, py, box):
    bx, by, bw, bh = box
    return bx <= px <= bx + bw and by <= py <= by + bh


def getDiamondBox():
    return [
        diamond_x - DIAMOND_SIZE / 2,
        diamond_y - DIAMOND_SIZE / 2,
        DIAMOND_SIZE,
        DIAMOND_SIZE
    ]


def getCatcherBox():
    return [
        catcher_x,
        catcher_y,
        CATCHER_WIDTH,
        CATCHER_HEIGHT
    ]


def hasCollide(box1, box2):
    return (
        box1[0] < box2[0] + box2[2] and
        box1[0] + box1[2] > box2[0] and
        box1[1] < box2[1] + box2[3] and
        box1[1] + box1[3] > box2[1]
    )


def randomBrightColor():
    return (
        random.uniform(0.5, 1.0),
        random.uniform(0.5, 1.0),
        random.uniform(0.5, 1.0)
    )


def dropDiamond():
    global diamond_x, diamond_y, diamond_color
    diamond_x = random.uniform(DIAMOND_SIZE / 2, SCREEN_WIDTH - DIAMOND_SIZE / 2)
    diamond_y = SCREEN_HEIGHT - 140
    diamond_color = randomBrightColor()


def restartGame():
    global Score, game_state, diamond_speed, catcher_x, catcher_direction, cheat_mode
    Score = 0
    game_state = "PLAYING"
    cheat_mode = False
    catcher_direction = 0
    diamond_speed = DIAMOND_INITIAL_SPEED
    catcher_x = SCREEN_WIDTH / 2 - CATCHER_WIDTH / 2
    print("Starting Over")
    dropDiamond()


def togglePause():
    global game_state
    if game_state == "PLAYING":
        game_state = "PAUSED"
    elif game_state == "PAUSED":
        game_state = "PLAYING"


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    drawCatcher()
    drawDiamond()
    drawButtons()
    glutSwapBuffers()


def idle():
    global diamond_y, diamond_speed, Score, catcher_x, last_time, game_state
    current_time = glutGet(GLUT_ELAPSED_TIME)
    delta_time = (current_time - last_time) / 1000 
    if delta_time <= 0:
        glutPostRedisplay()
        return
    last_time = current_time
    if game_state == "PLAYING":
        diamond_y -= diamond_speed * delta_time
        diamond_speed += DIAMOND_ACCELERATION * delta_time
        target_x = catcher_x

        if cheat_mode:
            target_x = diamond_x - CATCHER_WIDTH / 2
            if catcher_x < target_x:
                catcher_x += CATCHER_SPEED * delta_time
                if catcher_x > target_x:
                    catcher_x = target_x
            elif catcher_x > target_x:
                catcher_x -= CATCHER_SPEED * delta_time
                if catcher_x < target_x:
                    catcher_x = target_x
        else:
            if catcher_direction == -1:
                catcher_x -= CATCHER_SPEED * delta_time
            elif catcher_direction == 1:
                catcher_x += CATCHER_SPEED * delta_time

        if catcher_x < 0:
            catcher_x = 0
        if catcher_x > SCREEN_WIDTH - CATCHER_WIDTH:
            catcher_x = SCREEN_WIDTH - CATCHER_WIDTH

        if hasCollide(getCatcherBox(), getDiamondBox()):
            Score += 1
            print(f"Score: {Score}")
            dropDiamond()
        elif diamond_y - DIAMOND_SIZE / 2 <= 0:
            game_state = "GAME_OVER"
            print(f"Game Over! Score: {Score}")

    glutPostRedisplay()


def specialKeyListener(key, x, y):
    global catcher_direction
    if game_state != "PLAYING" or cheat_mode:
        return
    if key == GLUT_KEY_LEFT:
        catcher_direction = -1
    elif key == GLUT_KEY_RIGHT:
        catcher_direction = 1


def specialKeyUpListener(key, x, y):
    global catcher_direction
    if key == GLUT_KEY_LEFT and catcher_direction == -1:
        catcher_direction = 0
    elif key == GLUT_KEY_RIGHT and catcher_direction == 1:
        catcher_direction = 0


def keyboardListener(key, x, y):
    global cheat_mode

    key = key.decode("utf-8").lower()

    if key == 'c' and game_state != "GAME_OVER":
        cheat_mode = not cheat_mode
        if cheat_mode:
            print("Cheat Mode: ON")
        else:
            print("Cheat Mode: OFF")


def mouseListener(button, state, x, y):
    global score
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        my = SCREEN_HEIGHT - y
        if pointBoundary(x, my, Restart_button):
            restartGame()
        elif pointBoundary(x, my, Pause_button):
            if game_state != "GAME_OVER":
                togglePause()
        elif pointBoundary(x, my, Exit_button):
            print(f"Goodbye. Score: {score}")
            glutLeaveMainLoop()


def init():
    glClearColor(*BLACK, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glPointSize(2.0)


def main():
    global last_time
    glutInit()
    glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    glutInitWindowPosition(100, 50)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutCreateWindow(b"Catch the Diamond")
    init()
    dropDiamond()
    last_time = glutGet(GLUT_ELAPSED_TIME)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutSpecialFunc(specialKeyListener)
    glutSpecialUpFunc(specialKeyUpListener)
    glutKeyboardFunc(keyboardListener)
    glutMouseFunc(mouseListener)
    glutMainLoop()


if __name__ == "__main__":
    main()