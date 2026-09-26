import pygame
import math
import random

from objects import Satellite, Debris, Rocket, Planet, CollisionManager


# -----------------------------
# INITIALIZE PYGAME
# -----------------------------

pygame.init()

WIDTH = 1100
HEIGHT = 750

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE SENTINEL - Space Traffic Management")

clock = pygame.time.Clock()


# -----------------------------
# EARTH
# -----------------------------

EARTH_X = WIDTH // 2 - 150
EARTH_Y = HEIGHT // 2
EARTH_RADIUS = 60


# -----------------------------
# CREATE SPACE OBJECTS
# -----------------------------

planets = [
    Planet(
        "EARTH",
        EARTH_X,
        EARTH_Y,
        radius=EARTH_RADIUS,
        color=(40, 100, 220)
    ),

    Planet(
        "MOON",
        WIDTH - 120,
        160,
        radius=35,
        color=(225, 225, 225)
    )
]


satellites = [
    Satellite("SAT-01", 150, 0.0, 0.9),
    Satellite("SAT-02", 220, 2.4, -0.6),
]


# -----------------------------
# DEBRIS FIELD
# -----------------------------

debris_field = [

    # -------------------------
    # LINEAR DEBRIS
    # -------------------------

    Debris("DEBRIS-01", 90, 120, 45, 20, False),
    Debris("DEBRIS-02", 970, 180, -30, 35, False),
    Debris("DEBRIS-03", 180, 650, 35, -45, False),
    Debris("DEBRIS-04", 920, 650, -45, -25, False),
    Debris("DEBRIS-05", 80, 400, 55, -15, False),

    Debris("DEBRIS-06", 1020, 400, -50, 20, False),
    Debris("DEBRIS-07", 300, 80, 30, 50, False),
    Debris("DEBRIS-08", 750, 80, -25, 45, False),
    Debris("DEBRIS-09", 300, 680, 40, -30, False),
    Debris("DEBRIS-10", 750, 680, -40, -35, False),

    # Debris("DEBRIS-11", 150, 250, 50, 25, False),
    # Debris("DEBRIS-12", 1000, 550, -55, -20, False),
    # Debris("DEBRIS-13", 500, 60, 20, 55, False),
    # Debris("DEBRIS-14", 500, 700, -20, -50, False),
    # Debris("DEBRIS-15", 100, 600, 45, -35, False),


    # -------------------------
    # ORBITING DEBRIS
    # -------------------------

    # Around 100 px orbit
    Debris("DEBRIS-16", 500, 375, 0, 35, True),
    Debris("DEBRIS-17", 400, 275, -35, 0, True),

    # Around 280 px orbit
    Debris("DEBRIS-18", 680, 375, 0, 35, True),
    Debris("DEBRIS-19", 120, 375, 0, -35, True),
    Debris("DEBRIS-20", 400, 655, -35, 0, True),

    # Around 350 px orbit
    Debris("DEBRIS-21", 750, 375, 0, 40, True),
    Debris("DEBRIS-22", 50, 375, 0, -40, True),
    Debris("DEBRIS-23", 400, 25, 40, 0, True),
]


# -----------------------------
# ROCKET
# -----------------------------

rocket = Rocket(
    "ROCKET-01",
    EARTH_X,
    EARTH_Y + EARTH_RADIUS + 20,
    0,
    0
)


planet = planets[1]


# -----------------------------
# COLLISION MANAGER
# -----------------------------

collision_manager = CollisionManager(
    EARTH_X,
    EARTH_Y,
    lookahead=1.5
)


# -----------------------------
# FONTS
# -----------------------------

font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 18)
title_font = pygame.font.Font(None, 40)
warning_font = pygame.font.Font(None, 26)


# -----------------------------
# DEBRIS SPAWN UI
# -----------------------------

distance_input = ""
speed_input = ""

active_input = None

# Current mode
spawn_mode = "orbital"

# Small UI in top-right
distance_box = pygame.Rect(760, 25, 100, 28)
speed_box = pygame.Rect(870, 25, 100, 28)

orbital_button = pygame.Rect(760, 58, 100, 25)
linear_button = pygame.Rect(870, 58, 100, 25)

spawn_button = pygame.Rect(980, 25, 90, 58)


# ID for newly spawned debris
next_debris_id = 24


# -----------------------------
# TRACKABLE OBJECTS
# -----------------------------

