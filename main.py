import pygame
from objects import Satellite, Debris, Rocket

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("OrbitFlow Test")

clock = pygame.time.Clock()

earth_x = 400
earth_y = 300

satellite = Satellite("SAT-01", 150, 0, 1)
debris = Debris("DEBRIS-01", 100, 100, 40, 20)
rocket = Rocket("ROCKET-01", 400, 500, 0, -60)

running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    satellite.update_orbit(earth_x, earth_y, dt)
    debris.update(dt)
    rocket.update(dt)

    screen.fill((5, 8, 20))

    # Earth
    pygame.draw.circle(
        screen,
        (40, 100, 220),
        (earth_x, earth_y),
        60
    )

    # Satellite orbit
    pygame.draw.circle(
        screen,
        (100, 100, 100),
        (earth_x, earth_y),
        satellite.orbit_radius,
        1
    )

    # Satellite
    pygame.draw.circle(
        screen,
        (255, 255, 255),
        (int(satellite.x), int(satellite.y)),
        6
    )

    # Debris
    pygame.draw.circle(
        screen,
        (150, 150, 150),
        (int(debris.x), int(debris.y)),
        5
    )

    # Rocket
    pygame.draw.circle(
        screen,
        (255, 100, 40),
        (int(rocket.x), int(rocket.y)),
        7
    )

    pygame.display.flip()

pygame.quit()
