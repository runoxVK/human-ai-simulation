import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Human Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)  # Green color for plants
LIGHT_BLUE = (173, 216, 230)  # Light blue color for puddles
DARK_BLUE = (0, 0, 139)  # Darker blue for the border
GRAY = (128, 128, 128)  # Gray color for the sleeping text

# Fonts
font = pygame.font.SysFont(None, 24)

# Human Class
class Human:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.water = 100
        self.hunger = 100
        self.energy = 100
        self.alive = True
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.speed = 1
        self.change_direction_timer = 0
        self.nearest_puddle = None
        self.sleeping = False
        self.sleep_timer = 0  # Timer for how long the human has been sleeping
        self.target_animal = None
        self.target_plant = None

    def update_stats(self):
        # Continue decreasing water and hunger even when sleeping
        self.water -= 0.05
        self.hunger -= 0.03

        if self.sleeping:
            self.sleep_timer += 1
            if self.sleep_timer >= 600:  # 10 seconds = 600 frames (assuming 60 FPS)
                self.energy = 100
                self.sleeping = False
                self.sleep_timer = 0
        else:
            # Decrease energy if not sleeping
            self.energy -= 0.02

            # Check if the human is still alive
            if self.water <= 0 or self.hunger <= 0 or self.energy <= 0:
                self.alive = False

    def move(self, puddles, animals, plants):
        if not self.alive:
            return

        if self.sleeping:
            return

        # Priority: Water -> Food -> Sleep -> Roaming
        if self.water < 80:
            self.seek_water(puddles)
        elif self.hunger < 50:
            self.seek_food(animals, plants)
        elif self.energy < 50:
            self.sleeping = True
        else:
            self.random_movement()

    def seek_water(self, puddles):
        self.nearest_puddle = min(
            puddles,
            key=lambda p: math.hypot(self.x - p[0], self.y - p[1]),
            default=None
        )
        if self.nearest_puddle:
            target_x, target_y, _, _ = self.nearest_puddle
            self.move_towards(target_x, target_y)

            if math.hypot(self.x - target_x, self.y - target_y) < 20:
                self.water = 100
                self.nearest_puddle = None

    def seek_food(self, animals, plants):
        if not self.target_animal or self.target_animal not in animals:
            self.target_animal = min(
                animals,
                key=lambda a: math.hypot(self.x - a.x, self.y - a.y),
                default=None
            )

        if self.target_animal:
            target_x, target_y = self.target_animal.x, self.target_animal.y
            self.move_towards(target_x, target_y)

            if math.hypot(self.x - target_x, self.y - target_y) < 10:
                animals.remove(self.target_animal)
                self.hunger = 100
                self.target_animal = None
        elif not self.target_plant or self.target_plant not in plants:
            self.target_plant = min(
                plants,
                key=lambda p: math.hypot(self.x - p[0], self.y - p[1]),
                default=None
            )

        if self.target_plant:
            target_x, target_y = self.target_plant
            self.move_towards(target_x, target_y)

            if math.hypot(self.x - target_x, self.y - target_y) < 10:
                plants.remove(self.target_plant)
                self.hunger = min(100, self.hunger + 20)
                self.target_plant = None

    def move_towards(self, target_x, target_y):
        direction_x = target_x - self.x
        direction_y = target_y - self.y
        distance = math.hypot(direction_x, direction_y)

        if distance > 0:
            self.dx = direction_x / distance
            self.dy = direction_y / distance

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def random_movement(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        if self.x < 0 or self.x > WIDTH:
            self.dx *= -1
        if self.y < 0 or self.y > HEIGHT:
            self.dy *= -1

        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))

        self.change_direction_timer += 1
        if self.change_direction_timer >= 60:
            self.dx = random.uniform(-1, 1)
            self.dy = random.uniform(-1, 1)
            self.change_direction_timer = 0

    def draw(self, surface):
        if self.alive:
            pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), 10)
            self.draw_stats(surface)

    def draw_stats(self, surface):
        water_text = font.render(f"Water: {int(self.water)}", True, RED)
        hunger_text = font.render(f"Hunger: {int(self.hunger)}", True, RED)
        energy_text = font.render(f"Energy: {int(self.energy)}", True, RED)

        text_y_offset = 20
        total_text_height = 4 * text_y_offset
        start_y = self.y - 30 - total_text_height

        surface.blit(water_text, (self.x - water_text.get_width() // 2, start_y))
        surface.blit(hunger_text, (self.x - hunger_text.get_width() // 2, start_y + text_y_offset))
        surface.blit(energy_text, (self.x - energy_text.get_width() // 2, start_y + 2 * text_y_offset))

        if self.sleeping:
            sleeping_text = font.render("Sleeping...", True, GRAY)
            surface.blit(sleeping_text, (self.x - sleeping_text.get_width() // 2, start_y + 3 * text_y_offset))

# Animal Class
class Animal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-0.5, 0.5)
        self.dy = random.uniform(-0.5, 0.5)
        self.speed = 0.8

    def move(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        if self.x < 0 or self.x > WIDTH:
            self.dx *= -1
        if self.y < 0 or self.y > HEIGHT:
            self.dy *= -1

        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), 5)

# Create multiple humans
humans = [Human(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(10)]

# Create random water puddles with larger and irregular shapes
puddle_radius = 40
puddles = []
for _ in range(5):
    x = random.randint(puddle_radius, WIDTH - puddle_radius)
    y = random.randint(puddle_radius, HEIGHT - puddle_radius)
    width = random.randint(puddle_radius, puddle_radius + 40)
    height = random.randint(puddle_radius, puddle_radius + 40)
    puddles.append((x, y, width, height))

# Create animals
animals = [Animal(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(5)]

# Create plants
plants = [(random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10)) for _ in range(10)]

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update and draw each human
    window.fill(WHITE)
    
    # Draw puddles
    for puddle in puddles:
        x, y, width, height = puddle
        pygame.draw.ellipse(window, LIGHT_BLUE, (x - width//2, y - height//2, width, height))
        pygame.draw.ellipse(window, DARK_BLUE, (x - width//2, y - height//2, width, height), 2)

    # Draw plants
    for plant in plants:
        pygame.draw.circle(window, GREEN, plant, 5)
    
    for human in humans[:]:
        human.update_stats()
        human.move(puddles, animals, plants)
        if human.alive:
            human.draw(window)
        else:
            humans.remove(human)

    # Update and draw animals
    for animal in animals:
        animal.move()
        animal.draw(window)

    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

pygame.quit()
