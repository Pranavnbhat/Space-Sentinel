import pygame
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
        120,
        radius=35,
        color=(225, 225, 225)
    )
]


satellites = [
    Satellite("SAT-01", 150, 0.0, 0.9),
    Satellite("SAT-02", 220, 2.4, -0.6),
]

debris_field = [

    # -------------------------
    # NORMAL / LINEAR DEBRIS
    # -------------------------

    Debris("DEBRIS-01", 100, 100, 45, 20, False),
    Debris("DEBRIS-02", 900, 200, -30, 35, False),
    Debris("DEBRIS-03", 400, 600, 20, -50, False),
    Debris("DEBRIS-04", 200, 150, 35, 40, False),
    Debris("DEBRIS-05", 800, 500, -45, -20, False),
    Debris("DEBRIS-06", 600, 100, -25, 45, False),
    Debris("DEBRIS-07", 150, 550, 50, -30, False),
    Debris("DEBRIS-08", 950, 600, -40, -35, False),
    Debris("DEBRIS-09", 700, 350, 30, -45, False),
    Debris("DEBRIS-10", 300, 250, -35, 30, False),

    # Debris("DEBRIS-16", 80, 300, 55, 15, False),
    # Debris("DEBRIS-17", 1000, 350, -50, 10, False),
    # Debris("DEBRIS-18", 250, 650, 40, -40, False),
    # Debris("DEBRIS-19", 850, 650, -55, -25, False),
    # Debris("DEBRIS-20", 550, 50, 20, 55, False),
    # Debris("DEBRIS-21", 450, 700, -25, -55, False),
    # Debris("DEBRIS-22", 50, 500, 60, -20, False),
    # Debris("DEBRIS-23", 1050, 500, -60, -15, False),
    # Debris("DEBRIS-24", 750, 150, -40, 30, False),
    # Debris("DEBRIS-25", 350, 100, 35, 50, False),


    # -------------------------
    # ORBITING DEBRIS
    # -------------------------

    # Near SAT-01's 150px orbit
    Debris("DEBRIS-11", 550, 375, 0, 130, True),
    Debris("DEBRIS-12", 505, 483, -130, 0, True),
    Debris("DEBRIS-13", 312, 496, 0, 130, True),
    Debris("DEBRIS-14", 260, 322, 0, -130, True),
    Debris("DEBRIS-15", 443, 231, -130, 0, True),

    # Near SAT-02's 220px orbit
    Debris("DEBRIS-26", 610, 440, 0, 130, True),
    Debris("DEBRIS-27", 416, 595, -130, 0, True),
    Debris("DEBRIS-28", 193, 449, 0, 130, True),
    Debris("DEBRIS-29", 256, 209, 0, -130, True),
    Debris("DEBRIS-30", 506, 185, -130, 0, True),
    
    # INNER ORBIT ~100 px
    Debris("DEBRIS-31", 500, 375, 0, 35, True),
    Debris("DEBRIS-32", 400, 275, -35, 0, True),

    # MIDDLE ORBIT ~280 px
    Debris("DEBRIS-33", 680, 375, 0, 35, True),
    Debris("DEBRIS-34", 120, 375, 0, -35, True),
    Debris("DEBRIS-35", 400, 655, -35, 0, True),

    # OUTER ORBIT ~350 px
    Debris("DEBRIS-36", 750, 375, 0, 40, True),
    Debris("DEBRIS-37", 50, 375, 0, -40, True),
    Debris("DEBRIS-38", 400, 25, 40, 0, True),
]
rocket = Rocket("ROCKET-01", EARTH_X, EARTH_Y + EARTH_RADIUS + 20, 0, 0)

planet = Planet("MOON", WIDTH - 120, 120, radius=35, color=(225, 225, 225))

collision_manager = CollisionManager(EARTH_X, EARTH_Y, lookahead=1.5)


# -----------------------------
# FONTS
# -----------------------------

font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 18)
title_font = pygame.font.Font(None, 40)
warning_font = pygame.font.Font(None, 26)


