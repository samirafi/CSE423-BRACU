from OpenGL.GL import*
from OpenGL.GLUT import*
from OpenGL.GLU import*
import math
import random
import time

game_condition="menu"
current_lvl=1
max_lvl=3

key_pressed={'w':False,'s':False,'a':False,'d':False,'z':False,'x':False,'up':False,'down':False,'left':False,'right':False}
movement_speed=4.0
rotation_speed=2.5

cam_pos=[0,500,500]
cam_target=[0,0,0]
cam_angle_h=0
cam_angle_v=0
fp_mode=False
player_position=[0,0,50]
player_angle=0

shots_left=10
score=0
accuracy_threshold=70
time_left=240
beginning_time=0
pause_beginning_time=0

env=["Jungle of Shadows", "Cyber City Rush", "Desert of Lost Kings"]
env_description=[ "A dense jungle filled with exotic wildlife, glowing mist, and hidden ruins beneath thick vines.",
    "A futuristic city glowing with neon lights, towering skyscrapers, and fast-moving aerial traffic.",
    "A vast desert with golden dunes, ancient ruins, and scattered cacti under a blazing sun."]
current_env=0

avatar_type=["Wildlife Cameraman","Roadside Cameraman","Countryside Cameraman"]
avatar_description=["Nature specialist with stealth abilities, +10% animal bonus","Urban expert with architectural eye, +10% building bonus","Scenic master with weather resistance, +10% landscape bonus"]
avatar_color=[(0.1, 0.7, 0.1),(0.1, 0.4, 0.9),(0.8, 0.4, 0.2)]
selected_avatar=0

zoom_level=1.0
focus_mode="auto"
camera_shake=0

targets=[]
clicked_photos=[]

cheat_mode=False
auto_focus_cheat=False
cheat_rotation=0

weather_intensity=0.0
lighting="day"
weather="clear"
weather_particle_time=0

lense_unlocked={"telephoto":False,"wide_angle":False,"macro":False,"night_vision":False}
current_lense="standard"

GRID_LENGTH=1400
fovY=60

menu_animation=0
target_animation=0
environment_animation=0

