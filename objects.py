import math


class SpaceObject:
    def __init__(self, name, x, y, vx, vy, radius=5):
        self.name = name
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


class Satellite(SpaceObject):
    def __init__(self, name, orbit_radius, angle, speed):
        super().__init__(name, 0, 0, 0, 0, radius=6)

        self.orbit_radius = orbit_radius
        self.angle = angle
        self.speed = speed

    def update_orbit(self, earth_x, earth_y, dt):
        self.angle += self.speed * dt

        self.x = earth_x + self.orbit_radius * math.cos(self.angle)
        self.y = earth_y + self.orbit_radius * math.sin(self.angle)


class Debris(SpaceObject):
    def __init__(self, name, x, y, vx, vy):
        super().__init__(name, x, y, vx, vy, radius=4)


class Rocket(SpaceObject):
    def __init__(self, name, x, y, vx, vy):
        super().__init__(name, x, y, vx, vy, radius=7)

        self.fuel = 100
        self.active = True

    def burn_fuel(self, amount):
        if self.fuel >= amount:
            self.fuel -= amount
        else:
            self.fuel = 0
import math


def track_orbit(earth_x, earth_y, orbit_radius, angle, speed, dt):
    angle += speed * dt

    x = earth_x + orbit_radius * math.cos(angle)
    y = earth_y + orbit_radius * math.sin(angle)

    return x, y, angle
