from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random, time

player_x, player_y = 0, 0
gun_angle = 0.0
bullets = []
enemies = []
game_over = False

player_life = 5
game_score = 0
bullets_missed = 0

last_cheat_shot_time = 0.0
CHEAT_FIRE_COOLDOWN = 0.5

wall_height = 50
MAX_MISSED_BULLETS = 10
CHEAT_MODE = False
AUTO_FOLLOW = False

camera_mode = "third_person" #Player
camera_pos_third_person = (0, -200, 300)
camera_angle_h, camera_angle_v = 0.0, 0.0

fovY = 130
GRID_LENGTH = 900
SMOOTH_FACTOR = 2
TEXT_POS = {
    "life": (30, 770),
    "score": (30, 740),
    "missed": (30, 710),
    "game_over": (400, 400)
}

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18): #Prints text on screen
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player(first_person=False):
    global gun_angle, game_over
    glPushMatrix()
    glTranslatef(player_x, player_y, 0) # player move
    
    if game_over:
        glRotatef(90, 1, 0, 0)
    else:
        glRotatef(gun_angle, 0, 0, 1)

    if not first_person:
        glPushMatrix()      #body
        glTranslatef(0, 0, 35)
        glColor3f(0.0, 0.6, 0.0)
        glutSolidCube(30)  
        glPopMatrix()

        glPushMatrix()     #head
        glTranslatef(0, 0, 70)
        glColor3f(0.0, 0.0, 0.0)
        gluSphere(gluNewQuadric(), 15, 20, 20) 
        glPopMatrix()

        glColor3f(0.0, 0.0, 0.8) #arm
        glPushMatrix()
        glTranslatef(-10, 0, 0)
        gluCylinder(gluNewQuadric(), 8, 8, 40, 20, 20) 
        glPopMatrix()
        glPushMatrix()
        glTranslatef(10, 0, 0)
        gluCylinder(gluNewQuadric(), 8, 8, 40, 20, 20) 
        glPopMatrix()

    glColor3f(0.9, 0.7, 0.5) #leg
    glPushMatrix()
    glTranslatef(-15, 0, 40)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 4, 40, 20, 20)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(15, 0, 40)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 4, 40, 20, 20)
    glPopMatrix()

    glColor3f(0.6, 0.6, 0.6) #torso
    glPushMatrix()
    glTranslatef(0, 0, 40)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 5, 50, 20, 20)

    glPushMatrix() #feet
    glTranslatef(0, 0, -10)
    glColor3f(0.3, 0.3, 0.3)
    glutSolidCube(10) 
    glPopMatrix()
    glPopMatrix()
    glPopMatrix()

def draw_enemy(enemy_pos, scale):
    glPushMatrix()
    glTranslatef(enemy_pos[0], enemy_pos[1], enemy_pos[2])
    glScalef(scale, scale, scale)
    glColor3f(1.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 20, 20, 20)
    glTranslatef(0, 0, 25)
    glColor3f(0.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 10, 20, 20)
    glPopMatrix()

def draw_bullet(bullet_pos):
    glPushMatrix()
    glTranslatef(bullet_pos[0], bullet_pos[1], bullet_pos[2])
    glColor3f(1.0, 0.0, 0.0)
    glutSolidCube(12)  
    glPopMatrix()
    
