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
GREEN = (0, 255, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
PINK = (255, 192, 203)

# Fonts
font = pygame.font.SysFont(None, 24)

# Load the background image
background_image = pygame.image.load('dessert_blank.png').convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Human Class
class Human:
    def __init__(self, x, y, generation=1):
        self.x = x
        self.y = y
        self.water = 100
        self.hunger = 100
        self.energy = 100
        self.age = 0
        self.death_age = random.randint(70, 100)  # Random death age between 70 and 100
        self.generation = generation
        self.alive = True
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.speed = 1
        self.change_direction_timer = 0
        self.nearest_puddle = None
        self.sleeping = False
        self.sleep_timer = 0
        self.target_animal = None
        self.target_plant = None
        self.target_mate = None
        self.gender = random.choice(['male', 'female'])
        self.last_breed_time = 0
        self.breed_cooldown = 45000  # 45 seconds cooldown in milliseconds

    def update_stats(self):
        if not self.alive:
            return

        # Continue decreasing water and hunger even when sleeping
        self.water -= 0.05
        self.hunger -= 0.03

        if self.sleeping:
            self.sleep_timer += 1
            if self.sleep_timer >= 600:
                self.energy = 100
                self.sleeping = False
                self.sleep_timer = 0
        else:
            self.energy -= 0.02

            # Check if the human is still alive
            if self.water <= 0 or self.hunger <= 0 or self.energy <= 0 or self.age >= self.death_age:
                self.alive = False

    def move(self, puddles, animals, plants, humans):
        if not self.alive or self.sleeping:
            return

        # Priority: Water -> Food -> Sleep -> Breeding -> Roaming
        if self.water < 80:
            self.seek_water(puddles)
        elif self.hunger < 50:
            self.seek_food(animals, plants)
        elif self.energy < 50:
            self.sleeping = True
        elif self.water >= 80 and self.hunger >= 50 and self.energy >= 50 and self.age > 25:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_breed_time >= self.breed_cooldown:
                self.breed(humans)
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

    def breed(self, humans):
        if self.gender == 'male':
            potential_mates = [h for h in humans if h.gender == 'female' and h != self and h.alive and not h.sleeping]
        else:
            potential_mates = [h for h in humans if h.gender == 'male' and h != self and h.alive and not h.sleeping]

        if not potential_mates:
            return

        if not self.target_mate or self.target_mate not in potential_mates:
            self.target_mate = min(
                potential_mates,
                key=lambda h: math.hypot(self.x - h.x, self.y - h.y),
                default=None
            )

        if self.target_mate:
            target_x, target_y = self.target_mate.x, self.target_mate.y
            self.move_towards(target_x, target_y)

            if math.hypot(self.x - target_x, self.y - target_y) < 10:
                # Check if breeding cooldown is complete
                if pygame.time.get_ticks() - self.last_breed_time >= self.breed_cooldown:
                    # Create a new human
                    new_x = self.x + random.randint(-20, 20)
                    new_y = self.y + random.randint(-20, 20)
                    new_generation = self.generation + 1
                    humans.append(Human(new_x, new_y, generation=new_generation))
                    self.last_breed_time = pygame.time.get_ticks()  # Update last breed time
                    self.target_mate = None

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
            if self.gender == 'male':
                pygame.draw.circle(surface, BLUE, (int(self.x), int(self.y)), 5)
            else:
                pygame.draw.circle(surface, PINK, (int(self.x), int(self.y)), 5)
            self.draw_stats(surface)

    def draw_stats(self, surface):
        water_text = font.render(f"Water: {int(self.water)}", True, RED)
        hunger_text = font.render(f"Hunger: {int(self.hunger)}", True, RED)
        energy_text = font.render(f"Energy: {int(self.energy)}", True, RED)
        age_text = font.render(f"Age: {self.age}", True, RED)
        death_age_text = font.render(f"Death Age: {self.death_age}", True, RED)
        generation_text = font.render(f"Gen: {self.generation}", True, RED)

        text_y_offset = 20
        total_text_height = 8 * text_y_offset
        start_y = self.y - 30 - total_text_height

        surface.blit(water_text, (self.x - water_text.get_width() // 2, start_y))
        surface.blit(hunger_text, (self.x - hunger_text.get_width() // 2, start_y + text_y_offset))
        surface.blit(energy_text, (self.x - energy_text.get_width() // 2, start_y + 2 * text_y_offset))
        surface.blit(age_text, (self.x - age_text.get_width() // 2, start_y + 3 * text_y_offset))
        surface.blit(death_age_text, (self.x - death_age_text.get_width() // 2, start_y + 4 * text_y_offset))
        surface.blit(generation_text, (self.x - generation_text.get_width() // 2, start_y + 5 * text_y_offset))

        if self.sleeping:
            sleep_text = font.render("Sleeping", True, GRAY)
            surface.blit(sleep_text, (self.x - sleep_text.get_width() // 2, start_y + 6 * text_y_offset))

# Animal Class
class Animal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-0.5, 0.5)
        self.dy = random.uniform(-0.5, 0.5)
        self.speed = 0.6  # Increased speed

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
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), 5)  # Moving red dots

# Create initial humans, plants, and animals
humans = [Human(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(10)]
puddles = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), 60, 30) for _ in range(5)]  # Larger puddles
plants = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(10)]
animals = [Animal(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(5)]

# Main loop
running = True
clock = pygame.time.Clock()
last_age_update = pygame.time.get_ticks()
last_respawn_time = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = pygame.time.get_ticks()

    # Draw the background image
    window.blit(background_image, (0, 0))

    # Draw puddles
    for puddle in puddles:
        x, y, width, height = puddle
        pygame.draw.ellipse(window, LIGHT_BLUE, (x - width // 2, y - height // 2, width, height))
        pygame.draw.ellipse(window, DARK_BLUE, (x - width // 2, y - height // 2, width, height), 2)  # Larger puddles

    # Draw plants
    for plant in plants:
        pygame.draw.circle(window, GREEN, plant, 10)  # Larger plants

    # Update age
    if current_time - last_age_update >= 2000:
        last_age_update = current_time
        for human in humans:
            if human.alive:
                human.age += 1

    for human in humans[:]:
        human.update_stats()
        human.move(puddles, animals, plants, humans)
        if human.alive:
            human.draw(window)
        else:
            humans.remove(human)

    # Update and draw animals
    for animal in animals:
        animal.move()
        animal.draw(window)

    # Add new plants and animals every 60 seconds
    if current_time - last_respawn_time >= 60000:
        last_respawn_time = current_time
        plants.extend([(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(20)])
        animals.extend([Animal(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(10)])

    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

pygame.quit()
