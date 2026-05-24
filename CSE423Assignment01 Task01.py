from OpenGL.GL import *      
from OpenGL.GLUT import *    
from OpenGL.GLU import *     
import math
import random

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600

rain = [(random.randint(-400, 400), random.randint(80, 300)) for _ in range(25)]
rain_dx = 0

sky = 0.4
sky_dir = 0

def draw_ground():
    glColor3f(0.55, 0.4, 0.1) 
    glBegin(GL_TRIANGLES)

    glVertex2f(-400, -60)
    glVertex2f(400, -60)
    glVertex2f(-400, -300)
    
    glVertex2f(400, -60)
    glVertex2f(400, -300)
    glVertex2f(-400, -300)
    
    glEnd()


def draw_sky():
    glColor3f(0, 0, sky)   
    glBegin(GL_TRIANGLES)
    glVertex2f(-400, -80)
    glVertex2f(-400, 300)
    glVertex2f(400, 300)

    glVertex2f(400, 300)
    glVertex2f(400, -80)
    glVertex2f(-400, -80)   
    glEnd()


def draw_house():
    # Roof Triangle
    glBegin(GL_TRIANGLES)
    glColor3f(0, 1, 1)
    glVertex2d(-90, 50)
    glColor3f(0, 1, 1)
    glVertex2d(90, 50)
    glColor3f(0, 1, 1)
    glVertex2d(0, 100)
    glEnd()
    
    #Body
    glBegin(GL_TRIANGLES)
    glColor3f(0, 1, 1)
    glVertex2f(90, 50)
    glVertex2f(90, -60)
    glVertex2f(-90, -60)
    
    glVertex2f(-90, -60)
    glVertex2f(-90, 50)
    glVertex2f(90, 50)
    #House Gate
    glColor3f(1, 0, 0)
    glVertex2f(20, 10)
    glVertex2f(-20, 10)
    glVertex2f(-20, -60)
    
    glVertex2f(-20, -60)
    glVertex2f(20, -60)
    glVertex2f(20, 10)
    glEnd()


def draw_mountain():
    glColor3f(0, 0.5, 0)
    glBegin(GL_TRIANGLES)

    glVertex2f(-400, -60) 
    glVertex2f(-200, -60) 
    glVertex2f(-300, 60) 


    glVertex2f(-200, -60) 
    glVertex2f(0, -60) 
    glVertex2f(-100, 60) 
    
    glVertex2f(0, -60) 
    glVertex2f(200, -60) 
    glVertex2f(100, 60) 

    glVertex2f(200, -60)
    glVertex2f(400, -60)
    glVertex2f(300, 60)
    
    glEnd()


def draw_rain():
    
    rain_color = 0.7 + (1 - sky)*0.3
    glColor3f(rain_color, rain_color, 1.0)

    glBegin(GL_LINES)
    for x, y in rain:
        glVertex2f(x, y)
        glVertex2f(x + rain_dx, y - 12)
    glEnd()


def setup_projection():
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-400, 400, -300, 300, 0, 1) 
    glMatrixMode(GL_MODELVIEW)


def display():
    glClearColor(sky, sky, sky, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    draw_sky()
    draw_mountain()
    draw_ground()
    draw_house()
    draw_rain()  
    glutSwapBuffers()

def animate():
    global rain, sky

    updated = []
    for x, y in rain:
        y -= 6
        if y < -300:
            y = 300
            x = random.randint(-400, 400)
        updated.append((x, y))
    rain[:] = updated

    sky += sky_dir
    sky = max(0.05, min(1.0, sky))

    glutPostRedisplay()



def keyboard(key, x, y):
    global sky_dir

    if key == b'd':      # night to day
        sky_dir = 0.1
    elif key == b'n':    # day to night
        sky_dir = -0.1


def special(key, x, y):
    global rain_dx
    if key == GLUT_KEY_LEFT:
        rain_dx -= 0.5
    elif key == GLUT_KEY_RIGHT:
        rain_dx += 0.5
    if rain_dx > 10:
        rain_dx = 10
    if rain_dx < -10:
        rain_dx = -10

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(350, 50)
    glutCreateWindow(b"Assignment Task 01")
    setup_projection()
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special)
    glutMainLoop()
    
if __name__ == "__main__":
    main()