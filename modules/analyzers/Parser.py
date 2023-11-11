from modules.Symbols import Symbols
import re

class Parser(Symbols):
  def __init__(self, font):
    self.resetProps()
    self.font = font

  def showElements(self, element=None, initSymbol=''):
    element = self.elements if element is None else element
    children = element.pop('children') if 'children' in element else None
    print(initSymbol, element)
    if not children is None:
      for subElement in children:
        self.showElements(subElement, initSymbol+'\t')    
      element['children'] = children

  def convertToPixels(self, value):
    return int(re.sub(r'\s|px', '', value))

  def getTokenValues(self, i):
    token = self.tokens[i]
    symbol = token[0]
    value = token[1]
    return (symbol, value, token[2] if len(token)==3 else None)

  def convertValToEleStructure(self, attrName, attrValue):
    newAttrName, newAttrValue = attrName, attrValue
    if newAttrName in self.cSSAttrs or newAttrName in self.attrs:
      if newAttrName=='width': newAttrName='w'
      elif newAttrName=='height': newAttrName='h'
      elif newAttrName=='flex-direction': newAttrName='orderIn'
      if newAttrName in ['w', 'h']: newAttrValue = self.convertToPixels(newAttrValue)
    return (newAttrName, newAttrValue)

  def setNewCoordsAndDimens(self, x, y, element, children, wTmp, hTmp):
    newX, newY = x, y
    newWTmp, newHTmp = wTmp, hTmp
    newWidth, newHeigth = element.get('w'), element.get('h')

    if not 'display' in element or element.get('orderIn')=='column':
      newY += children.get('h')
      newHTmp += children.get('h')
      if newHTmp>newHeigth: newHeigth = newHTmp
      if children.get('w')>newWidth: newWidth = children.get('w')
    elif element.get('orderIn')=='row':
      newX += children.get('w')
      newWTmp += children.get('w')
      if newWTmp>newWidth: newWidth = newWTmp
      if children.get('h')>newHeigth: newHeigth = children.get('h')
    return (newX, newY, newWidth, newHeigth, newWTmp, newHTmp)

  def createElement(self, i=0, x=0, y=0, parent=None):
    newElement, wTmp, hTmp = None, 0, 0
    while i<len(self.tokens):
      symbol, value, level = self.getTokenValues(i)
      if symbol in ['ta', 'tu'] and not value in ['html', 'head', 'title']:
        if newElement is None:
          newElement = {'x': x, 'y': y, 'tag': value, 'w': 0, 'h': 0}
          if value in self.tags: 
            newElement['children'], newElement['orderIn'] = [], 'column'
        else:
          if newElement.get('tag') in self.uniqueTags:
            i -= 1
            break
          elif newElement.get('tag') in self.tags:
            children, i = self.createElement(i, x, y, newElement)        
            x, y, newElement['w'], newElement['h'], wTmp, hTmp = self.setNewCoordsAndDimens(x, y, newElement, children, wTmp, hTmp)
            newElement['children'].append(children)

      elif symbol=='tf':
        ignoreTag = (value in ['html', 'head', 'title'])
        if ignoreTag: 
          i += 1
          continue
        uniqueTag = (not parent is None and newElement.get('tag') in self.uniqueTags and parent.get('tag')==value)
        tag = (newElement.get('tag') in self.tags and newElement.get('tag')==value)
        if not newElement is None: 
          if uniqueTag:
            i -= 1
          if (uniqueTag or tag): 
            break

      elif symbol in ['at', 'ats']:
        i += 1
        if value=='style': continue
        symbol2, value2, level2 = self.getTokenValues(i)
        if symbol2 in ['va', 'vas']:
          attrName, attrValue = self.convertValToEleStructure(value, value2)
          if (attrName=='orderIn' and 'display' in newElement and newElement['display']=='flex') or not attrName=='orderIn':
            newElement[attrName] = attrValue
            if attrName=='display':
              newElement['orderIn'] = 'row'

      elif symbol=='ct' and not newElement is None:
        if newElement.get('tag') in self.uniqueTags:
          i -= 1
          break
        txtWidth, txtHeight = self.font.size(value)
        children = {'x': x, 'y': y, 'text': value, 'w': txtWidth, 'h': txtHeight}
        x, y, newElement['w'], newElement['h'], wTmp, hTmp = self.setNewCoordsAndDimens(x, y, newElement, children, wTmp, hTmp)
        newElement['children'].append(children)

      i += 1
    return (newElement, i)  

  def resetProps(self):
    self.tokens = []
    self.i = 0
  
  def setTokens(self, tokens):
    self.tokens = tokens

  def generateElements(self, tokens):
    self.setTokens(tokens)
    children, i = self.createElement()
    self.resetProps()
    self.elements = children
    return children