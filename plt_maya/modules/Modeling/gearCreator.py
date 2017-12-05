# coding=utf-8

"""



"""

import maya.cmds as cmds

class gear(object):
	def __init__(self):
		self.transform=None
		self.extrude=None
		self.extrude=None

	def createGear(self, teeth=10, length=0.3):
		spans = teeth*2
		self.transform, self.constructor = cmds.polyPipe(sa=spans)
		sideFaces = range(spans*2, spans*3, 2)
		cmds.select(clear=True)
		for face in sideFaces:
			cmds.select('%s.f[%s]' % (self.transform, face), add=True)
		self.extrude = cmds.polyExtrudeFacet(ltz=length)[0]

	def changeTeeth(self, constructor, extrude, teeth=10, length=0.3):
		spans = teeth*2
		cmds.polyPipe(self.constructor, edit=True, sa=spans)
		sideFaces = range(spans*2, spans*3, 2)
		faceNames = []
		for face in sideFaces:
			faceName = 'f[%s]' % (face)
			faceNames.append(faceName)
		cmds.setAttr('%s.inputComponents' % (extrude), len(faceNames), *faceNames, type="componentList")
		cmds.polyExtrudeFacet(self.extrude, edit=True, ltz=length)
