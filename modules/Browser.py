import pygame as pg
from modules.analyzers.LexicalAnalyzer import LexicalAnalyzer
from modules.analyzers.Parser import Parser
from modules.Symbols import Symbols
import re
import random

class Browser(Symbols):
  def __init__(self, debug=False):
    self.pg = pg
    self.pg.init()
    self.font = self.pg.font.Font(None, 36)
    self.pg.display.set_caption("HTML Tag Recognizer")
    self.running = True
    self.debug = debug
    self.clearProps()

  def setScreen(self, dimensions):
    self.screen = self.pg.display.set_mode(dimensions)
    self.screen.fill(self.colors.get('white'))

  def initWindow(self):
    while self.running:
      for event in self.pg.event.get():
        if event.type == self.pg.QUIT:
          self.running = False
          self.pg.quit()

  def generateColorProp(self):
    return random.randrange(0, 255)

  def generateColor(self):
    return (
      self.generateColorProp(), 
      self.generateColorProp(),
      self.generateColorProp()
    )

  def getColor(self, color):
    return color if color else (
      self.generateColor() if self.debug else (0, 0, 0)
    )

  def loadPage(self, filename):
    htmlCode = None
    with open('{}.html'.format(filename), 'r') as file:
      htmlCode = file.read()
    if type(htmlCode)==str:
      lexicalAnalyzer = LexicalAnalyzer()
      parser = Parser(self.font)
      tokens = lexicalAnalyzer.getTokens(htmlCode)
      lexicalAnalyzer.showTokens()
      self.setElement(parser.generateElements(tokens))
      parser.showElements()
      self.render()
      
  def render(self):
    self.setScreen((800, 600))
    self.renderElement()
    self.initWindow()
    self.clearProps()

  def clearProps(self):
    self.setElement(None)

  def setElement(self, element):
    self.element = element

  def elementIsOfType(self, element, type):
    return type in element

  def drawRectangle(self, e):
    if not re.match(r'h\d', e.get('tag')):
      self.pg.draw.rect(self.screen, 
        self.getColor(e.get('color')), 
        (e.get('x'), e.get('y'), e.get('w'), e.get('h'))
      )

  def drawImage(self, e):
    img = self.pg.image.load(e['src'])
    img = self.pg.transform.scale(img, (e['w'], e['h']))
    imgRect = img.get_rect()
    imgRect.center = (e.get('x')+(e.get('w')/2), (e.get('y')+(e.get('h')/2)))
    self.screen.blit(img, imgRect)

  def drawText(self, e):
    textSurface = self.font.render(e.get('text'), True, self.colors.get('black'))
    textRect = textSurface.get_rect()
    textRect.center = (e.get('x')+(e.get('w')/2), (e.get('y')+(e.get('h')/2)))
    self.screen.blit(textSurface, textRect)

  def renderElement(self, element=None):
    scopeElement = element if element else self.element
    if self.elementIsOfType(scopeElement, 'tag') and scopeElement['tag']=='img' and 'src' in scopeElement:
      self.drawImage(scopeElement)
    elif self.elementIsOfType(scopeElement, 'tag'):
      self.drawRectangle(scopeElement)
      children = scopeElement.get('children') if self.elementIsOfType(scopeElement, 'tag') and 'children' in scopeElement else None
      if not children is None and len(children)>0:
        for subElement in children:
          self.renderElement(subElement)
    elif self.elementIsOfType(scopeElement, 'text'):
      self.drawText(scopeElement)
    self.pg.display.update()
