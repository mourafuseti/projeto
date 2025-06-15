import pygame
import random
import asyncio
import platform
import os

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo de Nave")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Configurações de FPS
FPS = 60  # Definido globalmente para garantir acesso

# Carregar imagens
player_img = pygame.image.load(os.path.join('assets', 'player.png')).convert_alpha()
player_img = pygame.transform.scale(player_img, (150, 150))  # Tamanho 3x
enemy_img = pygame.image.load(os.path.join('assets', 'enemy.png')).convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (50, 50))  # Tamanho original do inimigo
boss_img = pygame.image.load(os.path.join('assets', 'boss.png')).convert_alpha()
boss_img = pygame.transform.scale(boss_img, (150, 150))  # Tamanho 3x do inimigo

# Configurações da nave
player_width = 150
player_height = 150
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 5

# Configurações dos projéteis
bullet_width = 5
bullet_height = 10
bullet_speed = 7
bullets = []

# Configurações dos inimigos
enemy_width = 50
enemy_height = 50
enemy_speed = 3
enemies = []

# Configurações do chefão
boss_active = False
boss_hits = 0
boss_width = 150  # 3x o tamanho do inimigo
boss_height = 150
boss_x = WIDTH // 2 - boss_width // 2
boss_y = 50
boss_speed = 4
boss_direction = 1  # 1 para direita, -1 para esquerda

# Configurações do placar
score = 0
font = pygame.font.SysFont('arial', 30)

# Configurações do botão de reiniciar
button_width = 200
button_height = 50
button_x = WIDTH // 2 - button_width // 2
button_y = HEIGHT // 2 - button_height // 2
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

# Estado do jogo
game_over = False
running = True


def setup():
    global running, player_x, score, bullets, enemies, game_over, boss_active, boss_hits, boss_x, boss_y, boss_direction
    running = True
    game_over = False
    score = 0
    bullets = []
    enemies = []
    boss_active = False
    boss_hits = 0
    boss_x = WIDTH // 2 - boss_width // 2
    boss_y = 50
    boss_direction = 1
    player_x = WIDTH // 2 - player_width // 2
    # Evento para spawnar inimigos
    pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # Spawn a cada 1 segundo


def draw_player():
    screen.blit(player_img, (player_x, player_y))


def draw_bullet(bullet):
    pygame.draw.rect(screen, WHITE, (bullet[0], bullet[1], bullet_width, bullet_height))


def draw_enemy(enemy):
    screen.blit(enemy_img, (enemy[0], enemy[1]))


def draw_boss():
    screen.blit(boss_img, (boss_x, boss_y))  # Usar boss.png


def draw_score():
    score_text = font.render(f'Pontos: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))


def draw_game_over():
    button_text = font.render('Reiniciar', True, BLACK)
    pygame.draw.rect(screen, GREEN, button_rect)
    screen.blit(button_text, (button_x + 50, button_y + 10))


def reset_game():
    global score, bullets, enemies, game_over, player_x, boss_active, boss_hits, boss_x, boss_y, boss_direction
    score = 0
    bullets = []
    enemies = []
    boss_active = False
    boss_hits = 0
    boss_x = WIDTH // 2 - boss_width // 2
    boss_y = 50
    boss_direction = 1
    game_over = False
    player_x = WIDTH // 2 - player_width // 2
    pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # Reativar spawn de inimigos


def update_loop():
    global player_x, running, game_over, score, boss_active, boss_hits, boss_x, boss_y, boss_direction

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_SPACE:
                bullets.append([player_x + player_width // 2 - bullet_width // 2, player_y])
        elif event.type == pygame.USEREVENT + 1 and not game_over and not boss_active:
            enemies.append([random.randint(0, WIDTH - enemy_width), 0])
        elif event.type == pygame.MOUSEBUTTONDOWN and game_over:
            if button_rect.collidepoint(event.pos):
                reset_game()

    if not game_over:
        # Movimento da nave
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed

        # Ativar chefão quando atingir 100 pontos
        if score >= 100 and not boss_active:
            boss_active = True
            enemies.clear()  # Limpar inimigos normais
            boss_x = WIDTH // 2 - boss_width // 2
            boss_y = 50  # Garantir que boss_y está inicializado
            boss_direction = 1

        # Movimento do chefão
        if boss_active:
            boss_x += boss_speed * boss_direction
            if boss_x <= 0 or boss_x >= WIDTH - boss_width:
                boss_direction *= -1  # Inverter direção ao tocar as bordas

        # Atualizar projéteis
        for bullet in bullets[:]:
            bullet[1] -= bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)

        # Atualizar inimigos
        for enemy in enemies[:]:
            enemy[1] += enemy_speed
            if enemy[1] > HEIGHT:
                enemies.remove(enemy)

            # Verificar colisão com a nave
            if (player_x < enemy[0] + enemy_width and
                    player_x + player_width > enemy[0] and
                    player_y < enemy[1] + enemy_height and
                    player_y + player_height > enemy[1]):
                game_over = True

            # Verificar colisão com projéteis
            for bullet in bullets[:]:
                if (bullet[0] < enemy[0] + enemy_width and
                        bullet[0] + bullet_width > enemy[0] and
                        bullet[1] < enemy[1] + enemy_height and
                        bullet[1] + bullet_height > enemy[1]):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    score += 10  # Adicionar 10 pontos por inimigo destruído
                    break

        # Verificar colisão com o chefão
        if boss_active:
            if (player_x < boss_x + boss_width and
                    player_x + player_width > boss_x and
                    player_y < boss_y + boss_height and
                    player_y + player_height > boss_y):
                game_over = True

            for bullet in bullets[:]:
                if (bullet[0] < boss_x + boss_width and
                        bullet[0] + bullet_width > boss_x and
                        bullet[1] < boss_y + boss_height and
                        bullet[1] + bullet_height > boss_y):
                    bullets.remove(bullet)
                    boss_hits += 1
                    score += 50  # 50 pontos por acerto no chefão
                    if score >= 600:  # Chefão destruído aos 600 pontos
                        boss_active = False
                        boss_hits = 0
                        boss_x = WIDTH // 2 - boss_width // 2
                        boss_y = 50
                        boss_direction = 1
                        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # Reativar spawn de inimigos

    # Desenhar
    screen.fill(BLACK)
    draw_player()
    for bullet in bullets:
        draw_bullet(bullet)
    for enemy in enemies:
        draw_enemy(enemy)
    if boss_active:
        draw_boss()
    draw_score()
    if game_over:
        draw_game_over()

    pygame.display.flip()


async def main():
    setup()
    while running:
        update_loop()
        await asyncio.sleep(1.0 / FPS)  # FPS está definido globalmente


if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())