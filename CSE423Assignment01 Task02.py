from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

Width, Height = 500, 500   
Points = []
Speed = 0.2
BaseStep = 1.0       
PointSize = 10
blink_on = False
frozen = False
BG_R, BG_G, BG_B = 0.0, 0.0, 0.0

def convert_coordinate(x, y):
    a = x - (Width / 2)
    b = (Height / 2) - y
    return a, b

def setup_projection():
    glViewport(0, 0,Width, Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-Width/2, Width/2, -Height/2, Height/2, 0, 1)
    glMatrixMode(GL_MODELVIEW)



def draw_point(x, y, size):
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()



def keyboard_listener(key, x, y):
    global frozen
    if key == b' ':
        frozen = not frozen
        glutPostRedisplay()
        return
    if frozen:
        return

def special_key_listener(key, x, y):
    global Speed
    if frozen:
        return
    if key == GLUT_KEY_UP:
        Speed *= 1.6
    elif key == GLUT_KEY_DOWN:
        Speed /= 1.6
        if Speed < 0.15:
            Speed = 0.15
    glutPostRedisplay()

def mouse_listener(button, state, x, y):
    global blink_on
    if frozen:
        return
    if state != GLUT_DOWN:
        return
    if button == GLUT_LEFT_BUTTON:
        blink_on = not blink_on
        glutPostRedisplay()
        return
    if button == GLUT_RIGHT_BUTTON:
        px, py = convert_coordinate(x, y)
        dx = random.choice([-1, 1])
        dy = random.choice([-1, 1])
        r = random.random()
        g = random.random()
        b = random.random()
        Points.append([px, py, dx, dy, r, g, b])
        glutPostRedisplay()


def display():
    glClearColor(BG_R, BG_G, BG_B, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_projection()
    t = glutGet(GLUT_ELAPSED_TIME)
    phase = (t // 450) % 2
    for p in Points:
        x, y, dx, dy, r, g, b = p
        if blink_on and phase == 1:
            glColor3f(BG_R, BG_G, BG_B)
        else:
            glColor3f(r, g, b)
        draw_point(x, y, PointSize)
    glutSwapBuffers()

def animate():
    if frozen:
        glutPostRedisplay()
        return
    step = BaseStep * Speed
    min_x = -Width / 2
    max_x = Width / 2
    min_y = -Height / 2
    max_y = Height / 2
    for p in Points:
        x, y, dx, dy, r, g, b = p
        x += dx * step
        y += dy * step
        if x > max_x:
            x = max_x
            dx = -dx
        elif x < min_x:
            x = min_x
            dx = -dx

        if y > max_y:
            y = max_y
            dy = -dy
        elif y < min_y:
            y = min_y
            dy = -dy
        p[0] = x
        p[1] = y
        p[2] = dx
        p[3] = dy
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(Width, Height)
    glutInitWindowPosition(350, 50)
    glutCreateWindow(b"Assignment Task 02")
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)
    glutMainLoop()
    
if __name__ == "__main__":
    main()