def all_trackable_objects():
    return satellites + debris_field + [rocket] + planets


# -----------------------------
# SPAWN LINEAR DEBRIS
# -----------------------------

def spawn_linear_debris(speed):

    global next_debris_id

    # Pick a random screen edge
    edge = random.randint(0, 3)

    if edge == 0:
        # Top
        x = random.randint(50, WIDTH - 50)
        y = 10

    elif edge == 1:
        # Right
        x = WIDTH - 10
        y = random.randint(50, HEIGHT - 50)

    elif edge == 2:
        # Bottom
        x = random.randint(50, WIDTH - 50)
        y = HEIGHT - 10

    else:
        # Left
        x = 10
        y = random.randint(50, HEIGHT - 50)

    # Point toward Earth
    dx = EARTH_X - x
    dy = EARTH_Y - y

    distance = math.sqrt(dx * dx + dy * dy)

    vx = (dx / distance) * speed
    vy = (dy / distance) * speed

    new_debris = Debris(
        f"DEBRIS-{next_debris_id:02d}",
        x,
        y,
        vx,
        vy,
        False
    )

    debris_field.append(new_debris)

    next_debris_id += 1


# -----------------------------
# SPAWN ORBITAL DEBRIS
# -----------------------------

def spawn_orbital_debris(orbit_radius, speed):

    global next_debris_id

    # Pick random position around Earth
    angle = random.uniform(0, 2 * math.pi)

    x = EARTH_X + orbit_radius * math.cos(angle)
    y = EARTH_Y + orbit_radius * math.sin(angle)

    # Tangential velocity
    vx = -math.sin(angle) * speed
    vy = math.cos(angle) * speed

    new_debris = Debris(
        f"DEBRIS-{next_debris_id:02d}",
        x,
        y,
        vx,
        vy,
        True
    )

    # --------------------------------
    # INITIALIZE ORBIT IMMEDIATELY
    # --------------------------------

    new_debris.orbit_radius = orbit_radius
    new_debris.angle = angle

    # Convert linear speed into angular speed
    new_debris.speed = speed / orbit_radius

    new_debris.orbit_initialized = True

    debris_field.append(new_debris)

    next_debris_id += 1


# -----------------------------
# MAIN LOOP
# -----------------------------

running = True