class Target:
    def __init__(self,x,y,z,target_type,size=30):
        self.x=x
        self.y=y
        self.z=z
        self.original_position=[x,y,z]
        self.target_type=target_type
        self.size=size
        self.movement_pattern=random.choice(["static","circular","linear","figure8"])
        self.movement_speed=random.uniform(0.8,2.5)
        self.movement_time=0
        self.captured=False
        self.visibility=1.0
        self.pulse_scale=0.50
        self.direction=random.uniform(0,360)
        self.health=100
        self.special_properties=[]

    def update(self):
        if self.captured:
            return
        self.movement_time+=0.015
        self.pulse_scale=1.0+0.15*math.sin(self.movement_time*5)
        if self.movement_pattern=="circular":
            radius=100
            self.x=self.original_position[0]+radius*math.cos(self.movement_time*self.movement_speed)
            self.y=self.original_position[1]+radius*math.sin(self.movement_time*self.movement_speed)
        elif self.movement_pattern=="linear":
            self.x+=self.movement_speed*3*math.cos(math.radians(self.direction))
            self.y+=self.movement_speed*3*math.sin(math.radians(self.direction))
        elif self.movement_pattern=="figure8":
            t=self.movement_time*self.movement_speed
            self.x=self.original_position[0]+80*math.sin(t)
            self.y=self.original_position[1]+60*math.sin(2*t)
        #boundary check
        if abs(self.x)>GRID_LENGTH//2-80:
            self.direction=180-self.direction
            self.x=max(-GRID_LENGTH//2+80,min(GRID_LENGTH//2-80,self.x))
        if abs(self.y)>GRID_LENGTH//2-80:
            self.direction=-self.direction
            self.y=max(-GRID_LENGTH//2+80,min(GRID_LENGTH//2-80,self.y))

    def draw(self):
        if self.captured:
            return
        glPushMatrix()
        glTranslatef(self.x,self.y,self.z) #move in updated position
        glScalef(self.pulse_scale,self.pulse_scale,self.pulse_scale) #pulse effect: make it lively
        if self.target_type=="animal":
            self.draw_animal()
        elif self.target_type=="building":
            self.draw_building()
        elif self.target_type=="cactus":
            self.draw_cactus()
        elif self.target_type=="landmark":
            self.draw_landmark()
        elif self.target_type=="bird":
            self.draw_flyingbird()
        elif self.target_type=="vehicle":
            self.draw_vehicle()
        glPopMatrix()

    def draw_animal(self):
    #body
        glColor3f(0.2, 0.7, 0.2)  
        gluSphere(gluNewQuadric(), self.size, 16, 16)
    #head
        glPushMatrix()
        glTranslatef(0, self.size * 1.0, self.size * 0.5)  
        glColor3f(0.2, 0.8, 0.2)  
        gluSphere(gluNewQuadric(), self.size * 0.4, 12, 12) 
        glPopMatrix()
    #eyes
        for eye_x in [-0.15, 0.15]:
            glPushMatrix()
            glTranslatef(eye_x * self.size * 0.5, self.size * 1.1, self.size * 0.7)
            glColor3f(1, 1, 1)  # eye color 
            gluSphere(gluNewQuadric(), 4, 8, 8) 
            glTranslatef(0, 0, 2)
            glColor3f(0, 0, 0)  # Black pupils
            gluSphere(gluNewQuadric(), 2, 6, 6) 
            glPopMatrix()
    #mouth
        glPushMatrix()
        glTranslatef(0, self.size * 1.2, self.size * 0.6)  
        glColor3f(0.8, 0.2, 0.2)  
        glScalef(1.5, 0.3, 0.1) 
        gluSphere(gluNewQuadric(), 6, 8, 8)
        glPopMatrix()

    def draw_building(self):
    #body
        glColor3f(0.6, 0.6, 0.8)  
        glutSolidCube(self.size) 
    #roof
        glPushMatrix()
        glTranslatef(0, 0, self.size * 0.5)  
        glColor3f(0.8, 0.8, 0.8)  
        gluCylinder(gluNewQuadric(), self.size * 0.4, self.size * 0.4, self.size * 0.2, 8, 8)  
        glPopMatrix()
    #light on top
        glPushMatrix()
        glTranslatef(0, 0, self.size * 0.75)  
        glColor3f(1.0, 1.0, 0.0)  
        gluSphere(gluNewQuadric(), 0.1 * self.size, 8, 8)  
        glPopMatrix()
        
    def draw_cactus(self):
    #body 
        glColor3f(0.2, 0.6, 0.2)  
        gluCylinder(gluNewQuadric(), self.size * 0.3, self.size * 0.3, self.size, 12, 4) 
        for arm_offset in [0.5, -0.5]:  
            glPushMatrix()
            glTranslatef(self.size * arm_offset, 0, self.size * 0.5)  
            glRotatef(45, 0, 0, 1)  #rotation for arm
            glColor3f(0.15, 0.5, 0.15)  
            gluCylinder(gluNewQuadric(), self.size * 0.15, self.size * 0.1, self.size * 0.4, 8, 4) 
            glPopMatrix()

    def draw_landmark(self):
            glRotatef(self.movement_time * 25, 0, 0, 1)
            glPushMatrix()
            glColor3f(0.6, 0.6, 0.4)
            glScalef(2, 2, 0.2)
            glutSolidCube(self.size)
            glPopMatrix()
            segments = 6
            for i in range(segments):
                glPushMatrix()
                segment_height = self.size * 0.4
                z_offset = i * segment_height
                glTranslatef(0, 0, z_offset)
                gold_intensity = 0.8 + 0.2 * math.sin(self.movement_time * 3 + i)
                glColor3f(gold_intensity, gold_intensity * 0.8, 0.2)
                scale = 1.0 - i * 0.1
                glScalef(scale, scale, 1)
                glutSolidCube(self.size * 0.8)
                glPopMatrix()
            glPushMatrix()
            glTranslatef(0, 0, segments * self.size * 0.3)
            glRotatef(self.movement_time * 60, 1, 1, 0)
            crystal_glow = 0.7 + 0.3 * math.sin(self.movement_time * 6)
            glColor3f(0.3, crystal_glow, crystal_glow)
            glutSolidSphere(self.size * 0.4, 8, 8)
            glPopMatrix()

    def draw_flyingbird(self):
            glColor3f(0.3, 0.2, 0.1)
            glScalef(1.5, 0.8, 0.6)
            glutSolidCube(self.size * 0.5)
            wing_angle = 30 * math.sin(self.movement_time * 8) #wing flap
            for wing_side in [-1, 1]:
                glPushMatrix()
                glTranslatef(wing_side * self.size * 0.4, 0, 0)
                glRotatef(wing_angle * wing_side, 0, 1, 0)
                glColor3f(0.4, 0.3, 0.2)
                glScalef(0.8, 2, 0.1)
                glutSolidCube(self.size * 0.4)
                glPopMatrix()
            glPushMatrix()
            glTranslatef(0, self.size * 0.6, self.size * 0.2)
            glColor3f(0.35, 0.25, 0.15)
            gluSphere(gluNewQuadric(), self.size * 0.25, 8, 8) #head
            glTranslatef(0, self.size * 0.3, 0)
            glColor3f(1, 0.6, 0.2)
            gluCylinder(gluNewQuadric(), 2, 1, 8, 6, 6) #beak
            glPopMatrix()

    def draw_vehicle(self):
            glColor3f(0.2, 0.4, 0.8)
            glScalef(2, 1, 0.6)
            glutSolidCube(self.size)
            glPushMatrix()
            glTranslatef(0, 0, -self.size * 0.5)
            hover_glow = 0.5 + 0.3 * math.sin(self.movement_time * 6)
            glColor3f(0.2, hover_glow, 1.0)
            glScalef(2.2, 1.2, 0.1)
            glutSolidCube(self.size * 0.8)
            glPopMatrix()
            glColor3f(0.7, 0.9, 1.0)
            for window_x in [-0.6, 0.6]:
                glPushMatrix()
                glTranslatef(window_x * self.size, 0, self.size * 0.2)
                glScalef(0.3, 0.8, 0.4)
                glutSolidCube(self.size * 0.4)
                glPopMatrix()

def draw_player():
    glPushMatrix()

    # Position + rotation
    glTranslatef(player_position[0], player_position[1], player_position[2] + 2)
    glRotatef(player_angle + 5, 0, 0, 1)

    base_color = avatar_color[selected_avatar]

    # ---- LEGS ----
    for offset in [-7, 7]:
        glPushMatrix()
        glTranslatef(offset, 0, 0)

        glColor3f(*base_color)
        gluCylinder(gluNewQuadric(), 3.5, 2.5, 18, 10, 6)

        glTranslatef(0, 6, 0)
        glColor3f(0.08, 0.08, 0.08)
        glScalef(1.2, 1.8, 0.6)
        glutSolidCube(5)

        glPopMatrix()

    # ---- BODY ----
    glPushMatrix()
    glTranslatef(0, 0, 18)

    glColor3f(*base_color)
    gluCylinder(gluNewQuadric(), 14, 11, 28, 10, 10)

    # neck
    glTranslatef(0, 0, 14)
    glColor3f(0.35, 0.2, 0.15)
    gluCylinder(gluNewQuadric(), 13, 13, 4, 12, 4)

    glPopMatrix()

    #  ARMS 
    for side in [-20, 20]:
        glPushMatrix()
        glTranslatef(side, 0, 34)

        if side > 0:
            glRotatef(-35, 1, 0, 0)

        glColor3f(*base_color)
        gluCylinder(gluNewQuadric(), 4.5, 3.5, 18, 8, 6)

        # hand
        glTranslatef(0, 0, 18)
        glColor3f(0.85, 0.65, 0.45)
        gluSphere(gluNewQuadric(), 3.5, 8, 8)

        glPopMatrix()

    # HEAD
    glPushMatrix()
    glTranslatef(0, 0, 55)

    glColor3f(0.92, 0.72, 0.55)
    gluSphere(gluNewQuadric(), 11, 10, 10)

    glTranslatef(0, 0, 9)

    if selected_avatar == 0:
        glColor3f(0.5, 0.4, 0.25)
        gluCylinder(gluNewQuadric(), 13, 10, 6, 10, 4)

    elif selected_avatar == 1:
        glColor3f(0.15, 0.15, 0.5)
        glScalef(1.3, 0.2, 1)
        glutSolidCube(14)

    else:
        glColor3f(0.45, 0.25, 0.1)
        gluCylinder(gluNewQuadric(), 10, 8, 5, 10, 4)

    glPopMatrix()

    #  CAMERA 
    glPushMatrix()
    glTranslatef(18, -6, 33)
    glRotatef(-15, 1, 0, 0)

    glColor3f(0.12, 0.12, 0.12)
    glScalef(1.3, 1, 1)
    glutSolidCube(7)

    # lens
    glTranslatef(5, 0, 0)
    glRotatef(90, 0, 1, 0)

    if current_lense == "telephoto":
        gluCylinder(gluNewQuadric(), 3.5, 2.5, 18, 10, 10)
    elif current_lense == "wide_angle":
        gluCylinder(gluNewQuadric(), 5, 3.5, 7, 10, 10)
    else:
        gluCylinder(gluNewQuadric(), 4, 4, 10, 10, 10)

    glColor3f(0.05, 0.05, 0.25)
    gluDisk(gluNewQuadric(), 0, 3.5, 10, 4)

    glPopMatrix()

    # ---- BACKPACK ----
    glPushMatrix()
    glTranslatef(0, -16, 34)

    glColor3f(0.25, 0.25, 0.25)
    glScalef(0.9, 1.1, 1.3)
    glutSolidCube(14)

    glColor3f(0.1, 0.1, 0.1)
    for y in [-7, 0, 7]:
        glPushMatrix()
        glTranslatef(0, y, 7)
        glutSolidCube(2.5)
        glPopMatrix()

    glPopMatrix()

    glPopMatrix()

def init_targets():
    global targets
    targets=[]
    if current_env==0:
        target_configs=[("animal","ground"),("animal","tree"),("bird","flying"),("landmark","mystical"),("animal","water")]
    elif current_env==1:
        target_configs=[("building","skyscraper"),("vehicle","hover"),("building","neon"),("landmark","tech"),("bird","drone")]
    else:
        target_configs=[("cactus","giant"),("animal","desert"),("landmark","ruins"),("cactus","flowering"),("bird","eagle")]
    for i,(target_type,subtype) in enumerate(target_configs):
        if i==0:
            x,y=0,0
        else:
            angle=(i-1)*90+random.uniform(-30,30)
            radius=random.randint(180,320)
            x=radius*math.cos(math.radians(angle))
            y=radius*math.sin(math.radians(angle))
        z=random.randint(50,120) if target_type!="bird" else random.randint(80,200)
        target=Target(x,y,z,target_type,random.randint(25,40))
        target.subtype=subtype
        targets.append(target)

def draw_env():
    glBegin(GL_QUADS)
    tile_size=50
    tiles_per_side=int(GRID_LENGTH/tile_size)
    for i in range(-tiles_per_side//2,tiles_per_side//2):
        for j in range(-tiles_per_side//2,tiles_per_side//2):
            if current_env==0:
                base_color=(0.1,0.3,0.1) if (i+j)%2==0 else (0.2,0.4,0.2)
                moss_variation=0.05*math.sin(i*0.5)*math.cos(j*0.3)
                glColor3f(base_color[0]+moss_variation,base_color[1]+moss_variation,base_color[2])
            elif current_env==1:
                if (i+j)%2==0:
                    glColor3f(0.35,0.35,0.4)
                else:
                    glColor3f(0.45,0.45,0.5)
            else:
                sand_r=0.85+0.05*math.sin(i*0.3+j*0.4)
                sand_g=0.75+0.05*math.cos(i*0.2+j*0.5)
                sand_b=0.4+0.03*math.sin(i*0.4+j*0.2)
                glColor3f(sand_r,sand_g,sand_b)
            x1,y1=i*tile_size,j*tile_size
            x2,y2=x1+tile_size,y1+tile_size
            height_var=2*math.sin(i*0.2)*math.cos(j*0.15)
            glVertex3f(x1,y1,height_var)
            glVertex3f(x2,y1,height_var)
            glVertex3f(x2,y2,height_var)
            glVertex3f(x1,y2,height_var)
    glEnd()
    glColor3f(0.25,0.25,0.3)
    wall_height=70
    wall_thickness=15
    for wall_side in range(4):
        glPushMatrix()
        if wall_side==0:
            glTranslatef(0,GRID_LENGTH//2,wall_height//2)
            glScalef(GRID_LENGTH,wall_thickness,wall_height)
        elif wall_side==1:
            glTranslatef(0,-GRID_LENGTH//2,wall_height//2)
            glScalef(GRID_LENGTH,wall_thickness,wall_height)
        elif wall_side==2:
            glTranslatef(GRID_LENGTH//2,0,wall_height//2)
            glScalef(wall_thickness,GRID_LENGTH,wall_height)
        else:
            glTranslatef(-GRID_LENGTH//2,0,wall_height//2)
            glScalef(wall_thickness,GRID_LENGTH,wall_height)
        glutSolidCube(1)
        glPopMatrix()

def process_key_input():
    global player_position,player_angle,cam_angle_h,cam_angle_v,zoom_level
    if game_condition!="playing":
        return
    if key_pressed['w']:
        move_x=movement_speed*math.cos(math.radians(player_angle))
        move_y=movement_speed*math.sin(math.radians(player_angle))
        new_x=player_position[0]+move_x
        new_y=player_position[1]+move_y
        max_pos=GRID_LENGTH//2-60
        if abs(new_x)<max_pos:
            player_position[0]=new_x
        if abs(new_y)<max_pos:
            player_position[1]=new_y
    if key_pressed['s']:
        move_x=movement_speed*math.cos(math.radians(player_angle))
        move_y=movement_speed*math.sin(math.radians(player_angle))
        new_x=player_position[0]-move_x
        new_y=player_position[1]-move_y
        max_pos=GRID_LENGTH//2-60
        if abs(new_x)<max_pos:
            player_position[0]=new_x
        if abs(new_y)<max_pos:
            player_position[1]=new_y
    if key_pressed['a'] and not cheat_mode:
        player_angle+=rotation_speed
    if key_pressed['d'] and not cheat_mode:
        player_angle-=rotation_speed
    if key_pressed['up']:
        cam_angle_v=min(80,cam_angle_v+1.0)
    if key_pressed['down']:
        cam_angle_v=max(-80,cam_angle_v-1.0)
    if key_pressed['left']:
        cam_angle_h+=1.5
    if key_pressed['right']:
        cam_angle_h-=1.5
    if key_pressed['z']:
        zoom_level=min(5.0,zoom_level+0.02)
    if key_pressed['x']:
        zoom_level=max(0.3,zoom_level-0.02)

def draw_cam_viewfinder():  #creates a realistic camera simulation overlay
    #It draws a camera-style on-screen interface with framing guides, focus indicator, zoom/lens info, and UI overlays on top of your scene.
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,1000,0,800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glLineWidth(2)
    glColor3f(0.8,0.8,0.8)
    glBegin(GL_LINES)
    glVertex2f(400,250)
    glVertex2f(400,550)
    glVertex2f(600,250)
    glVertex2f(600,550)
    glVertex2f(350,350)
    glVertex2f(650,350)
    glVertex2f(350,450)
    glVertex2f(650,450)
    glEnd()
    glLineWidth(3)
    if auto_focus_cheat or focus_mode=="manual":
        glColor3f(0.2,1.0,0.2)
    else:
        glColor3f(1.0,1.0,0.2)
    glBegin(GL_LINES)
    glVertex2f(485,400)
    glVertex2f(515,400)
    glVertex2f(500,385)
    glVertex2f(500,415)
    glEnd()
    glLineWidth(4)
    glColor3f(0.9,0.9,0.9)
    corner_size=40
    frame_positions=[(350,550),(650,550),(650,250),(350,250)]
    for i,(fx,fy) in enumerate(frame_positions):
        glBegin(GL_LINES)
        if i==0:
            glVertex2f(fx,fy)
            glVertex2f(fx+corner_size,fy)
            glVertex2f(fx,fy)
            glVertex2f(fx,fy-corner_size)
        elif i==1:
            glVertex2f(fx,fy)
            glVertex2f(fx-corner_size,fy)
            glVertex2f(fx,fy)
            glVertex2f(fx,fy-corner_size)
        elif i==2:
            glVertex2f(fx,fy)
            glVertex2f(fx-corner_size,fy)
            glVertex2f(fx,fy)
            glVertex2f(fx,fy+corner_size)
        else:
            glVertex2f(fx,fy)
            glVertex2f(fx+corner_size,fy)
            glVertex2f(fx,fy)
            glVertex2f(fx,fy+corner_size)
        glEnd()
    glColor3f(0.9,0.9,0.9)
    draw_text(360,580,f"Zoom:{zoom_level:.1f}x")
    draw_text(540,580,f"Lens:{current_lense.title()}")
    if focus_mode=="manual":
        draw_text(360,230,"Manual Focus")
    else:
        draw_text(360,230,"Auto Focus")
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def calc_photo_score(target):
    
    dx=target.x-player_position[0]
    dy=target.y-player_position[1]
    dz=target.z-player_position[2]
    distance=math.sqrt(dx*dx+dy*dy+dz*dz)
    
    target_angle_h=math.degrees(math.atan2(dy,dx))
    if target_angle_h<0:
        target_angle_h+=360
    target_angle_v=math.degrees(math.atan2(dz,math.sqrt(dx*dx+dy*dy)))
    current_angle_h=player_angle%360
    if current_angle_h<0:
        current_angle_h+=360
    angle_difference_h=abs(target_angle_h-current_angle_h)
    if angle_difference_h>180:
        angle_difference_h=360-angle_difference_h
    angle_difference_v=abs(target_angle_v-cam_angle_v)
    total_angle_diffrence=math.sqrt(angle_difference_h**2+(angle_difference_v*0.5)**2)
    if total_angle_diffrence<=3:
        accuracy=100
    elif total_angle_diffrence<=8:
        accuracy=95
    elif total_angle_diffrence<=15:
        accuracy=85
    elif total_angle_diffrence<=25:
        accuracy=75
    elif total_angle_diffrence<=40:
        accuracy=60
    else:
        accuracy=35
    optimal_distances={"standard":(120,280),"telephoto":(200,450),"wide_angle":(80,200),"macro":(50,150)}
    dmin, dmax = optimal_distances.get(current_lense, (120, 280))
    if distance < dmin: #penalty
        distance_score = max(0, 100 - (dmin - distance) * 0.35)
    elif distance > dmax:  #penalty
        distance_score = max(0, 100 - (distance - dmax) * 0.25)
    else:
        distance_score = 100  #perfectos 

    # bonus
    bonus_point = 0 if auto_focus_cheat else 5

    # combine
    score = 0.65 * accuracy + 0.35 * distance_score + bonus_point
    return int(max(0, min(100, score)))

def keyboardListener(key,x,y):
    global zoom_level,focus_mode,cheat_mode,auto_focus_cheat
    global selected_avatar,game_condition,beginning_time,player_position,player_angle
    global current_lense,fp_mode,pause_beginning_time
    key_char=key.decode('utf-8').lower() if isinstance(key,bytes) else key.lower()
    if key_char in ['w','s','a','d','z','x']:
        key_pressed[key_char]=True
    if key_char=='q':
        print("Thank you for playing Snapshot Safari!!")
        glutLeaveMainLoop()
        return
    if game_condition=="menu":
        if key==b'\r':
            game_condition="avatar_select"
        elif key_char=='i':
            game_condition="instructions"
        elif key_char=='a':
            game_condition="avatar_select"
        elif key_char=='g':
            game_condition="gallery"
    elif game_condition=="instructions":
        if key_char=='m':
            game_condition="menu"
        elif key_char=='a':
            game_condition="avatar_select"
    elif game_condition=="avatar_select":
        if key_char in ['1','2','3']:
            selected_avatar=int(key_char)-1
        elif key==b' ':
            reset()
        elif key_char=='m':
            game_condition="menu"
    elif game_condition=="playing":
        if key_char=='p':
            game_condition="paused"
            pause_beginning_time=time.time()
        elif key_char=='f':
            focus_mode="manual" if focus_mode=="auto" else "auto"
        elif key_char=='l':
            lenses=["standard"]
            if lense_unlocked["telephoto"]:
                lenses.append("telephoto")
            if lense_unlocked["wide_angle"]:
                lenses.append("wide_angle")
            if lense_unlocked["macro"]:
                lenses.append("macro")
            current_idx=lenses.index(current_lense) if current_lense in lenses else 0
            current_lense=lenses[(current_idx+1)%len(lenses)]
        elif key_char=='c':
            cheat_mode=not cheat_mode
            if not cheat_mode:
                auto_focus_cheat=False
        elif key_char=='v':
            if cheat_mode:
                auto_focus_cheat=not auto_focus_cheat
        elif key_char=='i':
            game_condition="instructions"
        elif key_char=='t':
            fp_mode=not fp_mode
    elif game_condition=="paused":
        if key_char=='p':
            game_condition="playing"
            if pause_beginning_time>0:
                pause_duration=time.time()-pause_beginning_time
                beginning_time+=pause_duration
        elif key_char=='n':
            lighting_change()
        elif key_char=='m':
            game_condition="menu"
        elif key_char=='r':
            reset()
    elif game_condition in ["game_over","victory"]:
        if key_char=='r':
            reset()
        elif key_char=='g':
            game_condition="gallery"
        elif key_char=='m':
            game_condition="menu"
    elif game_condition=="gallery":
        if key_char=='m':
            game_condition="menu"
        elif key_char=='r':
            reset()

def keyboardUpListener(key,x,y):
    key_char=key.decode('utf-8').lower() if isinstance(key,bytes) else key.lower()
    if key_char in key_pressed:
        key_pressed[key_char]=False

def specialKeyListener(key,x,y):
    if key==GLUT_KEY_UP:
        key_pressed['up']=True
    elif key==GLUT_KEY_DOWN:
        key_pressed['down']=True
    elif key==GLUT_KEY_LEFT:
        key_pressed['left']=True
    elif key==GLUT_KEY_RIGHT:
        key_pressed['right']=True

def specialKeyUpListener(key,x,y):
    if key==GLUT_KEY_UP:
        key_pressed['up']=False
    elif key==GLUT_KEY_DOWN:
        key_pressed['down']=False
    elif key==GLUT_KEY_LEFT:
        key_pressed['left']=False
    elif key==GLUT_KEY_RIGHT:
        key_pressed['right']=False

def mouseListener(button,state,x,y):
    global fp_mode
    if game_condition=="playing":
        if button==GLUT_LEFT_BUTTON and state==GLUT_DOWN:
            click_photo()
        elif button==GLUT_RIGHT_BUTTON and state==GLUT_DOWN:
            fp_mode=not fp_mode

def click_photo():
    global shots_left,score,camera_shake
    if shots_left<=0 or game_condition!="playing":
        return
    shots_left-=1
    camera_shake=10
    best_score=0
    best_target=None
    for target in targets:
        if not target.captured:
            photo_score=calc_photo_score(target)
            if photo_score>best_score:
                best_score=photo_score
                best_target=target
    if best_target and best_score>=45:
        best_target.captured=True
        score+=best_score
        clicked_photos.append({'target':best_target.target_type,'score':best_score,'environment':env[current_env],'weather':weather,'lighting':lighting,'lens':current_lense,'zoom':zoom_level})
        if best_score>=95 and not lense_unlocked["telephoto"]:
            lense_unlocked["telephoto"]=True
        if best_score>=90 and current_lvl>=2 and not lense_unlocked["wide_angle"]:
            lense_unlocked["wide_angle"]=True
        if best_score>=85 and current_lvl>=3 and not lense_unlocked["macro"]:
            lense_unlocked["macro"]=True
    captured_count=len([t for t in targets if t.captured])
    total_possible_score=len(targets)*80
    if captured_count>=4 or all(target.captured for target in targets):
        advanced_level()
    elif shots_left==0:
        if captured_count>=3 and score>=total_possible_score*0.6:
            advanced_level()
        else:
            game_over()

def advanced_level():
    global current_lvl,shots_left,current_env,time_left,beginning_time
    current_lvl+=1
    if current_lvl>max_lvl:
        victory()
        return
    current_env=(current_env+1)%3
    shots_left=12
    time_left=200
    beginning_time=time.time()
    player_position[0]=0
    player_position[1]=0
    player_position[2]=30
    player_angle=0
    init_targets()
    updated_weather()

def Camera_setup():
    global fovY,camera_shake
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    base_fov=fovY/zoom_level #zoom in effect
    lens_modifiers={"standard":1.0,"telephoto":0.3,"wide_angle":1.5,"macro":0.8}
    effective_fov=base_fov*lens_modifiers.get(current_lense,1.0)
    gluPerspective(effective_fov,1.25,0.1,3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    shake_x=shake_y=shake_z=0
    if camera_shake>0:
        shake_intensity=camera_shake*0.8
        shake_x=shake_intensity*(random.random()-0.5)
        shake_y=shake_intensity*(random.random()-0.5)
        shake_z=shake_intensity*0.3*(random.random()-0.5)
        camera_shake*=0.88
    if fp_mode:
        eye_height=55
        eye_x=player_position[0]+shake_x
        eye_y=player_position[1]+shake_y
        eye_z=player_position[2]+eye_height+shake_z
        look_distance=500
        look_x=eye_x+look_distance*math.cos(math.radians(player_angle))
        look_y=eye_y+look_distance*math.sin(math.radians(player_angle))
        look_z=eye_z+look_distance*math.tan(math.radians(cam_angle_v))
        gluLookAt(eye_x,eye_y,eye_z,look_x,look_y,look_z,0,0,1)
    else:
        base_distance=400
        distance=base_distance/(zoom_level*0.5+0.5)
        height=280+cam_angle_v*6
        cam_angle=player_angle+cam_angle_h
        cam_x=player_position[0]-distance*math.cos(math.radians(cam_angle))+shake_x
        cam_y=player_position[1]-distance*math.sin(math.radians(cam_angle))+shake_y
        cam_z=height+shake_z
        target_x=player_position[0]+30*math.cos(math.radians(player_angle))
        target_y=player_position[1]+30*math.sin(math.radians(player_angle))
        target_z=player_position[2]+35
        gluLookAt(cam_x,cam_y,cam_z,target_x,target_y,target_z,0,0,1)


def updated_game_timer():
    global time_left,game_condition,beginning_time
    if game_condition=="playing" and beginning_time>0:
        current_time=time.time()
        time_passed=current_time-beginning_time
        time_left=max(0,200-time_passed)
        if time_left<=0:
            captured_count=len([t for t in targets if t.captured])
            if captured_count>=2:
                time_left=60
                beginning_time=time.time()
            else:
                game_over()

def updated_target():
    if game_condition!="playing":
        return
    updated_cheat_mode()
    for target in targets:
        target.update()
        boundary=GRID_LENGTH//2-100
        if abs(target.x)>boundary:
            if hasattr(target,'direction'):
                target.direction=180-target.direction
            target.x=max(-boundary,min(boundary,target.x))
        if abs(target.y)>boundary:
            if hasattr(target,'direction'):
                target.direction=-target.direction
            target.y=max(-boundary,min(boundary,target.y))

def updated_cheat_mode():
    global cheat_rotation,player_angle
    if cheat_mode and game_condition=="playing":
        nearest_target=None
        nearest_distance=float('inf')
        for target in targets:
            if not target.captured:
                dx=target.x-player_position[0]
                dy=target.y-player_position[1]
                distance=math.sqrt(dx*dx+dy*dy)
                if distance<nearest_distance:
                    nearest_distance=distance
                    nearest_target=target
        if nearest_target:
            dx=nearest_target.x-player_position[0]
            dy=nearest_target.y-player_position[1]
            target_angle=math.degrees(math.atan2(dy,dx))
            angle_diff=target_angle-player_angle
            while angle_diff>180:angle_diff-=360
            while angle_diff<-180:angle_diff+=360
            if abs(angle_diff)>2:player_angle+=4*(1 if angle_diff>0 else -1)
            if abs(angle_diff)<=8 and nearest_distance<350 and shots_left>0:
                if int(time.time()*2)%2==0:click_photo()

def reset():
    global game_condition,current_lvl,shots_left,score,current_env
    global time_left,clicked_photos,beginning_time,player_position,player_angle
    global cheat_mode,auto_focus_cheat,fp_mode,zoom_level,cam_angle_h,cam_angle_v
    game_condition="playing"
    current_lvl=1
    current_env=0
    shots_left=12
    score=0
    time_left=200
    beginning_time=time.time()
    clicked_photos=[]
    player_position=[0,0,30]
    player_angle=0
    cam_angle_h=0
    cam_angle_v=0
    cheat_mode=False
    auto_focus_cheat=False
    fp_mode=False
    zoom_level=1.0
    for key in key_pressed:key_pressed[key]=False
    init_targets()
    updated_weather()

def updated_weather():
    global weather,lighting
    if current_env==0:
        weather_preferences=["clear","rain","fog"]
        weather_intensity=[0.4,0.4,0.2]
    elif current_env==1:
        weather_preferences=["clear","fog","rain","snow"]
        weather_intensity=[0.4,0.25,0.25,0.1]
    else:
        weather_preferences=["clear","sandstorm"]
        weather_intensity=[0.7,0.3]
    weather=random.choices(weather_preferences,weights=weather_intensity)[0]
    lighting_option=["day","golden_hour","dawn","dusk","night"]
    lighting_weights=[0.4,0.25,0.15,0.15,0.05]
    lighting=random.choices(lighting_option,weights=lighting_weights)[0]
    
def lighting_change():
    global lighting
    choices = ["day", "golden_hour", "dawn", "dusk", "night"]
    try:
        i = choices.index(lighting)
    except ValueError:
        i = 0
    lighting = choices[(i + 1) % len(choices)]

def draw_headsup_display():
    glColor3f(1,1,1)
    draw_text(10,720,f"Environment:{env[current_env]}")
    avatar_name=avatar_type[selected_avatar].split()[0]
    glColor3f(*avatar_color[selected_avatar])
    draw_text(10,700,f"Photographer:{avatar_name}")
    if shots_left>8:glColor3f(0.4,1,0.4)
    elif shots_left>4:glColor3f(1,1,0.4)
    else:glColor3f(1,0.4,0.4)
    draw_text(10,680,f"Shots:{shots_left}/12")
    glColor3f(0.7,1,0.7)
    draw_text(10,660,f"Score:{score}")
    if clicked_photos:
        avg_score=score/len(clicked_photos)
        if avg_score>=85:glColor3f(1,1,0.3)
        elif avg_score>=70:glColor3f(0.8,1,0.8)
        else:glColor3f(1,0.8,0.8)
        draw_text(10,640,f"(Avg:{avg_score:.0f}%)")
    minutes=int(time_left//60)
    seconds=int(time_left%60)
    if time_left>120:glColor3f(0.4,1,0.4)
    elif time_left>60:glColor3f(1,1,0.4)
    else:glColor3f(1,0.4,0.4)
    draw_text(10,620,f"Time:{minutes:02d}:{seconds:02d}")
    glColor3f(1,1,1)
    draw_text(10,600,f"Level:{current_lvl}/{max_lvl}")
    captured_count=len([t for t in targets if t.captured])
    progress=captured_count/len(targets)
    glColor3f(0.3,0.3,0.3)
    glBegin(GL_QUADS)
    glVertex2f(10,615)
    glVertex2f(160,615)
    glVertex2f(160,625)
    glVertex2f(10,625)
    glEnd()
    if progress>0.8:glColor3f(0.2,1,0.2)
    elif progress>0.6:glColor3f(1,1,0.2)
    else:glColor3f(1,0.4,0.4)
    glBegin(GL_QUADS)
    glVertex2f(10,615)
    glVertex2f(10+150*progress,615)
    glVertex2f(10+150*progress,625)
    glVertex2f(10,625)
    glEnd()
    glColor3f(0.4,0.8,1)
    draw_text(10,580,f"Targets:{captured_count}/{len(targets)}")
    glColor3f(0.7,1,0.7)
    draw_text(750,720,f"Zoom:{zoom_level:.1f}x")
    draw_text(750,700,f"Focus:{focus_mode.title()}")
    draw_text(750,680,f"Lens:{current_lense.title()}")
    if fp_mode:glColor3f(0.4,1,1);draw_text(750,660,"First Person View")
    else:glColor3f(1,0.7,0.7);draw_text(750,660,"Third Person View")
    if cheat_mode:
        glColor3f(1,0.2,0.2)
        draw_text(300,80,"CHEAT MODE: AUTO-AIM ACTIVE")
        if auto_focus_cheat:draw_text(320,55,"AUTO FOCUS ENABLED")
    glColor3f(1,1,1)
    draw_text(10,40,"WASD=Move|Arrows=Camera|Click=Photo|T=View|P=Pause|Q=Quit")
    draw_text(10,20,"F=Focus|L=Lens|Z/X=Zoom|C=Cheat|I=Help")

def draw_menu():
    global menu_animation
    menu_animation+=0.03
    title_y=680+12*math.sin(menu_animation*1.5)
    for i,char in enumerate("SNAPSHOT SAFARI"):
        char_offset=4*math.sin(menu_animation*3+i*0.3)
        color_cycle=0.7+0.3*math.sin(menu_animation*2+i*0.5)
        glColor3f(color_cycle,0.8,1.0)
        draw_text(250+i*35,title_y+char_offset,char)
    glColor3f(0.8,1,0.8)
    subtitle_y=630+6*math.sin(menu_animation*2) 
    draw_text(350,subtitle_y,"THE PERFECT SHOT")
    glColor3f(1,1,1)
    draw_text(300,580,"Master the art of photography across mystical worlds")
    draw_text(320,550,"Choose your avatar and explore stunning environments")
    draw_text(340,520,"Capture perfect moments to progress through levels")
    menu_options=[("Press 'I' for Instructions",(1,1,0.6)),("Press 'A' for Avatar Selection",(0.6,1,1)),("Press 'G' for Photo Gallery",(1,0.6,1)),("Press ENTER to Begin Adventure!",(0.8,1,0.4))]
    for i,(option_text,color) in enumerate(menu_options):
        pulse=0.7+0.3*math.sin(menu_animation*4+i*0.8)
        glColor3f(color[0]*pulse,color[1]*pulse,color[2]*pulse)
        option_y=420-i*45
        draw_text(320,option_y,option_text)
    preview_offset=25*math.cos(menu_animation*1.2)
    glColor3f(0.7,0.9,1)
    draw_text(250+preview_offset,180,f"Next Adventure:{env[0]}")
    draw_text(280+preview_offset,155,env_description[0])
    glColor3f(0.5,0.5,0.5)
    draw_text(10,10,"Snapshot Safari - Press Q to Quit")

def draw_avatar_selection():
    draw_text(320,720,"CHOOSE YOUR PHOTOGRAPHY SPECIALIST")
    for i in range(3):
        y_base=620-i*150
        if i==selected_avatar:
            glow=0.8+0.2*math.sin(menu_animation*4)
            glColor3f(1,1,0.2)
            glLineWidth(4)
            glBegin(GL_LINE_LOOP)
            border_expand=5*math.sin(menu_animation*6)
            glVertex2f(60-border_expand,y_base+50)
            glVertex2f(680+border_expand,y_base+50)
            glVertex2f(680+border_expand,y_base-80)
            glVertex2f(60-border_expand,y_base-80)
            glEnd()
            glColor3f(glow,glow,0.4)
            draw_text(80,y_base+60,">>> SELECTED PHOTOGRAPHER <<<")
        glColor3f(*avatar_color[i])
        glBegin(GL_QUADS)
        glVertex2f(80,y_base+20)
        glVertex2f(150,y_base+20)
        glVertex2f(150,y_base-20)
        glVertex2f(80,y_base-20)
        glEnd()
        glColor3f(0.1,0.1,0.1)
        glBegin(GL_QUADS)
        glVertex2f(120,y_base+5)
        glVertex2f(140,y_base+5)
        glVertex2f(140,y_base-5)
        glVertex2f(120,y_base-5)
        glEnd()
        glColor3f(1,1,1)
        draw_text(170,y_base+5,f"{i+1}. {avatar_type[i]}")
        glColor3f(0.8,0.8,0.8)
        draw_text(170,y_base-20,avatar_description[i])
        specializations = [ "Specializes in wildlife tracking, stealth movement, and natural composition",
                           "Specializes in architectural framing, urban lighting, and street photography",
                           "Specializes in scenic composition, adapting to weather, and capturing landmarks"]
        glColor3f(0.6,0.8,0.6)
        draw_text(170,y_base-45,specializations[i])
    nav_glow=0.8+0.2*math.sin(menu_animation*5)
    glColor3f(nav_glow,0.8,0.4)
    draw_text(200,120,"Press 1/2/3 to select your specialist")
    draw_text(280,90,"Press ENTER to begin your journey")
    draw_text(320,60,"Press M for Main Menu|Q to Quit")

def draw_gallery():
    draw_text(380,750,"PROFESSIONAL PORTFOLIO")
    if not clicked_photos:
        glColor3f(0.8,0.8,1)
        draw_text(280,400,"Your portfolio awaits your first masterpiece!")
        draw_text(250,370,"Complete photography missions to build your collection")
        glColor3f(0.6,0.6,0.6)
        draw_text(200,320,"Gallery will showcase:")
        draw_text(220,295,"• Photo quality ratings and technical details")
        draw_text(220,270,"• Environmental conditions during capture")
        draw_text(220,245,"• Equipment used and camera settings")
        draw_text(220,220,"• Professional photographer ranking")
    else:
        total_photos=len(clicked_photos)
        total_score=sum(photo['score'] for photo in clicked_photos)
        avg_score=total_score/total_photos
        glColor3f(0.7,1,0.7)
        draw_text(50,700,f"Portfolio Summary:{total_photos} Photos|Average Score:{avg_score:.1f}%")
        if avg_score>=90:glColor3f(1,1,0.2);rating="★★★ MASTER PHOTOGRAPHER ★★★"
        elif avg_score>=80:glColor3f(0.9,0.9,1);rating="★★ PROFESSIONAL PHOTOGRAPHER ★★"
        elif avg_score>=70:glColor3f(0.8,1,0.8);rating="★ SKILLED PHOTOGRAPHER ★"
        else:glColor3f(1,0.8,0.8);rating="AMATEUR PHOTOGRAPHER"
        draw_text(250,670,rating)
        y_pos=630
        for i,photo in enumerate(clicked_photos):
            if y_pos<180:
                remaining=len(clicked_photos)-i
                glColor3f(0.6,0.6,0.6)
                draw_text(50,y_pos,f"... and {remaining} more photos")
                break
            if photo['score']>=90:glColor3f(1,1,0.2);medal="★★★"
            elif photo['score']>=80:glColor3f(0.9,0.9,0.9);medal="★★"
            elif photo['score']>=70:glColor3f(0.8,0.5,0.2);medal="★"
            else:glColor3f(1,1,1);medal=""
            draw_text(50,y_pos,f"{i+1}.{photo['environment']}-{photo['target'].title()} {medal}")
            draw_text(400,y_pos,f"{photo['score']}%")
            glColor3f(0.7,0.7,0.7)
            conditions=f"{photo['lens'].title()} lens"
            if photo['zoom']!=1.0:conditions+=f",{photo['zoom']:.1f}x zoom"
            draw_text(480,y_pos,conditions)
            glColor3f(0.6,0.8,0.8)
            env_conditions=photo['weather'].title()
            if photo['lighting']!="day":env_conditions+=f",{photo['lighting'].replace('_',' ').title()}"
            draw_text(50,y_pos-15,env_conditions)
            y_pos-=45
    glColor3f(1,0.8,0.4)
    draw_text(250,80,"Press M for Menu|Press R to Start New Adventure|Q to Quit")



def draw_pause():
    glColor3f(0.2,0.2,0.2)
    glBegin(GL_QUADS)
    glVertex2f(0,0)
    glVertex2f(1000,0)
    glVertex2f(1000,800)
    glVertex2f(0,800)
    glEnd()
    pulse=0.8+0.2*math.sin(menu_animation*6)
    glColor3f(pulse,pulse,0.4)
    draw_text(420,450,"GAME PAUSED")
    glColor3f(1,1,1)
    draw_text(350,400,"Press P to Resume")
    draw_text(340,370,"Press M for Main Menu")
    draw_text(350,340,"Press R to Restart")
    draw_text(350,310,"Press N to Change Lighting")
    draw_text(380,280,"Press Q to Quit")
    glColor3f(0.8,0.8,0.8)
    draw_text(300,220,f"Current Level:{current_lvl}")
    draw_text(320,190,f"Score:{score}")
    draw_text(290,160,f"Photos Taken:{len(clicked_photos)}")
    colors={"day":(1,1,0.8),"golden_hour":(1,1,0.4),"dawn":(1,0.8,0.6),"dusk":(0.9,0.6,0.8),"night":(0.6,0.6,1)}
    glColor3f(*colors.get(lighting,(1,1,1)))
    draw_text(280,130,f"Current Lighting:{lighting.replace('_',' ').title()}")

def idle_status():
    global menu_animation,target_animation,environment_animation
    menu_animation+=0.02
    target_animation+=0.03
    environment_animation+=0.015
    process_key_input()
    updated_game_timer()
    updated_target()
    updated_camera_position()
    glutPostRedisplay()

def updated_camera_position():
    global camera_shake
    if camera_shake>0:
        camera_shake*=0.85
        if camera_shake<0.1:camera_shake=0

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0,0,1000,800)
    if game_condition=="playing":
        if lighting=="night":glClearColor(0.02,0.02,0.15,1)
        elif lighting=="golden_hour":glClearColor(1,0.8,0.4,1)
        elif lighting=="dawn":glClearColor(0.9,0.7,0.6,1)
        elif lighting=="dusk":glClearColor(0.7,0.4,0.6,1)
        else:glClearColor(0.5,0.7,1,1)
    else:
        bg=0.05+0.02*math.sin(menu_animation)
        glClearColor(bg,bg+0.05,bg+0.15,1)
    if game_condition=="menu":draw_menu()
    elif game_condition=="instructions":draw_instruction()
    elif game_condition=="avatar_select":draw_avatar_selection()
    elif game_condition=="playing":
        Camera_setup()
        draw_env()
        if not fp_mode:draw_player()
        for t in targets:t.draw()
        if fp_mode:draw_cam_viewfinder()
        draw_headsup_display()
    elif game_condition=="paused":
        Camera_setup()
        glColor3f(0.3,0.3,0.3)
        draw_env()
        if not fp_mode:draw_player()
        for t in targets:t.draw()
        draw_pause()
    elif game_condition=="game_over":draw_game_over()
    elif game_condition=="victory":draw_win()
    elif game_condition=="gallery":draw_gallery()
    glutSwapBuffers()

def draw_text(x,y,text,font=GLUT_BITMAP_HELVETICA_18): #switches to a 2D mode, prints the text, then restores everything back
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,1000,0,800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x,y)
    for c in text:glutBitmapCharacter(font,ord(c))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def game_over():global game_condition;game_condition="game_over"
def victory():global game_condition;game_condition="victory"

def draw_game_over():
    glColor3f(1,0.4,0.4);draw_text(350,600,"MISSION INCOMPLETE")
    glColor3f(1,1,1)
    draw_text(320,540,f"Final Score:{score}")
    draw_text(270,510,f"Photos Captured:{len(clicked_photos)}")
    draw_text(290,480,f"Level Reached:{current_lvl}")
    glColor3f(0.8,1,0.8);draw_text(320,440,"Performance Analysis:")
    if len(clicked_photos)==0:
        glColor3f(1,0.6,0.6)
        draw_text(200,410,"No photos captured - practice aiming with the crosshair!")
        draw_text(230,385,"Try using cheat mode (C) to learn targeting")
    elif len(clicked_photos)<3:
        glColor3f(1,0.8,0.6)
        draw_text(220,410,"Good start! Try capturing more targets per level")
        draw_text(260,385,"Use different lenses and zoom for better shots")
    else:
        avg=score/len(clicked_photos)
        if avg<65:glColor3f(1,1,0.6);draw_text(180,410,"Good quantity! Focus on accuracy and composition");draw_text(210,385,"Try manual focus and optimal zoom levels")
        else:glColor3f(0.6,1,0.6);draw_text(280,410,"Excellent photography skills!");draw_text(300,385,"Keep practicing for mastery")
    glColor3f(0.8,1,0.8)
    draw_text(320,320,"Press R to Try Again")
    draw_text(310,290,"Press G for Photo Gallery")
    draw_text(320,260,"Press M for Main Menu")
    draw_text(360,230,"Press Q to Quit")

def draw_win():
    global menu_animation
    y=600+15*math.sin(menu_animation*2.5)
    colors=[(1,0.2,0.2),(1,0.8,0.2),(1,1,0.2),(0.2,1,0.2),(0.2,0.2,1),(0.8,0.2,1),(1,0.2,0.8)]
    text="PHOTOGRAPHY MASTER!"
    for i,c in enumerate(text):
        clr=colors[i%len(colors)]
        pulse=0.8+0.2*math.sin(menu_animation*4+i*0.2)
        glColor3f(clr[0]*pulse,clr[1]*pulse,clr[2]*pulse)
        offset=8*math.sin(menu_animation*6+i*0.4)
        draw_text(280+i*25,y+offset,c)
    glColor3f(0.4,1,0.4)
    draw_text(200,520,"All environments conquered! You are a true professional!")
    glColor3f(1,1,1)
    draw_text(320,480,f"Total Score:{score}")
    draw_text(300,450,f"Photos Taken:{len(clicked_photos)}")
    if clicked_photos:
        avg=score/len(clicked_photos)
        perfect=len([p for p in clicked_photos if p['score']>=95])
        excellent=len([p for p in clicked_photos if p['score']>=85])
        glColor3f(0.8,1,0.8)
        draw_text(280,410,f"Average Quality:{avg:.1f}%")
        draw_text(300,385,f"Perfect Shots:{perfect}")
        draw_text(290,360,f"Excellent Shots:{excellent}")
        if avg>=88 and perfect>=3:
            glow=0.9+0.1*math.sin(menu_animation*8)
            glColor3f(glow,glow,0.4)
            draw_text(250,320,"✓ CERTIFIED MASTER PHOTOGRAPHER ✓You're the Champ")
    glColor3f(0.8,0.8,1)
    draw_text(300,250,"Press R for New Adventure")
    draw_text(280,220,"Press G for Complete Gallery")
    draw_text(320,190,"Press M for Main Menu")
    draw_text(360,160,"Press Q to Quit")



def draw_instruction():
    draw_text(350,750,"Snapshot Safari - COMPLETE TUTORIAL")
    y = 700

    glColor3f(1,1,0.3)
    draw_text(50,y,"PHOTOGRAPHER MOVEMENT SYSTEM:")
    y -= 25
    glColor3f(1,1,1)
    draw_text(70,y,"W / S - Move Forward & Backward (Smooth movement)")
    y -= 20
    draw_text(70,y,"A / D - Rotate Left & Right (Continuous turning)")
    y -= 20
    draw_text(70,y,"Arrow Keys - Adjust camera pitch and height")
    y -= 30
    glColor3f(1,1,0.3)
    draw_text(50,y,"PROFESSIONAL CAMERA SYSTEM:")
    y -= 25
    glColor3f(1,1,1)
    draw_text(70,y,"Left Click - Capture Photo (Limited to 12 shots per level)")
    y -= 20
    draw_text(70,y,"Right Click / T - Toggle First & Third Person View")
    y -= 20
    draw_text(70,y,"Z / X - Zoom In & Out (Hold for smooth zoom control)")
    y -= 20
    draw_text(70,y,"F - Toggle Auto / Manual Focus Mode")
    y -= 20
    draw_text(70,y,"L - Switch Camera Lens (Unlock via performance scores)")
    y -= 30
    glColor3f(1,1,0.3)
    draw_text(50,y,"GAME CONTROLS:")
    y -= 25
    glColor3f(1,1,1)
    draw_text(70,y,"P - Pause / Resume Game")
    y -= 20
    draw_text(70,y,"Q - Quit Game (available anytime)")
    y -= 20
    draw_text(70,y,"I - Open In-Game Instructions")
    y -= 30
    glColor3f(1,1,0.3)
    draw_text(50,y,"PROFESSIONAL EQUIPMENT:")
    y -= 25
    glColor3f(0.8,1,0.8)
    draw_text(70,y,"• Standard Lens - Balanced performance for all scenarios")
    y -= 18
    draw_text(70,y,"• Telephoto Lens - Long-distance photography (Unlock: 95%+ score)")
    y -= 18
    draw_text(70,y,"• Wide Angle Lens - Close and environmental shots (Unlock: Level 2, 90%+)")
    y -= 18
    draw_text(70,y,"• Macro Lens - Extreme close-up detail shots (Unlock: Level 3, 85%+)")
    y -= 25
    glColor3f(1,0.8,0.3)
    draw_text(50,y,"TRAINING ASSISTANCE:")
    y -= 25
    glColor3f(1,1,1)
    draw_text(70,y,"C - Toggle Auto-Aim Training Mode")
    y -= 18
    draw_text(70,y,"V - Enable Auto Focus (Training Mode Only)")
    y -= 30
    glColor3f(1,0.7,0.4)
    draw_text(200,y,"Press M - Menu | Press A - Avatar Selection | Press Q - Quit")

def main():
    print("=== PHOTO QUEST: THE PERFECT SHOT ===")
    print("Loading enhanced photography simulator...")
    print("Controls: WASD=Move, P=Pause, Q=Quit, T=Toggle View")
    print("Use 'I' in-game for complete instructions!")
    glutInit();glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
    glutInitWindowSize(1100,750)
    glutInitWindowPosition(200,0)
    glutCreateWindow(b"Snapshot Safari: The Perfect Shot")
    init_targets();updated_weather()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener);glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener);glutSpecialUpFunc(specialKeyUpListener)
    glutMouseFunc(mouseListener);glutIdleFunc(idle_status)
    print("Game initialized successfully!")
    print("Choose your photography specialist and begin your adventure!")
    glutMainLoop()

if __name__=="__main__":main()
