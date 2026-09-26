import math
import pygame 


class SpaceObject:
    def __init__(self, name, x, y, vx, vy, radius=5):
        self.name = name
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.warning = False  # currently flagged as at-risk of collision

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def predict_position(self, t):
        """Where this object will be in t seconds, assuming current velocity."""
        return (self.x + self.vx * t, self.y + self.vy * t)


class Satellite(SpaceObject):
    def __init__(self, name, orbit_radius, angle, speed):
        super().__init__(name, 0, 0, 0, 0, radius=6)

        self.orbit_radius = orbit_radius
        self.base_orbit_radius = orbit_radius  # radius to return to after avoiding
        self.angle = angle
        self.speed = speed

        # Avoidance state
        self.avoiding = False
        self.avoid_target_radius = orbit_radius
        self.avoid_cooldown = 0.0

    def update_orbit(self, earth_x, earth_y, dt):
        self.angle += self.speed * dt

        # Smoothly ease orbit_radius toward its target (avoidance or back to normal)
        self.orbit_radius += (self.avoid_target_radius - self.orbit_radius) * min(1, dt * 2)

        self.x = earth_x + self.orbit_radius * math.cos(self.angle)
        self.y = earth_y + self.orbit_radius * math.sin(self.angle)

    def predict_position(self, t, earth_x=None, earth_y=None):
        """Predict future orbital position. Falls back to straight-line if no earth given."""
        if earth_x is None or earth_y is None:
            return super().predict_position(t)
        future_angle = self.angle + self.speed * t
        x = earth_x + self.orbit_radius * math.cos(future_angle)
        y = earth_y + self.orbit_radius * math.sin(future_angle)
        return (x, y)

    def start_avoidance(self, offset, cooldown=3.0):
        """Nudge orbit radius outward/inward by `offset` to dodge a threat."""
        self.avoiding = True
        self.avoid_target_radius = self.base_orbit_radius + offset
        self.avoid_cooldown = cooldown

    def update_avoidance_timer(self, dt):
        if self.avoiding:
            self.avoid_cooldown -= dt
            if self.avoid_cooldown <= 0:
                self.avoiding = False
                self.avoid_target_radius = self.base_orbit_radius


class Debris(SpaceObject):
    def __init__(self, name, x, y, vx, vy, if_orbiting=False):
        super().__init__(name, x, y, vx, vy, radius=4)
        self.if_orbiting = if_orbiting

        if self.if_orbiting:
            self.orbit_radius = 0
            self.angle = 0
            self.speed = 0
            self.orbit_initialized = False
            
    def update_orbit(self, earth_x, earth_y, dt):
        if not self.orbit_initialized:

            dx = self.x - earth_x
            dy = self.y - earth_y

            self.orbit_radius = math.sqrt(dx * dx + dy * dy)

            self.angle = math.atan2(dy, dx)

            velocity = math.sqrt(
                self.vx * self.vx +
                self.vy * self.vy
            )

            self.speed = velocity / self.orbit_radius

            self.orbit_initialized = True

        self.angle += self.speed * dt

        self.x = (
            earth_x
            + self.orbit_radius * math.cos(self.angle)
        )

        self.y = (
            earth_y
            + self.orbit_radius * math.sin(self.angle)
    )

    def bounce_bounds(self, width, height):
        """Bounce off screen edges so debris doesn't fly off forever."""
        if self.x <= 0 or self.x >= width:
            self.vx *= -1
        if self.y <= 0 or self.y >= height:
            self.vy *= -1
            
    def draw_orbit(self, screen, earth_x, earth_y):
        if not self.if_orbiting or not self.orbit_initialized:
            return

        points = []

        for i in range(360):
            angle = math.radians(i)

            x = earth_x + self.orbit_radius * math.cos(angle)
            y = earth_y + self.orbit_radius * math.sin(angle)

            points.append((int(x), int(y)))

        # Draw a very faint dotted orbit
        for i in range(0, len(points), 8):
            pygame.draw.circle(
                screen,
                (55, 55, 55),
                points[i],
                1
            )
            
    def destroy_debris(self, objects):
        for obj in objects:
            if obj is not self:
                if check_collision(self, obj, margin=0):
                    return True

        return False


