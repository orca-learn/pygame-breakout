#!/usr/bin/env python3
import pygame
pygame.init()
from colors import Colors
from paddle import Paddle
from ball import Ball
from brick import Brick
from score_manager import ScoreManager

# GLOBALS AND CONSTANTS ========================================================
# Window and Rendering ---------------------------------------------------------
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BG_COLOR = Colors.BLACK
# Scoring ----------------------------------------------------------------------
STARTING_LIVES = 1
# Paddle -----------------------------------------------------------------------
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_STARTING_POS = ((WINDOW_WIDTH - PADDLE_WIDTH) / 2, WINDOW_HEIGHT - 40)
PADDLE_COLOR = Colors.LIGHT_BLUE
# Ball -------------------------------------------------------------------------
BALL_SIZE = 10
BALL_STARTING_POS = ((WINDOW_WIDTH - BALL_SIZE) / 2, 350)
BALL_STARTING_DIRECTION = 200
BALL_SPEED = 7
BALL_COLOR = Colors.WHITE
# Bricks -----------------------------------------------------------------------
BRICK_ROWS = 1
BRICKS_PER_ROW = 1
BRICK_PADDING_X = 2
BRICK_PADDING_TOP = 5
BRICK_WIDTH = (WINDOW_WIDTH / BRICKS_PER_ROW) - 2 * BRICK_PADDING_X
BRICK_HEIGHT = 30
# Colors for each row, top to bottom
BRICK_ROW_COLORS = [
    Colors.RED,
    Colors.ORANGE,
    Colors.YELLOW,
    Colors.GREEN,
    Colors.BLUE,
]
# UI ---------------------------------------------------------------------------
# General
UI_COLOR = Colors.WHITE
UI_FONT = pygame.font.Font(None, 34)
# Score/Lives
UI_SCORE_POS = (20, 10)
UI_LIVES_POS = (650, 10)
# Top UI divider line
UI_LINE_Y = 38
UI_LINE_STROKE = 2
# Level complete text
LEVEL_END_TEXT_FONT = pygame.font.Font(None, 74)
LEVEL_END_TEXT_CENTER_POS = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
# Playfield --------------------------------------------------------------------
# Set top of playfield to just below UI
PLAYFIELD_TOP_Y = UI_LINE_Y + UI_LINE_STROKE

# PYGAME SETUP =================================================================
# Game Objects -----------------------------------------------------------------
# (Declaring here to be instantiated in setup_game())
# Global sprites list
sprites = None
# Paddle
paddle = None
# Ball
ball = None
# Sprites list of all bricks
bricks = None
# Object to keep track of score/lives
score_manager = None
# Window -----------------------------------------------------------------------
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Breakout')
# Clock ------------------------------------------------------------------------
clock = pygame.time.Clock()


# HELPERS ======================================================================

def spawn_ball():
    """Initialize ball and add to global sprites list."""
    global ball, sprites
    ball = Ball(BALL_COLOR, BALL_SIZE, BALL_STARTING_POS, BALL_STARTING_DIRECTION, BALL_SPEED,
                min_y=PLAYFIELD_TOP_Y)
    sprites.add(ball)


def setup_game():
    """Setup a fresh game (initialize all sprites, set score to 0, lives to 5)"""
    global ball, paddle, bricks, sprites, score_manager
    # Setup global sprites list
    sprites = pygame.sprite.Group()
    # Ball not spawned until player clicks
    ball = None
    # Paddle
    paddle = Paddle(PADDLE_COLOR, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_STARTING_POS)
    sprites.add(paddle)
    # Bricks
    bricks = pygame.sprite.Group()
    for r in range(BRICK_ROWS):
        for b in range(BRICKS_PER_ROW):
            # x = b * (l_pad + r_pad + width) + l_pad
            brick_x = b * (2 * BRICK_PADDING_X + BRICK_WIDTH) + BRICK_PADDING_X
            # y = top_y + r * (t_pad + height) + t_pad
            brick_y = PLAYFIELD_TOP_Y + r * (BRICK_PADDING_TOP + BRICK_HEIGHT) + BRICK_PADDING_TOP
            brick = Brick(BRICK_ROW_COLORS[r], BRICK_WIDTH, BRICK_HEIGHT, (brick_x, brick_y))
            bricks.add(brick)
    sprites.add(bricks)
    # Object to keep track of score
    score_manager = ScoreManager(STARTING_LIVES)


def finish_level(text_to_display, reset_game=True, wait_time=3000):
    """Show text in the center of the screen, pause for a bit, then optionally
    restart game.
    """
    finish_text = LEVEL_END_TEXT_FONT.render(text_to_display, True, UI_COLOR)
    finish_text_rect = finish_text.get_rect(center=LEVEL_END_TEXT_CENTER_POS)
    screen.blit(finish_text, finish_text_rect)
    pygame.display.flip()
    # TODO: no wait?
    if wait_time:
        pygame.time.wait(3000)
    # Reset game
    if reset_game:
        setup_game()


# MAIN LOOP ====================================================================
setup_game()
# Game continues as long as this is True
running = True
while running:
    # Event Loop ---------------------------------------------------------------
    for event in pygame.event.get():
        # Quit game
        if event.type == pygame.QUIT:
            running = False
    # Input Handlers -----------------------------------------------------------
    # Keys
    keys = pygame.key.get_pressed()
    # Quit on ESC
    if keys[pygame.K_ESCAPE]:
        running = False
    # Mouse
    mouse_buttons = pygame.mouse.get_pressed(3)
    # Spawn ball on click if not already in play
    if ball is None and mouse_buttons[0]:
        spawn_ball()
    # Paddle controls (mouse position)
    # paddle.set_center_x(pygame.mouse.get_pos()[0])
    # Game Logic ---------------------------------------------------------------
    if ball is not None:
        # Update ball position, determine if ball hit bottom
        lose_life = ball.update()
        # Paddle/ball collision
        if pygame.sprite.collide_mask(ball, paddle):
            diff = paddle.rect.centerx - ball.rect.centerx
            ball.h_bounce(paddle.rect.y - ball.size - 1, diff)
        # Brick/ball collision
        for i, brick in enumerate(pygame.sprite.spritecollide(ball, bricks, False)):
            # To avoid bug where ball direction changes twice on 1 axis (causing it to keep going the same way),
            # only bounce once during this frame.
            if i < 1:
                ball.handle_brick_collision(brick.rect)
            score_manager.add_points()
            """ brick.kill() """
        if len(bricks) == 0:
            finish_level('STAGE CLEAR')
        if lose_life:
            ball.kill()
            ball = None
            score_manager.lose_life()

    # Drawing ------------------------------------------------------------------
    # Background
    screen.fill(BG_COLOR)
    # UI border and text
    pygame.draw.line(screen, UI_COLOR, [0, UI_LINE_Y], [WINDOW_WIDTH, UI_LINE_Y], UI_LINE_STROKE)
    score_text = UI_FONT.render(f'Score: {score_manager.score}', True, UI_COLOR)
    lives_text = UI_FONT.render(f'Lives: {score_manager.lives}', True, UI_COLOR)
    screen.blit(score_text, UI_SCORE_POS)
    screen.blit(lives_text, UI_LIVES_POS)
    # Draw sprites
    sprites.draw(screen)
    # Render screen
    pygame.display.flip()

    # Handle game over
    if score_manager.lives <= 0:
        # Show game over then exit
        finish_level('GAME OVER')

    # Ticks --------------------------------------------------------------------
    clock.tick(FPS)

pygame.quit()
