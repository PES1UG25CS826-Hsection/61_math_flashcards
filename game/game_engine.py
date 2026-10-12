import random
import pygame
from game.text_box import TextBox


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.score = 0
        self.total_attempts = 0
        self.feedback_msg = "Solve the card and press Enter!"
        self.feedback_color = (200, 205, 215)

        self.num_a = 0
        self.num_b = 0
        self.operator = "+"

        box_w, box_h = 130, 44
        self.input_box = TextBox(width // 2 - 110, 230, box_w, box_h)
        self.submit_btn = pygame.Rect(width // 2 + 30, 230, 90, box_h)

        self.font_title = pygame.font.SysFont(None, 38)
        self.font_hud = pygame.font.SysFont(None, 26)
        self.font_card = pygame.font.SysFont(None, 56)
        self.font_btn = pygame.font.SysFont(None, 24)

        # Task 2: per-question timer
        self.time_limit_ms = 10000
        self.card_start_ms = 0

        # Task 3: streak multiplier
        self.streak = 0
        self.max_multiplier = 5

        self.generate_new_card()

    def generate_new_card(self):
        self.operator = random.choice(["+", "-", "*", "/"])

        if self.operator == "/":
            # Task 4: pick divisor and quotient first so the division is always exact
            divisor = random.randint(2, 12)
            quotient = random.randint(2, 12)
            self.num_a = divisor * quotient
            self.num_b = divisor
        else:
            self.num_a = random.randint(3, 15)
            self.num_b = random.randint(2, 12)
            if self.operator == "-" and self.num_a < self.num_b:
                self.num_a, self.num_b = self.num_b, self.num_a

        self.input_box.clear()
        self.card_start_ms = pygame.time.get_ticks()

    # Task 1: evaluate by operator instead of joining the numbers as text
    def compute_expected_answer(self):
        if self.operator == "+":
            return self.num_a + self.num_b
        elif self.operator == "-":
            return self.num_a - self.num_b
        elif self.operator == "*":
            return self.num_a * self.num_b
        elif self.operator == "/":
            return self.num_a // self.num_b
        raise ValueError(f"Unknown operator: {self.operator}")

    # Task 3: +1 multiplier for every 3 correct answers in a row, capped
    def current_multiplier(self):
        return min(1 + self.streak // 3, self.max_multiplier)

    def submit_answer(self):
        val_str = self.input_box.text.strip()
        if not val_str or val_str == "-":
            self.feedback_msg = "Type an answer first!"
            self.feedback_color = (240, 175, 40)
            return

        user_answer = int(val_str)
        expected = self.compute_expected_answer()
        self.total_attempts += 1

        if user_answer == expected:
            points = self.current_multiplier()
            self.score += points
            self.streak += 1
            self.feedback_msg = (
                f"CORRECT! {self.num_a} {self.operator} {self.num_b} = {expected}  (+{points})"
            )
            self.feedback_color = (80, 230, 110)
            self.generate_new_card()
        else:
            self.streak = 0
            self.feedback_msg = f"WRONG! Expected {expected}."
            self.feedback_color = (240, 75, 75)
            self.input_box.clear()

    def handle_event(self, event):
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.submit_answer()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_answer()

    def update(self):
        # Task 2: time ran out -> counts as a missed attempt (and resets the streak)
        elapsed = pygame.time.get_ticks() - self.card_start_ms
        if elapsed >= self.time_limit_ms:
            expected = self.compute_expected_answer()
            self.total_attempts += 1
            self.streak = 0
            self.feedback_msg = f"TIME'S UP! {self.num_a} {self.operator} {self.num_b} = {expected}"
            self.feedback_color = (240, 75, 75)
            self.generate_new_card()

    def render(self, screen):
        screen.fill((25, 29, 37))

        title_surf = self.font_title.render("Math Flashcards Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 18))

        score_surf = self.font_hud.render(f"Score: {self.score}   Attempts: {self.total_attempts}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 58))

        card_rect = pygame.Rect(self.width // 2 - 130, 95, 260, 110)
        pygame.draw.rect(screen, (240, 242, 245), card_rect, border_radius=12)
        pygame.draw.rect(screen, (85, 120, 175), card_rect, width=3, border_radius=12)

        card_str = f"{self.num_a}  {self.operator}  {self.num_b}"
        card_surf = self.font_card.render(card_str, True, (25, 30, 42))
        screen.blit(card_surf, (card_rect.centerx - card_surf.get_width() // 2, card_rect.centery - card_surf.get_height() // 2))

        # Task 2: countdown timer bar under the card
        remaining = max(0, self.time_limit_ms - (pygame.time.get_ticks() - self.card_start_ms))
        frac = remaining / self.time_limit_ms
        bar_bg = pygame.Rect(card_rect.x, card_rect.bottom + 8, card_rect.width, 10)
        bar_fill = pygame.Rect(bar_bg.x, bar_bg.y, int(bar_bg.width * frac), bar_bg.height)
        if frac > 0.5:
            bar_color = (80, 230, 110)
        elif frac > 0.25:
            bar_color = (240, 175, 40)
        else:
            bar_color = (240, 75, 75)
        pygame.draw.rect(screen, (60, 66, 80), bar_bg, border_radius=5)
        pygame.draw.rect(screen, bar_color, bar_fill, border_radius=5)

        self.input_box.render(screen)

        pygame.draw.rect(screen, (45, 140, 80), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (215, 225, 220), self.submit_btn, width=2, border_radius=6)
        btn_txt = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(btn_txt, (self.submit_btn.centerx - btn_txt.get_width() // 2, self.submit_btn.centery - btn_txt.get_height() // 2))

        msg_surf = self.font_hud.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(msg_surf, (self.width // 2 - msg_surf.get_width() // 2, 295))

        # Task 3: streak and multiplier display
        streak_color = (255, 150, 60) if self.streak >= 3 else (200, 205, 215)
        streak_surf = self.font_hud.render(
            f"Streak: {self.streak}   Multiplier: x{self.current_multiplier()}", True, streak_color
        )
        screen.blit(streak_surf, (self.width // 2 - streak_surf.get_width() // 2, 325))