def all_trackable_objects():
    return satellites + debris_field + [rocket] +planets


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

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l and not rocket.launched:
                # Launch rocket toward the planet, spend some fuel
                if rocket.burn_fuel(30):
                    rocket.launch_toward(planet.x, planet.y, speed=140)

    # -------------------------
    # UPDATE OBJECTS
    # -------------------------
    for sat in satellites:
        sat.update_avoidance_timer(dt)
        sat.update_orbit(EARTH_X, EARTH_Y, dt)

    for d in debris_field:
        if d.if_orbiting:
            d.update_orbit(EARTH_X, EARTH_Y, dt)
        else:
            d.update(dt)
            d.bounce_bounds(WIDTH, HEIGHT)

    
    if rocket.launched:
        rocket.update(dt)

    # Predict + resolve collisions across everything we're tracking, so
    # avoiding one collision doesn't walk a satellite into another object.
    collision_manager.update(all_trackable_objects())
    if rocket.launched:
        rocket.update(dt)

    # -------------------------
    # DESTROY DEBRIS ON CONTACT
    # -------------------------

    all_objects = all_trackable_objects()

    for debris in debris_field[:]:
        if debris.destroy_debris(all_objects):
            debris_field.remove(debris)

    # Predict + resolve collisions across everything we're tracking
    collision_manager.update(all_trackable_objects())
    
    
    # -------------------------
    # DRAW BACKGROUND
    # -------------------------
    screen.fill((5, 8, 20))

    title = title_font.render("SPACE SENTINEL", True, (255, 255, 255))
    screen.blit(title, (30, 20))

    subtitle = small_font.render(
        "Press L to launch ROCKET toward MOON", True, (150, 150, 170)
    )
    screen.blit(subtitle, (30, 60))

    # -------------------------
    # EARTH + ORBITS
    # -------------------------
    pygame.draw.circle(screen, (40, 100, 220), (EARTH_X, EARTH_Y), EARTH_RADIUS)

    for sat in satellites:
        pygame.draw.circle(
            screen, (60, 60, 90), (EARTH_X, EARTH_Y), int(sat.base_orbit_radius), 1
        )

    # -------------------------
    # PLANET
    # -------------------------
    pygame.draw.circle(screen, planet.color, (int(planet.x), int(planet.y)), planet.radius)
    planet_label = font.render(planet.name, True, (255, 200, 180))
    screen.blit(planet_label, (int(planet.x) - 20, int(planet.y) - planet.radius - 22))

    # -------------------------
    # DRAW SATELLITES
    # -------------------------
    for sat in satellites:
        color = (255, 80, 80) if sat.warning else (255, 255, 255)
        pygame.draw.circle(screen, color, (int(sat.x), int(sat.y)), sat.radius)
        label = font.render(sat.name, True, color)
        screen.blit(label, (int(sat.x) + 10, int(sat.y) - 10))

        if sat.avoiding:
            tag = small_font.render("AVOIDING", True, (255, 180, 80))
            screen.blit(tag, (int(sat.x) + 10, int(sat.y) + 8))

    # -------------------------
    # DRAW DEBRIS
    # -------------------------
    for d in debris_field:

        if d.if_orbiting:
            d.draw_debris_orbit(screen, EARTH_X, EARTH_Y)

        color = (255, 80, 80) if d.warning else (160, 160, 160)

        pygame.draw.circle(
            screen,
            color,
            (int(d.x), int(d.y)),
            d.radius
        )

        label = small_font.render(d.name, True, color)
        screen.blit(label, (int(d.x) + 8, int(d.y) - 8))

    # -------------------------
    # DRAW ROCKET
    # -------------------------
    rocket_color = (255, 80, 80) if rocket.warning else (255, 120, 40)
    pygame.draw.circle(screen, rocket_color, (int(rocket.x), int(rocket.y)), rocket.radius)
    rocket_label = font.render(rocket.name, True, (255, 180, 100))
    screen.blit(rocket_label, (int(rocket.x) + 10, int(rocket.y) - 10))

    fuel_text = small_font.render(f"Fuel: {rocket.fuel}", True, (200, 200, 200))
    screen.blit(fuel_text, (int(rocket.x) + 10, int(rocket.y) + 10))

    # -------------------------
    # DRAW COLLISION WARNINGS
    # -------------------------
    for a, b in collision_manager.active_warnings:
        pygame.draw.line(
            screen, (255, 60, 60), (int(a.x), int(a.y)), (int(b.x), int(b.y)), 1
        )

    if collision_manager.active_warnings:
        warn_text = warning_font.render(
            f"COLLISION RISK: {len(collision_manager.active_warnings)} pair(s) - auto-correcting",
            True,
            (255, 90, 90),
        )
        screen.blit(warn_text, (30, HEIGHT - 40))

    # -------------------------
    # DISPLAY
    # -------------------------
    pygame.display.flip()


pygame.quit()
