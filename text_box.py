import pygame
import globals as g
from constants import *

class Blitted_rect(object):
    def __init__(self, size, position, color):
        self.rectangle = pygame.Surface(size)
        self.rectangle.fill(color)
        self.position = position
        g.screen.blit(self.rectangle, self.position)

class TextBox(Blitted_rect):
    # takes tree tuples like (height,width), (left,top),(r,g,b) and Text size

    # color is for the backround of the text

    def __init__(self, size, position, color, font, text_size):
        Blitted_rect.__init__(self, size, position, color)
        self.font = pygame.font.Font(font, text_size)
        self.size = size
        self.x_pos = self.position[0] + 10
        self.y_pos = self.position[1] + 5
        #self.rect = self.image.get_rect()
        # self.rect.topleft = position                # positions text boxes
        self.wait = False

    # writes the text to the surface we created
    def setText(self, text):
        # loops through the list of words writing them to the self.image surface
        words = text.split()
        for word in words:
            # text is the text object which needs to be blitted to the screen at
            text = self.font.render(word, True, (255, 255, 255))
            text_rect = text.get_rect()
            # if the word comes within five pixels of the edge move down a line
            if (self.x_pos + text_rect.width > self.position[0] + self.size[0]-5):
                self.x_pos = self.position[0]+10
                self.y_pos += 33
            g.screen.blit(text, (self.x_pos, self.y_pos))
            if self.wait is True:
                #delay between words so that it scroles
                pygame.time.wait(80)
                pygame.display.flip()
                pygame.event.get()  # Discard any events that take place while text box is blitting

            self.x_pos += text_rect.width + 8

    # writes the text to the surface we created
    def setTextspace(self, text, space):
        # loops through the list of words writing them to the self.image surface
        words = text.split()
        for word in words:
            # text is the text object which needs to be blitted to the screen at
            text = self.font.render(word, True, (255, 255, 255))
            text_rect = text.get_rect()
            # if the word comes within five pixels of the edge move down a line
            if (self.x_pos + text_rect.width > self.position[0] + self.size[0]-5):
                self.x_pos = self.position[0]+10
                self.y_pos += 33
            g.screen.blit(text, (self.x_pos, self.y_pos))
            if self.wait is True:
                #Delay between words so that it scrolls
                pygame.time.wait(80)
                pygame.display.flip()
                pygame.event.get()  # Discard any events that take place while text box is blitting

            self.x_pos += text_rect.width + space

    def space_centered_text(self, text, space):
        self.width = 0
        # loops through the list of words writing them to the self.image surface
        words = text.split()
        texts = []
        for word in words:
            # text is the text object which needs to be blitted to the screen at
            text = self.font.render(word, True, (255, 255, 255))
            text_rect = text.get_rect()
            texts.append([text,text_rect.width])
        for text in texts:
            self.width += text[1] + space
        self.width -= space
        self.x_pos = (g.xsize - self.width)/2

            # if the word comes within five pixels of the edge move down a line
        for text in texts:
            g.screen.blit(text[0], (self.x_pos, self.y_pos))

            self.x_pos += text[1] + space
