import re
from modules.Symbols import Symbols

""" 
  # ? ta -> tag de abertura
  # ? tu -> tag única
  # ? at -> atributo da tag
  # ? ats -> atributo de estilo
  # ? vas -> valor do atributo de estilo
  # ? va -> valor do atributo
  # ? ct -> conteúdo da tag
  # ? tf -> tag de fechamento
"""

class LexicalAnalyzer(Symbols):
  def __init__(self):
    self.i = 0
    self.tagEnd = None
    self.patternTag = r'<(/?)(\w+)([^>]*)>'
    self.patternAttr = r'(\w+)="([^"]*)"'
    self.patternCSSAttr = r'(\w[^"|\d|\s]+):([^"|;]*);?'

  def getContent(self, htmlCode, tag):
    if self.tagEnd:
      contentStart = self.tagEnd
      contentEnd = tag.start()
      content = htmlCode[contentStart:contentEnd].strip()
      if content:
        self.tokens.append(("ct", content))
      self.tagEnd = None

  def getTag(self, closing, tagName):
    if not closing:
      if tagName in self.tags:
        self.tokens.append(('ta', tagName, self.i))
        self.i += 1
      elif tagName in self.uniqueTags:
        self.tokens.append(('tu', tagName, self.i))
      return False
  
    if tagName in self.tags:
      self.i -= 1
      self.tokens.append(('tf', tagName))
    return True

  def getAttrs(self, attrs, endSymbols, patterns, attrsWithSubAttrs):
    if attrs:
      endSymbol, pattern = endSymbols[0], patterns[0]
      attrWithSubAttrs = attrsWithSubAttrs[0] if len(attrsWithSubAttrs)>0 else None
      for attr in re.finditer(pattern, attrs):        
        attrName, attrValue = attr.groups()
        if attrName in self.attrs or self.cSSAttrs:
          self.tokens.append(("at"+endSymbol, attrName))
          if not attrWithSubAttrs is None and attrWithSubAttrs==attrName:
            self.getAttrs(attrValue, endSymbols[1:], patterns[1:], attrsWithSubAttrs[1:])
          else:
            self.tokens.append(("va"+endSymbol, attrValue.strip()))

  def showTokens(self):
    for t in self.tokens:
      print(t)

  def getTokens(self, htmlCode):
    self.tokens = []
    for tag in re.finditer(self.patternTag, htmlCode.strip()):
      self.getContent(htmlCode, tag)
      closing, tagName, attrs = tag.groups()
      self.getTag(closing, tagName)
      self.getAttrs(attrs, ['', 's'], [self.patternAttr, self.patternCSSAttr], ['style'])
      if not closing:
        self.tagEnd = tag.end()

    return self.tokens