def create_grid_walls():
    cell_size = GRID_LENGTH / 10
    grid_boundary = cell_size * 5

    glBegin(GL_QUADS)
    for i in range(-6, 6):
        for j in range(-6, 6):
            if (i + j) % 2 == 0:
                glColor3f(0.643, 0.463, 1.0)
            else:
                glColor3f(1.0, 1.0, 1.0)
            glVertex3f(i * cell_size, j * cell_size, 0)
            glVertex3f(i * cell_size, (j + 1) * cell_size, 0)
            glVertex3f((i + 1) * cell_size, (j + 1) * cell_size, 0)
            glVertex3f((i + 1) * cell_size, j * cell_size, 0)
    glEnd()

    glBegin(GL_QUADS) #1st wall
    glColor3f(1, 1, 1)
    glVertex3f(-grid_boundary, -grid_boundary, 0)
    glVertex3f(grid_boundary, -grid_boundary, 0)
    glVertex3f(grid_boundary, -grid_boundary, wall_height)
    glVertex3f(-grid_boundary, -grid_boundary, wall_height)
    glEnd()

    glBegin(GL_QUADS) #2nd wall
    glColor3f(0, 1, 0)
    glVertex3f(grid_boundary, -grid_boundary, 0)
    glVertex3f(grid_boundary, grid_boundary, 0)
    glVertex3f(grid_boundary, grid_boundary, wall_height)
    glVertex3f(grid_boundary, -grid_boundary, wall_height)
    glEnd()

    glBegin(GL_QUADS) #3rd wall
    glColor3f(0, 1, 1)
    glVertex3f(-grid_boundary, grid_boundary, 0)
    glVertex3f(-grid_boundary, grid_boundary, wall_height)
    glVertex3f(grid_boundary, grid_boundary, wall_height)
    glVertex3f(grid_boundary, grid_boundary, 0)
    glEnd()

    glBegin(GL_QUADS) #4rth wall
    glColor3f(0, 0, 1)
    glVertex3f(-grid_boundary, grid_boundary, 0)
    glVertex3f(-grid_boundary, -grid_boundary, 0)
    glVertex3f(-grid_boundary, -grid_boundary, wall_height)
    glVertex3f(-grid_boundary, grid_boundary, wall_height)
    glEnd()

def keyboardListener(key, x, y):
    global player_x, player_y, gun_angle, CHEAT_MODE, AUTO_FOLLOW
    global game_over, camera_mode, camera_angle_h

    if key == b'R':
        restart_game()
        return
    if game_over:
        return
    
    move_speed = 10
    if CHEAT_MODE:
        if camera_mode == "first_person":
            move_dir = camera_angle_h
            if key == b'W':
                player_x += move_speed * math.sin(math.radians(move_dir))
                player_y += move_speed * math.cos(math.radians(move_dir))
            if key == b'S':
                player_x -= move_speed * math.sin(math.radians(move_dir))
                player_y -= move_speed * math.cos(math.radians(move_dir))
            if key == b'A':
                gun_angle += 20
                camera_angle_h = gun_angle
            if key == b'D':
                gun_angle -= 20
                camera_angle_h = gun_angle
        else:
            move_dir = camera_angle_h
            if key == b'W':
                player_x += move_speed * math.sin(math.radians(move_dir))
                player_y += move_speed * math.cos(math.radians(move_dir))
            if key == b'S':
                player_x -= move_speed * math.sin(math.radians(move_dir))
                player_y -= move_speed * math.cos(math.radians(move_dir))
            if key == b'A':
                player_x -= move_speed * math.cos(math.radians(move_dir))
                player_y += move_speed * math.sin(math.radians(move_dir))
            if key == b'D':
                player_x += move_speed * math.cos(math.radians(move_dir))
                player_y -= move_speed * math.sin(math.radians(move_dir))
    else: 
        if camera_mode == "first_person":
            move_dir = camera_angle_h
            if key == b'W':
                player_x += move_speed * math.sin(math.radians(move_dir))
                player_y += move_speed * math.cos(math.radians(move_dir))
            if key == b'S':
                player_x -= move_speed * math.sin(math.radians(move_dir))
                player_y -= move_speed * math.cos(math.radians(move_dir))
            if key == b'A':
                gun_angle += 10
                camera_angle_h = -gun_angle
            if key == b'D':
                gun_angle -= 10
                camera_angle_h = -gun_angle
        else: 
            if key == b'W':
                player_x += move_speed * math.sin(math.radians(gun_angle))
                player_y += move_speed * math.cos(math.radians(gun_angle))
            if key == b'S':
                player_x -= move_speed * math.sin(math.radians(gun_angle))
                player_y -= move_speed * math.cos(math.radians(gun_angle))
            if key == b'A':
                gun_angle += 10
            if key == b'D':
                gun_angle -= 10

    if key == b'C':
        CHEAT_MODE = not CHEAT_MODE
        if not CHEAT_MODE:
            AUTO_FOLLOW = False

    if key == b'V':
        if CHEAT_MODE and camera_mode == "first_person":
            AUTO_FOLLOW = not AUTO_FOLLOW

    player_x = max(-GRID_LENGTH/2 + 20, min(GRID_LENGTH/2 - 20, player_x))
    player_y = max(-GRID_LENGTH/2 + 20, min(GRID_LENGTH/2 - 20, player_y))

    glutPostRedisplay()

