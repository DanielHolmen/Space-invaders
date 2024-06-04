import pygame
import random

# Initialiser Pygame
pygame.init()

# Sett opp skjermen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Farger
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Spilletid
clock = pygame.time.Clock()
FPS = 60

# Poeng
score = 0
font = pygame.font.SysFont(None, 36)

class Ship:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 10
        self.velocity = 7
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.lives = 3

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.velocity
        if keys[pygame.K_RIGHT] and self.rect.x < WIDTH - self.width:
            self.rect.x += self.velocity

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

class Bullet:
    def __init__(self, x, y, velocity, color):
        self.width = 5
        self.height = 10
        self.velocity = velocity
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = color

    def move(self):
        self.rect.y += self.velocity

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Alien:
    def __init__(self, x, y):
        self.width = 40
        self.height = 30
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)

class Shield:
    def __init__(self, x, y):
        self.width = 60
        self.height = 20
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.health = 3

    def draw(self, screen):
        colors = [WHITE, (200, 200, 200), (150, 150, 150), (100, 100, 100)]
        pygame.draw.rect(screen, colors[self.health], self.rect)

def create_aliens(rows, cols):
    aliens = []
    for row in range(rows):
        for col in range(cols):
            x = col * (alien_width + 10) + 50
            y = row * (alien_height + 10) + 50
            aliens.append(Alien(x, y))
    return aliens

def create_shields():
    return [
        Shield(WIDTH // 4 - 30, HEIGHT - 100),
        Shield(WIDTH // 2 - 30, HEIGHT - 100),
        Shield(3 * WIDTH // 4 - 30, HEIGHT - 100)
    ]

def game_over_screen():
    screen.fill(BLACK)
    game_over_text = font.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

# Romskip
ship = Ship()

# Skudd
player_bullets = []
alien_bullets = []

# Romvesener
alien_width, alien_height = 40, 30
alien_velocity_x = 2
alien_velocity_y = 30
aliens = create_aliens(5, 11)
alien_speed_multiplier = 1.1

# Skjold
shields = create_shields()

# Hovedsløyfe
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet_x = ship.rect.x + ship.width // 2 - 2.5
                bullet_y = ship.rect.y
                player_bullets.append(Bullet(bullet_x, bullet_y, -10, RED))

    # Beveg romskipet
    keys = pygame.key.get_pressed()
    ship.move(keys)

    # Beveg skudd
    for bullet in player_bullets:
        bullet.move()
        if bullet.rect.y < 0:
            player_bullets.remove(bullet)

    for bullet in alien_bullets:
        bullet.move()
        if bullet.rect.y > HEIGHT:
            alien_bullets.remove(bullet)

    # Beveg romvesenene
    move_down = False
    for alien in aliens:
        alien.rect.x += alien_velocity_x
        if alien.rect.right >= WIDTH or alien.rect.left <= 0:
            move_down = True

    if move_down:
        for alien in aliens:
            alien.rect.y += alien_velocity_y
        alien_velocity_x *= -1

    # Kollisjonssjekk for skudd mot romvesener
    for bullet in player_bullets:
        for alien in aliens:
            if bullet.rect.colliderect(alien.rect):
                player_bullets.remove(bullet)
                aliens.remove(alien)
                score += 10
                break  # Avbryt loopen når kulen treffer et romvesen
                
        for shield in shields:
            if bullet.rect.colliderect(shield.rect):
                player_bullets.remove(bullet)
                shield.health -= 1
                if shield.health <= 0:
                    shields.remove(shield)
                break  # Avbryt loopen når kulen treffer et skjold
                
    for bullet in alien_bullets:
        for shield in shields:
            if bullet.rect.colliderect(shield.rect):
                alien_bullets.remove(bullet)
                shield.health -= 1
                if shield.health <= 0:
                    shields.remove(shield)
                break  # Avbryt loopen når kulen treffer et skjold
                
        if bullet.rect.colliderect(ship.rect):
            alien_bullets.remove(bullet)
            ship.lives -= 1
            if ship.lives <= 0:
                game_over_screen()
                running = False

    # Kollisjonssjekk for romvesener mot skjold
    for alien in aliens:
        for shield in shields:
            if alien.rect.colliderect(shield.rect):
                aliens.remove(alien)
                shield.health -= 1
                if shield.health <= 0:
                    shields.remove(shield)
                break  # Avbryt loopen når et romvesen treffer et skjold
                
        if alien.rect.colliderect(ship.rect):
            ship.lives -= 1
            if ship.lives <= 0:
                game_over_screen()
                running = False
            break  # Avbryt loopen når et romvesen treffer skipet
        
        if alien.rect.y >= HEIGHT:
            ship.lives -= 1
            if ship.lives <= 0:
                game_over_screen()
                running = False
            break  # Avbryt loopen når et romvesen når bunnen

    # Romvesener som skyter
    if random.random() < 0.02 and aliens:  # Sjekk at det finnes romvesener
        shooting_alien = random.choice(aliens)
        bullet_x = shooting_alien.rect.x + shooting_alien.width // 2 - 2.5
        bullet_y = shooting_alien.rect.y + shooting_alien.height
        alien_bullets.append(Bullet(bullet_x, bullet_y, 10, GREEN))

    # Tegn alt
    ship.draw(screen)

    for bullet in player_bullets:
        bullet.draw(screen)

    for bullet in alien_bullets:
        bullet.draw(screen)

    for alien in aliens:
        alien.draw(screen)

    for shield in shields:
        shield.draw(screen)

    # Oppdater poeng og liv
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {ship.lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 100, 10))

    # Sjekk om alle romvesenene er fjernet
    if not aliens:
        alien_velocity_x = 2  # Reset X-hastighet for nye romvesener
        alien_velocity_y = 30  # Reset Y-hastighet for nye romvesener
        aliens = create_aliens(5, 11)
        shields = create_shields()
        ship.lives += 1

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()