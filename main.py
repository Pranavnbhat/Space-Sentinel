import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 1200, 740
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE SENTINEL")
clock = pygame.time.Clock()
FPS = 24

font_mini = pygame.font.SysFont("consolas", 12)
font_small = pygame.font.SysFont("consolas", 14)
font_ttc = pygame.font.SysFont("consolas", 16, bold=True)
font_label = pygame.font.SysFont("consolas", 22, bold=True)
font_big = pygame.font.SysFont("consolas", 18, bold=True)

BG_COLOR = (4, 4, 14)
EARTH_COLOR = (60, 120, 255)
MOON_COLOR = (220, 220, 235)
MOON_CRATER_COLOR = (170, 170, 185)
ORBIT_COLOR = (50, 50, 80)
TEXT_COLOR = (220, 220, 230)
WHITE_COLOR = (255, 255, 255)
WARNING_COLOR = (255, 60, 60)
TTC_COLOR = (255, 230, 0)
AVOID_COLOR = (255, 140, 0)
DEBRIS_COLOR = (170, 150, 120)
ASTEROID_COLOR = (200, 110, 50)
SAT_COLORS = [(0, 255, 150), (255, 200, 0), (255, 100, 255), (0, 200, 255)]

EARTH_POS = (WIDTH // 2, HEIGHT // 2)
EARTH_RADIUS = 40
WARNING_DISTANCE = 45

# --- REAL-LIFE CATALOGS ---
REAL_SATELLITES = ["ISS", "HUBBLE", "JAMES-WEBB", "STARLINK-3012", "GPS-BIIR-2", "TIANGONG", "LANDSAT-9", "SENTINEL-6", "IRIDIUM-100", "KEPLER-SAT"]
REAL_DEBRIS = ["FENGYUN-1C-DEB", "COSMOS-1408-FRAG", "SL-12-R/B", "DELTA-4-R/B", "IRIDIUM-33-DEB", "PEGASUS-HAPS-DEB"]
REAL_ASTEROIDS = ["BENNU", "APOPHIS", "RYUGU", "EROS", "TOUTATIS", "ITOKAWA", "CERES", "VESTA", "PALLAS", "GEOGRAPHOS"]


def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def draw_text(surface, text, pos, color=TEXT_COLOR, font=font_small):
    surface.blit(font.render(text, True, color), pos)


def get_unique_sat_name(all_objects, rockets):
    """Generates a satellite name that is not currently present in the orbit or in transit."""
    existing_names = set(getattr(obj, 'label', '') for obj in all_objects)
    existing_names.update(getattr(r, 'sat_name', '') for r in rockets)

    available_names = [name for name in REAL_SATELLITES if name not in existing_names]

    if available_names:
        return random.choice(available_names)
    
    # Fallback to auto-numbered naming if catalog is exhausted
    counter = 1
    while f"SAT-{counter:03d}" in existing_names:
        counter += 1
    return f"SAT-{counter:03d}"


class InputBox:
    def __init__(self, x, y, w, h, default_text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = (70, 70, 100)
        self.color_active = (0, 200, 255)
        self.color = self.color_inactive
        self.text = default_text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key != pygame.K_RETURN and len(self.text) < 14:
                self.text += event.unicode

    def draw(self, surface):
        pygame.draw.rect(surface, (15, 15, 30), self.rect)
        pygame.draw.rect(surface, self.color, self.rect, 1)
        draw_text(surface, self.text, (self.rect.x + 4, self.rect.y + 2), TEXT_COLOR, font=font_mini)


class OrbitingObject:
    def __init__(self, orbit_radius, speed, color, label, angle=0.0, size=4, is_debris=False, is_moon=False):
        self.base_radius = orbit_radius
        self.orbit_radius = orbit_radius
        self.speed = speed
        self.angle = angle
        self.color = color
        self.label = label
        self.is_debris = is_debris
        self.is_moon = is_moon
        self.avoiding = False
        self.avoid_timer = 0
        self.size = size
        self.self_rotation = 0.0

    def update(self):
        self.angle = (self.angle + self.speed) % (2 * math.pi)
        
        if self.is_moon:
            self.self_rotation = (self.self_rotation + 0.015) % (2 * math.pi)
        else:
            self.self_rotation = (self.self_rotation + 0.02) % (2 * math.pi)

        if self.avoiding and not self.is_moon:
            self.avoid_timer -= 1
            if self.avoid_timer <= 0:
                self.avoiding = False
        target = self.base_radius + (25 if (self.avoiding and not self.is_moon) else 0)
        self.orbit_radius += (target - self.orbit_radius) * 0.12

    def position(self):
        x = EARTH_POS[0] + self.orbit_radius * math.cos(self.angle)
        y = EARTH_POS[1] + self.orbit_radius * math.sin(self.angle)
        return (int(x), int(y))

    def start_avoidance(self):
        if not self.is_moon:
            self.avoiding = True
            self.avoid_timer = 20

    def draw(self, surface, warning=False):
        pygame.draw.circle(surface, ORBIT_COLOR, EARTH_POS, int(self.base_radius), 1)
        pos = self.position()

        if self.is_moon:
            pygame.draw.circle(surface, self.color, pos, self.size)
            crater_offsets = [(0.4, 0.2, 3), (-0.3, -0.4, 2), (0.1, -0.5, 2)]
            for rx, ry, r_size in crater_offsets:
                rot_x = pos[0] + self.size * (rx * math.cos(self.self_rotation) - ry * math.sin(self.self_rotation))
                rot_y = pos[1] + self.size * (rx * math.sin(self.self_rotation) + ry * math.cos(self.self_rotation))
                pygame.draw.circle(surface, MOON_CRATER_COLOR, (int(rot_x), int(rot_y)), r_size)
        else:
            marker_color = WARNING_COLOR if (warning and not self.is_moon) else self.color
            radius = 4 if self.is_debris else self.size
            pygame.draw.circle(surface, marker_color, pos, radius)

        lx, ly = pos
        if not self.is_debris:
            draw_text(surface, self.label, (lx + 12, ly - 14), WHITE_COLOR, font=font_label)
            
            if self.avoiding and not self.is_moon:
                draw_text(surface, "[AVOIDING]", (lx + 12, ly + 10), WHITE_COLOR, font=font_small)


class EllipticalHazard:
    def __init__(self, name, a, e, tilt_angle, speed, color, size=3, is_asteroid=False):
        self.label = name
        self.a = a
        self.e = e
        self.b = a * math.sqrt(1 - e ** 2) if e < 1 else a * 0.5
        self.tilt = tilt_angle
        self.mean_anomaly = random.uniform(0, 2 * math.pi)
        self.speed = speed
        self.color = color
        self.size = size
        self.is_debris = True
        self.is_moon = False
        self.is_asteroid = is_asteroid
        self.focus_offset = self.a * self.e
        self.avoiding = False
        self.avoid_timer = 0

    def update(self):
        self.mean_anomaly = (self.mean_anomaly + self.speed) % (2 * math.pi)
        if self.avoiding:
            self.avoid_timer -= 1
            if self.avoid_timer <= 0:
                self.avoiding = False

    def position(self):
        offset_a = self.a + (30 if self.avoiding else 0)
        x_raw = offset_a * math.cos(self.mean_anomaly) - (offset_a * self.e)
        y_raw = self.b * math.sin(self.mean_anomaly)

        x_rot = x_raw * math.cos(self.tilt) - y_raw * math.sin(self.tilt)
        y_rot = x_raw * math.sin(self.tilt) + y_raw * math.cos(self.tilt)

        return (int(EARTH_POS[0] + x_rot), int(EARTH_POS[1] + y_rot))

    def start_avoidance(self):
        self.avoiding = True
        self.avoid_timer = 20

    def draw(self, surface, warning=False):
        pos = self.position()
        color = WARNING_COLOR if warning else self.color
        
        if self.is_asteroid:
            pygame.draw.circle(surface, color, pos, self.size)
            pygame.draw.circle(surface, (255, 180, 100), pos, max(1, self.size - 2))
        else:
            pygame.draw.circle(surface, color, pos, self.size)

        draw_text(surface, self.label, (pos[0] + 6, pos[1] - 6), color, font=font_mini)


class Rocket:
    def __init__(self, target_radius, angle, sat_name="SAT", sat_speed=0.009):
        self.angle = angle
        self.target_radius = target_radius
        self.progress = 0.0
        self.speed = 0.008
        self.done = False
        self.is_debris = False
        self.is_moon = False
        self.sat_name = sat_name
        self.sat_speed = sat_speed

    def update(self):
        self.progress += self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            self.done = True

    def position(self):
        r = EARTH_RADIUS + (self.target_radius - EARTH_RADIUS) * self.progress
        x = EARTH_POS[0] + r * math.cos(self.angle)
        y = EARTH_POS[1] + r * math.sin(self.angle)
        return (int(x), int(y))

    def start_avoidance(self):
        pass

    def draw(self, surface, warning=False):
        color = WARNING_COLOR if warning else (255, 255, 255)
        pygame.draw.circle(surface, color, self.position(), 4)


class Mission:
    def __init__(self, target_object):
        self.progress = 0.0
        self.speed = 0.005
        self.done = False
        self.target = target_object

    def update(self):
        self.progress += self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            self.done = True

    def get_control_point(self):
        target_pos = self.target.position()
        mid_x = (EARTH_POS[0] + target_pos[0]) / 2
        mid_y = (EARTH_POS[1] + target_pos[1]) / 2
        return (mid_x, mid_y - 120)

    def position(self):
        t = self.progress
        target_pos = self.target.position()
        control = self.get_control_point()
        
        x = ((1 - t) ** 2) * EARTH_POS[0] + 2 * (1 - t) * t * control[0] + (t ** 2) * target_pos[0]
        y = ((1 - t) ** 2) * EARTH_POS[1] + 2 * (1 - t) * t * control[1] + (t ** 2) * target_pos[1]
        return (int(x), int(y))

    def draw(self, surface):
        target_pos = self.target.position()
        control = self.get_control_point()

        for i in range(0, 21):
            t = i / 20
            x = ((1 - t) ** 2) * EARTH_POS[0] + 2 * (1 - t) * t * control[0] + (t ** 2) * target_pos[0]
            y = ((1 - t) ** 2) * EARTH_POS[1] + 2 * (1 - t) * t * control[1] + (t ** 2) * target_pos[1]
            pygame.draw.circle(surface, (80, 80, 60), (int(x), int(y)), 1)
        
        pygame.draw.circle(surface, (255, 230, 120), self.position(), 5)


def check_collisions_and_draw_ttc(objects, surface):
    warning_ids = set()
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            obj1, obj2 = objects[i], objects[j]

            if getattr(obj1, 'is_moon', False) or getattr(obj2, 'is_moon', False):
                other_obj = obj2 if getattr(obj1, 'is_moon', False) else obj1
                if not getattr(other_obj, 'is_debris', False):
                    continue

            p1 = obj1.position()
            p2 = obj2.position()
            dist = distance(p1, p2)
            
            if dist < WARNING_DISTANCE:
                if not getattr(obj1, 'is_moon', False):
                    warning_ids.add(i)
                if not getattr(obj2, 'is_moon', False):
                    warning_ids.add(j)
                
                pygame.draw.line(surface, WARNING_COLOR, p1, p2, 2)
                
                relative_speed = abs(getattr(obj1, 'speed', 0.008) - getattr(obj2, 'speed', 0.008)) * 100
                relative_speed = max(relative_speed, 0.3)
                ttc_seconds = max(0.0, round(dist / (relative_speed * FPS), 1))
                
                mid_x = (p1[0] + p2[0]) // 2
                mid_y = (p1[1] + p2[1]) // 2
                
                lbl = f"t-{ttc_seconds}s" if ttc_seconds > 0 else "IMPACT!"
                draw_text(surface, lbl, (mid_x - 28, mid_y - 14), TTC_COLOR, font=font_ttc)

                if hasattr(obj1, "start_avoidance"):
                    obj1.start_avoidance()
                if hasattr(obj2, "start_avoidance"):
                    obj2.start_avoidance()

    return warning_ids


def spawn_debris(custom_name=None, custom_speed=None):
    name = custom_name.strip() if custom_name and custom_name.strip() else random.choice(REAL_DEBRIS)
    a = random.randint(140, 280)
    e = random.uniform(0.35, 0.72)
    tilt = random.uniform(0, 2 * math.pi)
    speed = custom_speed if custom_speed is not None else random.choice([-0.008, -0.01, 0.009, 0.012])
    return EllipticalHazard(name, a, e, tilt, speed, DEBRIS_COLOR, size=3, is_asteroid=False)


def spawn_asteroid(custom_name=None, custom_speed=None):
    name = custom_name.strip() if custom_name and custom_name.strip() else random.choice(REAL_ASTEROIDS)
    a = random.randint(260, 420)
    e = random.uniform(0.55, 0.85)
    tilt = random.uniform(0, 2 * math.pi)
    speed = custom_speed if custom_speed is not None else random.choice([-0.004, 0.006, -0.007])
    return EllipticalHazard(name, a, e, tilt, speed, ASTEROID_COLOR, size=6, is_asteroid=True)


moon = OrbitingObject(300, 0.002, MOON_COLOR, "MOON", angle=5.0, size=14, is_moon=True)

satellites = [
    OrbitingObject(110, 0.009, SAT_COLORS[0], "ISS", angle=0.0),
    OrbitingObject(160, 0.007, SAT_COLORS[1], "HUBBLE", angle=2.0),
    OrbitingObject(210, 0.005, SAT_COLORS[2], "JAMES-WEBB", angle=4.0),
    moon,
]

hazards = [
    spawn_debris(),
    spawn_asteroid()
]

all_objects = satellites + hazards

rockets = []
missions = []

BOX_H = 18

sat_name_box = InputBox(80, HEIGHT - 25, 95, BOX_H, "")
sat_speed_box = InputBox(215, HEIGHT - 25, 45, BOX_H, "0.009")

RIGHT_COL_X = WIDTH - 310

deb_name_box = InputBox(RIGHT_COL_X + 75, HEIGHT - 45, 95, BOX_H, "")
deb_speed_box = InputBox(RIGHT_COL_X + 210, HEIGHT - 45, 45, BOX_H, "-0.010")

ast_name_box = InputBox(RIGHT_COL_X + 75, HEIGHT - 23, 95, BOX_H, "")
ast_speed_box = InputBox(RIGHT_COL_X + 210, HEIGHT - 45, 45, BOX_H, "0.005")

input_boxes = [sat_name_box, sat_speed_box, deb_name_box, deb_speed_box, ast_name_box, ast_speed_box]

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        for box in input_boxes:
            box.handle_event(event)

        if event.type == pygame.KEYDOWN:
            any_active = any(box.active for box in input_boxes)
            
            if not any_active:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_l:
                    raw_name = sat_name_box.text.strip()
                    # Check for explicit input, otherwise pick a unique catalog name
                    name = raw_name if raw_name else get_unique_sat_name(all_objects, rockets)
                    
                    try: speed = float(sat_speed_box.text.strip())
                    except ValueError: speed = 0.009

                    rockets.append(Rocket(
                        target_radius=random.choice([110, 160, 210]),
                        angle=random.uniform(0, 2 * math.pi),
                        sat_name=name, sat_speed=speed
                    ))
                elif event.key == pygame.K_d:
                    name = deb_name_box.text.strip() or None
                    try: speed = float(deb_speed_box.text.strip())
                    except ValueError: speed = -0.010

                    new_deb = spawn_debris(custom_name=name, custom_speed=speed)
                    hazards.append(new_deb)
                    all_objects.append(new_deb)
                elif event.key == pygame.K_a:
                    name = ast_name_box.text.strip() or None
                    try: speed = float(ast_speed_box.text.strip())
                    except ValueError: speed = 0.005

                    new_ast = spawn_asteroid(custom_name=name, custom_speed=speed)
                    hazards.append(new_ast)
                    all_objects.append(new_ast)
                elif event.key == pygame.K_m:
                    missions.append(Mission(target_object=moon))

    for obj in all_objects:
        obj.update()

    for rocket in rockets:
        rocket.update()
    finished_rockets = [r for r in rockets if r.done]
    for r in finished_rockets:
        new_sat = OrbitingObject(
            r.target_radius, r.sat_speed, random.choice(SAT_COLORS), r.sat_name, angle=r.angle
        )
        satellites.append(new_sat)
        all_objects.append(new_sat)
    rockets = [r for r in rockets if not r.done]

    for mission in missions:
        mission.update()
    missions = [m for m in missions if not m.done]

    screen.fill(BG_COLOR)

    random.seed(42)
    for _ in range(80):
        sx, sy = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        screen.set_at((sx, sy), (90, 90, 110))
    random.seed()

    pygame.draw.circle(screen, EARTH_COLOR, EARTH_POS, EARTH_RADIUS)
    draw_text(screen, "EARTH", (EARTH_POS[0] - 22, EARTH_POS[1] + EARTH_RADIUS + 6), font=font_small)

    trackable = all_objects + rockets
    warning_ids = check_collisions_and_draw_ttc(trackable, screen)

    for idx, obj in enumerate(all_objects):
        obj.draw(screen, warning=idx in warning_ids)

    rocket_start = len(all_objects)
    for offset, rocket in enumerate(rockets):
        rocket.draw(screen, warning=(rocket_start + offset) in warning_ids)

    for mission in missions:
        mission.draw(screen)

    # Upper Left HUD
    panel_lines = [
        "SPACE SENTINEL",
        f"Tracked objects : {len(all_objects)}",
        f"Active warnings : {len(warning_ids)}",
        f"Rockets in transit : {len(rockets)}",
        f"Active missions : {len(missions)}",
        "",
        "[L] Launch Satellite    [D] Spawn Debris",
        "[A] Spawn Asteroid      [M] Moon Mission    [ESC] Quit",
    ]
    for i, line in enumerate(panel_lines):
        color = WARNING_COLOR if ("warnings" in line and warning_ids) else TEXT_COLOR
        f = font_big if i == 0 else font_small
        draw_text(screen, line, (10, 10 + i * 18), color, f)

    # COMPACT BOTTOM PANELS
    draw_text(screen, "SAT CONFIG", (10, HEIGHT - 45), (0, 200, 255), font_small)
    draw_text(screen, "Name:", (10, HEIGHT - 23), font=font_mini)
    sat_name_box.draw(screen)
    draw_text(screen, "Spd:", (180, HEIGHT - 23), font=font_mini)
    sat_speed_box.draw(screen)

    draw_text(screen, "HAZARD CONFIG", (RIGHT_COL_X, HEIGHT - 65), (255, 160, 60), font_small)
    
    draw_text(screen, "Deb Name:", (RIGHT_COL_X, HEIGHT - 43), font=font_mini)
    deb_name_box.draw(screen)
    draw_text(screen, "Spd:", (RIGHT_COL_X + 175, HEIGHT - 43), font=font_mini)
    deb_speed_box.draw(screen)

    draw_text(screen, "Ast Name:", (RIGHT_COL_X, HEIGHT - 21), font=font_mini)
    ast_name_box.draw(screen)
    draw_text(screen, "Spd:", (RIGHT_COL_X + 175, HEIGHT - 21), font=font_mini)
    ast_speed_box.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
#That is the end please install pygame using pip install pygame in python compiler.