def specialKeyListener(key, x, y):
    global camera_angle_v, camera_angle_h, gun_angle, CHEAT_MODE, AUTO_FOLLOW, camera_mode
    if game_over:
        return
    if camera_mode == "third_person":
        if key == GLUT_KEY_UP:
            camera_angle_v += 5
        if key == GLUT_KEY_DOWN:
            camera_angle_v -= 5
        if key == GLUT_KEY_LEFT:
            camera_angle_h -= 5
        if key == GLUT_KEY_RIGHT:
            camera_angle_h += 5
    elif camera_mode == "first_person":
        if key == GLUT_KEY_UP:
            camera_angle_v += 2
        if key == GLUT_KEY_DOWN:
            camera_angle_v -= 2
        if key == GLUT_KEY_LEFT:
            camera_angle_h += 2
        if key == GLUT_KEY_RIGHT:
            camera_angle_h -= 2
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global bullets, camera_mode, game_over, AUTO_FOLLOW, CHEAT_MODE

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        bullet_speed = 3
       
        bullet_vx = bullet_speed * math.cos(math.radians(gun_angle + 90))
        bullet_vy = bullet_speed * math.sin(math.radians(gun_angle + 90))
        bullet_x_start = player_x + 80 * math.cos(math.radians(gun_angle + 90))
        bullet_y_start = player_y + 80 * math.sin(math.radians(gun_angle + 90))

        bullets.append([bullet_x_start, bullet_y_start, 0, bullet_vx, bullet_vy])
        print("Player Bullet Fired!")
       
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if camera_mode == "third_person":
            camera_mode = "first_person"
        else:
            camera_mode = "third_person"
            AUTO_FOLLOW = False

def setupCamera():
    global AUTO_FOLLOW, CHEAT_MODE, gun_angle, camera_angle_v, camera_mode, camera_angle_h
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == "first_person":
        eye_x = player_x
        eye_y = player_y
        eye_z = 80
        
        if CHEAT_MODE and AUTO_FOLLOW:
            camera_angle_h = gun_angle

        center_x = eye_x + 100 * math.sin(math.radians(camera_angle_h))
        center_y = eye_y + 100 * math.cos(math.radians(camera_angle_h))
        center_z = eye_z + camera_angle_v
        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 0, 1)
    else:
        eye_x = (camera_pos_third_person[0] * math.cos(math.radians(camera_angle_h)) - camera_pos_third_person[1] * math.sin(math.radians(camera_angle_h)))
        eye_y = (camera_pos_third_person[0] * math.sin(math.radians(camera_angle_h)) + camera_pos_third_person[1] * math.cos(math.radians(camera_angle_h)))
        eye_z = camera_pos_third_person[2] + camera_angle_v
        gluLookAt(eye_x, eye_y, eye_z, player_x, player_y, 20, 0, 0, 1)


