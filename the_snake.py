from random import randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""
    
    def __init__(self, position=None, body_color=None):
        """Инициализирует игровой объект.
        
        Args:
            position (tuple): Начальная позиция объекта (x, y)
            body_color (tuple): Цвет объекта в формате RGB
        """
        self.position = position if position else (
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        )
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод для отрисовки объекта."""
        raise NotImplementedError(
            "Метод draw должен быть переопределен в дочернем классе"
        )
    
    def draw_cell(self, position=None):
        """Отрисовывает ячейку на игровом поле."""
        if position is None:
            position = self.position
            
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс для представления яблока в игре."""
    
    def __init__(self, position=None, body_color=APPLE_COLOR,
                 occupied_positions=None):
        """Инициализирует яблоко со случайной позицией и красным цветом."""
        super().__init__(position, body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Устанавливает случайную позицию для яблока на игровом поле.
        
        Args:
            occupied_positions (list): Список занятых позиций, которые нужно
                                       избегать
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            
            # Если нет занятых позиций или позиция свободна, выходим из цикла
            if (not occupied_positions or 
                    self.position not in occupied_positions):
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell()


class Snake(GameObject):
    """Класс для представления змейки в игре."""
    
    def __init__(self, position=None, body_color=SNAKE_COLOR):
        """Инициализирует змейку с начальными параметрами."""
        super().__init__(position, body_color)
        self.reset()

    def update_direction(self, next_direction=None):
        """Обновляет направление движения змейки.
        
        Args:
            next_direction (tuple): Новое направление движения
        """
        if next_direction:
            # Проверяем, не является ли новое направление противоположным
            # текущему
            opposite_directions = {
                UP: DOWN,
                DOWN: UP,
                LEFT: RIGHT,
                RIGHT: LEFT
            }
            
            if next_direction != opposite_directions.get(self.direction):
                self.direction = next_direction

    def get_head_position(self):
        """Возвращает позицию головы змейки.
        
        Returns:
            tuple: Координаты головы змейки (x, y)
        """
        return self.positions[0]

    def move(self):
        """Перемещает змейку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        )
        
        self.positions.insert(0, new_head)
        self.last = (self.positions.pop() 
                     if len(self.positions) > self.length else None)

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        # Отрисовка тела змейки
        for position in self.positions[1:]:
            self.draw_cell(position)
        
        # Отрисовка головы змейки
        self.draw_cell(self.get_head_position())
        
        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для управления змейкой.
    
    Args:
        game_object (Snake): Объект змейки, которым управляет игрок
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        
        if event.type == pg.KEYDOWN:
            # Выход из игры по ESC
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
                
            # Словарь соответствия клавиш и направлений
            key_direction_map = {
                pg.K_UP: UP,
                pg.K_DOWN: DOWN,
                pg.K_LEFT: LEFT,
                pg.K_RIGHT: RIGHT
            }
            
            # Получаем новое направление из словаря
            new_direction = key_direction_map.get(event.key)
            
            # Если клавиша соответствует одному из направлений, обновляем
            if new_direction:
                game_object.update_direction(new_direction)


def main():
    """Основная функция игры, содержащая главный игровой цикл."""
    pg.init()
    
    # Создание объектов игры
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    
    # Первоначальная отрисовка фона и объектов
    screen.fill(BOARD_BACKGROUND_COLOR)
    apple.draw()
    snake.draw()
    pg.display.update()
    
    # Флаг для отслеживания необходимости перерисовки фона
    need_redraw_background = False
    
    while True:
        clock.tick(SPEED)
        
        # Обработка ввода пользователя
        handle_keys(snake)
        
        # Перемещение змейки
        snake.move()
        
        # Проверка на съедание яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
            apple.draw()
        
        # Проверка на столкновение с собой
        elif snake.get_head_position() in snake.positions[1:]:
            # Устанавливаем флаг для перерисовки фона
            need_redraw_background = True
            snake.reset()
            apple.randomize_position(snake.positions)
        
        # Перерисовываем фон только при необходимости
        if need_redraw_background:
            screen.fill(BOARD_BACKGROUND_COLOR)
            need_redraw_background = False
            # Перерисовываем объекты после очистки фона
            apple.draw()
        
        # Отрисовка змейки
        snake.draw()
        
        # Обновление экрана
        pg.display.update()


if __name__ == '__main__':
    main()