class Rocket(SpaceObject):
    def __init__(self, name, x, y, vx, vy):
        super().__init__(name, x, y, vx, vy, radius=7)

        self.fuel = 100
        self.active = True
        self.launched = False
        self.target = None  # (x, y) of destination planet

    def burn_fuel(self, amount):
        if self.fuel >= amount:
            self.fuel -= amount
            return True
        self.fuel = 0
        return False

    def launch_toward(self, target_x, target_y, speed):
        """Point the rocket at a target and set it moving."""
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist == 0:
            return
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed
        self.launched = True
        self.target = (target_x, target_y)


class Planet(SpaceObject):
    def __init__(self, name, x, y, radius=30, color=(200, 100, 60)):
        super().__init__(name, x, y, 0, 0, radius=radius)
        self.color = color


def track_orbit(earth_x, earth_y, orbit_radius, angle, speed, dt):
    """Standalone orbit stepper (kept for backward compatibility)."""
    angle += speed * dt
    x = earth_x + orbit_radius * math.cos(angle)
    y = earth_y + orbit_radius * math.sin(angle)
    return x, y, angle


def check_collision(obj_a, obj_b, margin=15):
    """True if two objects are currently within collision range (reactive check)."""
    return obj_a.distance_to(obj_b) < (obj_a.radius + obj_b.radius + margin)


def predict_collision(pos_a_now, pos_a_future, pos_b_now, pos_b_future, combined_radius, margin=15):
    """
    True if two objects moving in straight lines from their `now` to `future`
    positions come within (combined_radius + margin) of each other at any
    point along that path (predictive check, not just current distance).
    """
    steps = 10
    for i in range(steps + 1):
        t = i / steps
        ax = pos_a_now[0] + (pos_a_future[0] - pos_a_now[0]) * t
        ay = pos_a_now[1] + (pos_a_future[1] - pos_a_now[1]) * t
        bx = pos_b_now[0] + (pos_b_future[0] - pos_b_now[0]) * t
        by = pos_b_now[1] + (pos_b_future[1] - pos_b_now[1]) * t
        dist = math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
        if dist < (combined_radius + margin):
            return True
    return False


class CollisionManager:
    """
    Tracks all trackable objects, predicts near-future collisions, and
    coordinates avoidance so that dodging one object doesn't create a
    new collision with another (multi-object coordination).
    """

    def __init__(self, earth_x, earth_y, lookahead=2.0):
        self.earth_x = earth_x
        self.earth_y = earth_y
        self.lookahead = lookahead
        self.active_warnings = []  # list of (obj_a, obj_b) pairs currently at risk

    def _future_pos(self, obj):
        if isinstance(obj, Satellite):
            return obj.predict_position(self.lookahead, self.earth_x, self.earth_y)
        return obj.predict_position(self.lookahead)

    def update(self, objects):
        self.active_warnings = []
        satellite_threat_count = {}  # satellite -> how many threats already handled this frame

        n = len(objects)
        for i in range(n):
            for j in range(i + 1, n):
                a = objects[i]
                b = objects[j]

                now_a, now_b = (a.x, a.y), (b.x, b.y)
                future_a = self._future_pos(a)
                future_b = self._future_pos(b)
                combined_radius = a.radius + b.radius

                if predict_collision(now_a, future_a, now_b, future_b, combined_radius):
                    self.active_warnings.append((a, b))
                    a.warning = True
                    b.warning = True

                    # Whichever object(s) in the pair can maneuver get nudged.
                    # Each extra simultaneous threat pushes a satellite further
                    # out, so avoiding one object doesn't walk it into another.
                    for sat in (a, b):
                        if isinstance(sat, Satellite):
                            used = satellite_threat_count.get(sat, 0)
                            offset = 35 + used * 25
                            sat.start_avoidance(offset)
                            satellite_threat_count[sat] = used + 1

        at_risk = set()
        for a, b in self.active_warnings:
            at_risk.add(a)
            at_risk.add(b)
        for obj in objects:
            if obj not in at_risk:
                obj.warning = False
