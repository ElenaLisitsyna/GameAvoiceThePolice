import pygame
import random

# Инициализация Pygame
pygame.init()

# Определение констант
WIDTH, HEIGHT = 800, 600  # Размер окна
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)  # Цвет для первого игрокая
LIGHT_BLUE = (173, 216, 230)  # Цвет для второго игрока
TRANSLUCENT_RED = (255, 0, 0, 128)  # Полупрозрачный красный
GRAY = (169, 169, 169)  # Серый цвет фона для завершения игры
BROWN = (128, 0, 0)  # Бордовый цвет

# Загружаем изображение с обработкой ошибок
def load_image(name, size=(50, 100)):
    try:
        image = pygame.image.load(name)
        return pygame.transform.scale(image, size)
    except pygame.error as e:
        print(f"Ошибка загрузки изображения {name}: {e}")
        return pygame.Surface(size)

# Базовый класс для всех объектов
class GameObject:
    def __init__(self, image, x, y):
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Абстрактный класс для движущихся объектов
class MovableObject(GameObject):
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

# Класс игрока
class Player(MovableObject):
    def __init__(self, image, start_x, start_y, name, color):
        super().__init__(image, start_x, start_y)
        self.horizontal_speed = 5
        self.vertical_speed = 5
        self._lives = 5
        self.name = name
        self.color = color

    @property
    def lives(self):
        return self._lives

    def lose_life(self):
        if self._lives > 0:
            self._lives -= 1

    def reset(self):
        self.rect.center = (self.rect.centerx, self.rect.centery)  # Сброс по центральной оси x
        self._lives = 5

    def draw(self, surface):
        super().draw(surface)
        font = pygame.font.Font(None, 36)
        name_text = font.render(self.name, True, self.color)
        surface.blit(name_text, (self.rect.centerx - name_text.get_width() // 2, self.rect.y - 30))

    def move(self, dx, dy):
        if 0 <= self.rect.x + dx <= WIDTH - self.rect.width:
            self.rect.x += dx
        if 0 <= self.rect.y + dy <= HEIGHT - self.rect.height:
            self.rect.y += dy

# Класс препятствий
class Obstacle(MovableObject):
    def __init__(self):
        super().__init__(load_image("obstacle_car.png", size=(40, 80)), random.randint(0, WIDTH - 40), 0)
        self.speed = 3

    def update(self):
        self.move(0, self.speed)

# Класс бонусов
class Bonus(MovableObject):
    def __init__(self):
        super().__init__(load_image("bonus.png", size=(30, 30)), random.randint(0, WIDTH - 30), random.randint(0, HEIGHT // 2))
        self.speed = 2

    def update(self):
        self.move(0, self.speed)

# Класс игры
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Avoid the Police!")
        self.clock = pygame.time.Clock()

        # Загружаем фон
        self.background = load_image("background.png", size=(WIDTH, HEIGHT))

        # Создаем двух игроков с цветами
        self.player1 = Player(load_image("player_car.png", size=(40, 80)), WIDTH // 2 - 60, HEIGHT - 120, "Игрок 1", BLUE)
        self.player2 = Player(load_image("player2_car.png", size=(40, 80)), WIDTH // 2 + 60, HEIGHT - 120, "Игрок 2", LIGHT_BLUE)

        self.obstacles = []
        self.bonuses = []  # Список бонусов
        self.score = 0
        self.running = True
        self.collision_effect_duration = 0  # Время полупрозрачного эффекта
        self.collision_effect_max_duration = 20  # Количество кадров для эффекта
        self.collision_color = None  # Цвет столкновения

    def spawn_obstacle(self):
        if random.randint(1, 20) == 1:
            self.obstacles.append(Obstacle())

    def spawn_bonus(self):
        if random.randint(1, 30) == 1:  # Вероятность появления бонуса
            self.bonuses.append(Bonus())

    def handle_collisions(self):
        bonuses_to_remove = []  # Создаем список для удаления бонусов
        for obstacle in self.obstacles:
            if self.player1.rect.colliderect(obstacle.rect):
                self.player1.lose_life()
                self.obstacles.remove(obstacle)
                self.collision_effect_duration = self.collision_effect_max_duration
                self.collision_color = BLUE
                if self.player1.lives <= 0:
                    self.game_over(self.player1)

            if self.player2.rect.colliderect(obstacle.rect):
                self.player2.lose_life()
                self.obstacles.remove(obstacle)
                self.collision_effect_duration = self.collision_effect_max_duration
                self.collision_color = LIGHT_BLUE
                if self.player2.lives <= 0:
                    self.game_over(self.player2)

        # Проверка столкновений с бонусами
        for bonus in self.bonuses[:]:  # Проходим в копии списка
            if self.player1.rect.colliderect(bonus.rect):
                self.player1._lives += 1
                bonuses_to_remove.append(bonus)

            if self.player2.rect.colliderect(bonus.rect):
                self.player2._lives += 1
                bonuses_to_remove.append(bonus)

        # Удаляем бонусы после завершения цикла столкновений
        for bonus in bonuses_to_remove:
            if bonus in self.bonuses:  # Проверяем, есть ли в списке
                self.bonuses.remove(bonus)

    def game_over(self, loser):
        # Отображаем сообщение о завершении игры
        font = pygame.font.Font(None, 72)
        game_over_text = font.render(f"{loser.name} проиграл!", True, BROWN)

        restart_font = pygame.font.Font(None, 36)
        restart_text = restart_font.render("Нажмите R, чтобы начать заново", True, BLACK)
        exit_text = restart_font.render("Нажмите Esc для выхода", True, BLACK)

        while True:
            self.screen.fill(GRAY)  # Серый фон при завершении игры
            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
            self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))
            self.screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        return
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

    def reset_game(self):
        self.player1.reset()
        self.player2.reset()
        self.obstacles.clear()
        self.bonuses.clear()  # Очистка бонусов
        self.score = 0
        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.player1.move(-self.player1.horizontal_speed, 0)
            if keys[pygame.K_d]:
                self.player1.move(self.player1.horizontal_speed, 0)
            if keys[pygame.K_w]:
                self.player1.move(0, -self.player1.vertical_speed)
            if keys[pygame.K_s]:
                self.player1.move(0, self.player1.vertical_speed)

            if keys[pygame.K_LEFT]:
                self.player2.move(-self.player2.horizontal_speed, 0)
            if keys[pygame.K_RIGHT]:
                self.player2.move(self.player2.horizontal_speed, 0)
            if keys[pygame.K_UP]:
                self.player2.move(0, -self.player2.vertical_speed)
            if keys[pygame.K_DOWN]:
                self.player2.move(0, self.player2.vertical_speed)

            self.spawn_obstacle()
            self.spawn_bonus()  # Спавн бонусов
            for obstacle in self.obstacles:
                obstacle.update()
                if obstacle.rect.y > HEIGHT:
                    self.obstacles.remove(obstacle)
                    self.score += 1

            for bonus in self.bonuses:
                bonus.update()
                if bonus.rect.y > HEIGHT:
                    self.bonuses.remove(bonus)  # Удаляем бонус, если он вышел за пределы экрана

            self.handle_collisions()

            # Отрисовка
            self.screen.blit(self.background, (0, 0))  # Рисуем фон

            if self.collision_effect_duration > 0:
                self.screen.fill(self.collision_color)  # Изменяем цвет фона в момент столкновения
                self.collision_effect_duration -= 1

            self.player1.draw(self.screen)
            self.player2.draw(self.screen)
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)
            for bonus in self.bonuses:
                bonus.draw(self.screen)  # Рисуем бонусы

            # Отображение счета и жизней
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Счет: {self.score}", True, BLACK)
            lives_text1 = font.render(f"Жизни Игрока 1: {self.player1.lives}", True, BLUE)
            lives_text2 = font.render(f"Жизни Игрока 2: {self.player2.lives}", True, LIGHT_BLUE)

            self.screen.blit(score_text, (10, 10))
            self.screen.blit(lives_text1, (10, 50))
            self.screen.blit(lives_text2, (10, 90))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()