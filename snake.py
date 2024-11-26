import os
import sys
import termios
import tty
import random

from threading import Thread
from time import sleep

class Color:
    SNAKE = "\033[34;44m"
    FOOD = "\033[31;41m"
    RESEST = "\033[m"
    EMPTY = "\033[37;47m"
    WALL = "\033[30;40m"

class Snake:
    DIR_LEFT = "left"
    DIR_RIGHT = "right"
    DIR_UP = "up"
    DIR_DOWN = "down"
    
    DIR_TO_COORD = {
        DIR_LEFT: (-1, 0),
        DIR_RIGHT: (1, 0),
        DIR_UP: (0, -1),
        DIR_DOWN: (0, 1)
    }

    def __init__(self, size, head_x, head_y):
        self.size = size
        self.direction = Snake.DIR_RIGHT
        # Head is always parts[0] and tail is always parts[-1]
        self.parts = []
        for i in range(size):
            self.parts.append((head_x-i, head_y))
        
    def update_head_position(self):
        head = self.parts[0]
        new_head_x = head[0] + Snake.DIR_TO_COORD[self.direction][0]
        new_head_y = head[1] + Snake.DIR_TO_COORD[self.direction][1]
        self.parts.insert(0, (new_head_x, new_head_y))
        
    def remove_tail(self):
        self.parts.pop()
        
    def get_parts(self):
        return self.parts
    
    def has_hit(self):
        for part in self.parts[1:]:
            if part == self.parts[0]:
                return True
        return False
            


class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [["_" for _ in range(width)] for _ in range(height)]
        self.snake = Snake(3, 3, 5)
        self.start_input_thread()
        self.food_x = width - 1
        self.food_y = height - 1
        
        
    
    def start_input_thread(self):
        input_thread = Thread(target=self.read_input)
        input_thread.start()
        
    def read_input(self):
        K_RIGHT = b'\x1b[C'
        K_LEFT  = b'\x1b[D'
        K_UP  = b'\x1b[A'
        K_DOWN = b'\x1b[B'
        for key in self.read_keys():
            if key == K_LEFT:
                if self.snake.direction != Snake.DIR_RIGHT:
                    self.snake.direction = Snake.DIR_LEFT
            elif key == K_RIGHT:
                if self.snake.direction != Snake.DIR_LEFT:
                    self.snake.direction = Snake.DIR_RIGHT
            elif key == K_UP:
                if self.snake.direction != Snake.DIR_DOWN:
                    self.snake.direction = Snake.DIR_UP
            elif key == K_DOWN:
                if self.snake.direction != Snake.DIR_UP:
                    self.snake.direction = Snake.DIR_DOWN
        
        
    def read_keys(self):
        stdin = sys.stdin.fileno()
        tattr = termios.tcgetattr(stdin)
        try:
            tty.setcbreak(stdin, termios.TCSANOW)
            while True:
                yield sys.stdin.buffer.read1()
        except KeyboardInterrupt:
            yield None
        finally:
            termios.tcsetattr(stdin, termios.TCSANOW, tattr)

        
        
    def reset_board(self):
        for y in range(self.height):
            for x in range(self.width):
                self.board[y][x] = "_"
    
    
    def show_snake(self):
        snake_parts = self.snake.get_parts()
        for part in snake_parts:
            part_x = part[0]
            part_y = part[1]
            self.board[part_y][part_x] = "S"
            
    def snake_hit_food(self):
        snake_head_pos = self.snake.parts[0]
        food_pos = (self.food_x, self.food_y)
        return snake_head_pos == food_pos
    
    def snake_hit_walls(self):
        snake_head_x = self.snake.parts[0][0]
        snake_head_y = self.snake.parts[0][1]
        return snake_head_x > self.width - 1 or snake_head_x < 0 or snake_head_y > self.height - 1 or snake_head_y < 0
            
    def new_food(self):
        while True:
            random_place_x = random.randint(0, self.width - 1)
            random_place_y = random.randint(0, self.height - 1)
            if self.board[random_place_y][random_place_x] != "S":
                self.food_x = random_place_x
                self.food_y = random_place_y
                break
    
    def show_food(self):
        self.board[self.food_y][self.food_x] = "F"
        
        
    def print_board(self):
        print(Color.WALL, "==" * (self.width + 2), Color.RESEST, sep="")
        for y in range(self.height):
            print(Color.WALL, "==", Color.RESEST, sep="", end="")
            for x in range(self.width):
                if self.board[y][x] == "_":
                    print(Color.EMPTY, "__",Color.RESEST, end="", sep="")
                if self.board[y][x] == "S":
                    print(Color.SNAKE, "__",Color.RESEST, end="", sep="")
                if self.board[y][x] == "F":
                    print(Color.FOOD, "__",Color.RESEST, end="", sep="")
            print(Color.WALL, "==", Color.RESEST, sep="")
        print(Color.WALL, "==" * (self.width + 2), Color.RESEST, sep="")
        
    
    def play(self):
        while True:
            if self.snake_hit_food():
               self.new_food()
            else:
                self.snake.remove_tail()
            self.snake.update_head_position()
            
            if self.snake_hit_walls() or self.snake.has_hit():
                print("GAME OVER")
                return
            
            os.system("clear")
            self.reset_board()
            self.show_snake()
            self.show_food()
            self.print_board()
            sleep(0.1)
        
        

game = Game(30, 15)
game.play()