def idle():
    global bullets, enemies, player_x, player_y, gun_angle
    global game_over, player_life, game_score, bullets_missed
    global CHEAT_MODE, AUTO_FOLLOW, last_cheat_shot_time

    if game_over:
        glutPostRedisplay()
        return

    if CHEAT_MODE:
        current_time = time.time()
        closest_enemy = None
        min_dist = float('inf')

        for enemy in enemies:
            dist = math.sqrt((player_x - enemy[0])**2 + (player_y - enemy[1])**2)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
        if closest_enemy:
            dx = closest_enemy[0] - player_x
            dy = closest_enemy[1] - player_y
            target_gun_angle = math.degrees(math.atan2(dx, dy))
            if AUTO_FOLLOW:
                angle_diff = (target_gun_angle - gun_angle + 180) % 360 - 180
                gun_angle += angle_diff * SMOOTH_FACTOR
            else:
                gun_angle = (gun_angle + 2) % 360

            if current_time - last_cheat_shot_time >= CHEAT_FIRE_COOLDOWN:
                cheat_bullet_speed = 2
                bullet_vx = cheat_bullet_speed * math.sin(math.radians(target_gun_angle))
                bullet_vy = cheat_bullet_speed * math.cos(math.radians(target_gun_angle))

                bullet_x_start = player_x + 80 * math.sin(math.radians(target_gun_angle))
                bullet_y_start = player_y + 80 * math.cos(math.radians(target_gun_angle))
                bullets.append([bullet_x_start, bullet_y_start, 0, bullet_vx, bullet_vy])
                last_cheat_shot_time = current_time
                print("Plyaer Bullet Fire")
        else:
            if not AUTO_FOLLOW:
                gun_angle = (gun_angle + 2) % 360

    new_bullets = []
    for bullet in bullets:
        bullet[0] += bullet[3]
        bullet[1] += bullet[4]

        if abs(bullet[0]) > GRID_LENGTH/2 or abs(bullet[1]) > GRID_LENGTH/2:
            bullets_missed += 1
            print(f"Bullet missed: {bullets_missed}")
            if bullets_missed >= MAX_MISSED_BULLETS:
                game_over = True
        else:
            hit = False
            for i, enemy in enumerate(enemies):
                if math.sqrt((bullet[0]-enemy[0])**2 + (bullet[1]-enemy[1])**2) < 30:
                    game_score += 1
                    enemies[i] = generate_enemy_pos()
                    hit = True
                    break
            if not hit:
                new_bullets.append(bullet)
    bullets = new_bullets

    for i, enemy in enumerate(enemies):
        dx = player_x - enemy[0]
        dy = player_y - enemy[1]
        dist = math.sqrt(dx**2 + dy**2)
        move_x, move_y = 0, 0

        if dist > 0:
            move_x += (dx / dist)
            move_y += (dy / dist)

        for j, other in enumerate(enemies):
            if i != j:
                diff_x = enemy[0] - other[0]
                diff_y = enemy[1] - other[1]
                d = math.sqrt(diff_x**2 + diff_y**2)

                if d < 150 and d > 0.1:
                    strength = 10.0 / (d * d)
                    move_x += diff_x * strength
                    move_y += diff_y * strength

        length = math.sqrt(move_x**2 + move_y**2)
        if length > 0:
            move_x /= length
            move_y /= length
            enemy_speed = 0.05 if CHEAT_MODE else 0.08
            enemy[0] += move_x * enemy_speed
            enemy[1] += move_y * enemy_speed
        enemy[4] = 1.0 + 0.3 * math.sin(time.time() * 2 + i)

        if dist < 40:
            player_life -= 1
            enemies[i] = generate_enemy_pos()
            print(f"Remaining Player Life: {player_life}")
            if player_life <= 0:
                game_over = True

    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    glEnable(GL_DEPTH_TEST)
    create_grid_walls()

    if camera_mode == "first_person":
        draw_player(first_person=True)
    else:
        draw_player()
    for bullet in bullets:
        draw_bullet(bullet)
    for enemy in enemies:
        draw_enemy(enemy, enemy[4])
    if not game_over:
        draw_text(TEXT_POS["life"][0], TEXT_POS["life"][1], f"Player Life Remaining: {player_life}")
        draw_text(TEXT_POS["score"][0], TEXT_POS["score"][1], f"Game Score: {game_score}")
        draw_text(TEXT_POS["missed"][0], TEXT_POS["missed"][1], f"Player Bullet Missed: {bullets_missed}")
    else:
        draw_text(TEXT_POS["score"][0], TEXT_POS["score"][1], f"Game is Over. Your Final Score: {game_score}.", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(TEXT_POS["missed"][0], TEXT_POS["missed"][1], "Press 'R' to RESTART the game.", font=GLUT_BITMAP_HELVETICA_18)

    glutSwapBuffers()

def generate_enemy_pos():
    while True:
        x = random.uniform(-GRID_LENGTH/2 + 50, GRID_LENGTH/2 - 50)
        y = random.uniform(-GRID_LENGTH/2 + 50, GRID_LENGTH/2 - 50)
        if math.sqrt((x-player_x)**2 + (y-player_y)**2) > 200:
            return [x, y, 20, 0, 1.0]

def restart_game():
    global player_x, player_y, gun_angle, bullets, enemies, game_over, player_life, game_score, bullets_missed
    player_x, player_y, gun_angle = 0,0,0
    bullets, enemies = [], []
    game_over = False
    player_life = 5
    game_score = 0
    bullets_missed = 0
    for _ in range(5):
        enemies.append(generate_enemy_pos())

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy")
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    restart_game()
    glEnable(GL_DEPTH_TEST)
    glutMainLoop()

if __name__ == "__main__":
    main()