while running:

    dt = clock.tick(60) / 1000


    # -------------------------
    # EVENTS
    # -------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


        # -------------------------
        # MOUSE INPUT
        # -------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = event.pos


            # Distance input
            if distance_box.collidepoint(mouse_pos):

                active_input = "distance"


            # Speed input
            elif speed_box.collidepoint(mouse_pos):

                active_input = "speed"


            # Orbital mode
            elif orbital_button.collidepoint(mouse_pos):

                spawn_mode = "orbital"
                active_input = None


            # Linear mode
            elif linear_button.collidepoint(mouse_pos):

                spawn_mode = "linear"
                active_input = None


            # Spawn button
            elif spawn_button.collidepoint(mouse_pos):

                try:

                    speed = float(speed_input)

                    if speed <= 0:
                        continue


                    # -------------------------
                    # ORBITAL
                    # -------------------------

                    if spawn_mode == "orbital":

                        orbit_radius = float(distance_input)

                        if orbit_radius <= 0:
                            continue


                        # Keep orbit inside the visible screen
                        max_radius = min(
                            EARTH_X,
                            WIDTH - EARTH_X,
                            EARTH_Y,
                            HEIGHT - EARTH_Y
                        ) - 5


                        if orbit_radius > max_radius:
                            orbit_radius = max_radius


                        spawn_orbital_debris(
                            orbit_radius,
                            speed
                        )


                    # -------------------------
                    # LINEAR
                    # -------------------------

                    else:

                        spawn_linear_debris(speed)


                    # Clear fields
                    distance_input = ""
                    speed_input = ""
                    active_input = None


                except ValueError:

                    pass


        # -------------------------
        # KEYBOARD INPUT
        # -------------------------

        if event.type == pygame.KEYDOWN:

            # Distance field
            if active_input == "distance":

                if event.key == pygame.K_BACKSPACE:

                    distance_input = distance_input[:-1]

                elif event.key == pygame.K_RETURN:

                    active_input = None

                elif event.unicode.isdigit():

                    distance_input += event.unicode


            # Speed field
            elif active_input == "speed":

                if event.key == pygame.K_BACKSPACE:

                    speed_input = speed_input[:-1]

                elif event.key == pygame.K_RETURN:

                    active_input = None

                elif event.unicode.isdigit() or event.unicode == ".":

                    speed_input += event.unicode


            # Launch rocket
            elif event.key == pygame.K_l:

                if not rocket.launched:

                    if rocket.burn_fuel(30):

                        rocket.launch_toward(
                            planet.x,
                            planet.y,
                            speed=140
                        )


    # -------------------------
    # UPDATE SATELLITES
    # -------------------------

    for sat in satellites:

        sat.update_avoidance_timer(dt)

        sat.update_orbit(
            EARTH_X,
            EARTH_Y,
            dt
        )


    # -------------------------
    # UPDATE DEBRIS
    # -------------------------

    for d in debris_field:

        if d.if_orbiting:

            d.update_orbit(
                EARTH_X,
                EARTH_Y,
                dt
            )

        else:

            d.update(dt)

            d.bounce_bounds(
                WIDTH,
                HEIGHT
            )


    # -------------------------
    # UPDATE ROCKET
    # -------------------------

    if rocket.launched:

        rocket.update(dt)


    # -------------------------
    # DESTROY DEBRIS ON CONTACT
    # -------------------------

    all_objects = all_trackable_objects()

    for debris in debris_field[:]:

        if debris.destroy_debris(all_objects):

            debris_field.remove(debris)


    # -------------------------
    # COLLISION PREDICTION
    # -------------------------

    collision_manager.update(
        all_trackable_objects()
    )


    # -------------------------
    # DRAW BACKGROUND
    # -------------------------

    screen.fill(
        (5, 8, 20)
    )


    # -------------------------
    # TITLE
    # -------------------------

    title = title_font.render(
        "SPACE SENTINEL",
        True,
        (255, 255, 255)
    )

    screen.blit(
        title,
        (30, 20)
    )


    subtitle = small_font.render(
        "Press L to launch ROCKET toward MOON",
        True,
        (150, 150, 170)
    )

    screen.blit(
        subtitle,
        (30, 60)
    )


    # -------------------------
    # DEBRIS INPUT UI
    # -------------------------

    # Distance box
    pygame.draw.rect(
        screen,
        (25, 30, 50),
        distance_box
    )

    pygame.draw.rect(
        screen,
        (255, 255, 255)
        if active_input == "distance"
        else (100, 100, 120),
        distance_box,
        1
    )


    # Speed box
    pygame.draw.rect(
        screen,
        (25, 30, 50),
        speed_box
    )

    pygame.draw.rect(
        screen,
        (255, 255, 255)
        if active_input == "speed"
        else (100, 100, 120),
        speed_box,
        1
    )


    # Orbital button
    orbital_color = (
        (50, 110, 150)
        if spawn_mode == "orbital"
        else (30, 40, 60)
    )

    pygame.draw.rect(
        screen,
        orbital_color,
        orbital_button
    )

    pygame.draw.rect(
        screen,
        (100, 150, 180),
        orbital_button,
        1
    )


    # Linear button
    linear_color = (
        (50, 110, 150)
        if spawn_mode == "linear"
        else (30, 40, 60)
    )

    pygame.draw.rect(
        screen,
        linear_color,
        linear_button
    )

    pygame.draw.rect(
        screen,
        (100, 150, 180),
        linear_button,
        1
    )


    # Spawn button
    pygame.draw.rect(
        screen,
        (30, 80, 120),
        spawn_button
    )

    pygame.draw.rect(
        screen,
        (100, 150, 180),
        spawn_button,
        1
    )


    # -------------------------
    # UI TEXT
    # -------------------------

    distance_text = small_font.render(
        distance_input if distance_input else "Distance",
        True,
        (220, 220, 220)
    )

    speed_text = small_font.render(
        speed_input if speed_input else "Speed",
        True,
        (220, 220, 220)
    )

    orbital_text = small_font.render(
        "ORBITAL",
        True,
        (255, 255, 255)
    )

    linear_text = small_font.render(
        "LINEAR",
        True,
        (255, 255, 255)
    )

    spawn_text = small_font.render(
        "SPAWN",
        True,
        (255, 255, 255)
    )


    screen.blit(
        distance_text,
        (
            distance_box.x + 5,
            distance_box.y + 6
        )
    )

    screen.blit(
        speed_text,
        (
            speed_box.x + 5,
            speed_box.y + 6
        )
    )

    screen.blit(
        orbital_text,
        (
            orbital_button.x + 25,
            orbital_button.y + 5
        )
    )

    screen.blit(
        linear_text,
        (
            linear_button.x + 28,
            linear_button.y + 5
        )
    )

    screen.blit(
        spawn_text,
        (
            spawn_button.x + 28,
            spawn_button.y + 20
        )
    )


    # -------------------------
    # EARTH
    # -------------------------

    pygame.draw.circle(
        screen,
        (40, 100, 220),
        (EARTH_X, EARTH_Y),
        EARTH_RADIUS
    )


    # -------------------------
    # SATELLITE ORBITS
    # -------------------------

    for sat in satellites:

        pygame.draw.circle(
            screen,
            (60, 60, 90),
            (EARTH_X, EARTH_Y),
            int(sat.base_orbit_radius),
            1
        )


    # -------------------------
    # MOON
    # -------------------------

    pygame.draw.circle(
        screen,
        planet.color,
        (int(planet.x), int(planet.y)),
        planet.radius
    )

    planet_label = font.render(
        planet.name,
        True,
        (255, 200, 180)
    )

    screen.blit(
        planet_label,
        (
            int(planet.x) - 20,
            int(planet.y) - planet.radius - 22
        )
    )


    # -------------------------
    # DRAW ORBITING DEBRIS
    # -------------------------

    for d in debris_field:

        if d.if_orbiting:

            d.draw_debris_orbit(
                screen,
                EARTH_X,
                EARTH_Y
            )


    # -------------------------
    # DRAW DEBRIS
    # -------------------------

    for d in debris_field:

        color = (
            (255, 80, 80)
            if d.warning
            else (160, 160, 160)
        )

        pygame.draw.circle(
            screen,
            color,
            (int(d.x), int(d.y)),
            d.radius
        )

        label = small_font.render(
            d.name,
            True,
            color
        )

        screen.blit(
            label,
            (
                int(d.x) + 8,
                int(d.y) - 8
            )
        )


    # -------------------------
    # DRAW SATELLITES
    # -------------------------

    for sat in satellites:

        color = (
            (255, 80, 80)
            if sat.warning
            else (255, 255, 255)
        )

        pygame.draw.circle(
            screen,
            color,
            (int(sat.x), int(sat.y)),
            sat.radius
        )

        label = font.render(
            sat.name,
            True,
            color
        )

        screen.blit(
            label,
            (
                int(sat.x) + 10,
                int(sat.y) - 10
            )
        )


        if sat.avoiding:

            tag = small_font.render(
                "AVOIDING",
                True,
                (255, 180, 80)
            )

            screen.blit(
                tag,
                (
                    int(sat.x) + 10,
                    int(sat.y) + 8
                )
            )


    # -------------------------
    # DRAW ROCKET
    # -------------------------

    rocket_color = (
        (255, 80, 80)
        if rocket.warning
        else (255, 120, 40)
    )

    pygame.draw.circle(
        screen,
        rocket_color,
        (int(rocket.x), int(rocket.y)),
        rocket.radius
    )

    rocket_label = font.render(
        rocket.name,
        True,
        (255, 180, 100)
    )

    screen.blit(
        rocket_label,
        (
            int(rocket.x) + 10,
            int(rocket.y) - 10
        )
    )

    fuel_text = small_font.render(
        f"Fuel: {rocket.fuel}",
        True,
        (200, 200, 200)
    )

    screen.blit(
        fuel_text,
        (
            int(rocket.x) + 10,
            int(rocket.y) + 10
        )
    )


    # -------------------------
    # DRAW COLLISION WARNINGS
    # -------------------------

    for a, b in collision_manager.active_warnings:

        pygame.draw.line(
            screen,
            (255, 60, 60),
            (int(a.x), int(a.y)),
            (int(b.x), int(b.y)),
            1
        )


    if collision_manager.active_warnings:

        warn_text = warning_font.render(
            f"COLLISION RISK: "
            f"{len(collision_manager.active_warnings)} "
            f"pair(s) - auto-correcting",
            True,
            (255, 90, 90)
        )

        screen.blit(
            warn_text,
            (30, HEIGHT - 40)
        )


    # -------------------------
    # DISPLAY
    # -------------------------

    pygame.display.flip()


pygame.quit()