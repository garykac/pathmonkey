#!/usr/bin/env python
"""
X-agram
Create n-pointed star polygons (pentagram, hexagram, etc)
"""
import inkex
from math import *
from lxml import etree

def addPathCommand(a, cmd):
	for x in cmd:
		a.append(str(x))

class XGramEffect(inkex.Effect):

	def __init__(self):
		inkex.Effect.__init__(self)
		self.arg_parser.add_argument('--tab',
			action = 'store', type = str, dest = 'tab')
		self.arg_parser.add_argument('--points',
			action='store', type=int, dest='points', default=5,
			help='Number of points (or sides)')
		self.arg_parser.add_argument('--skip',
			action='store', type=int, dest='skip', default=2,
			help='Vertex increment when connecting points')
		self.arg_parser.add_argument('--rotate',
			action='store', type=float, dest='rotate', default=0,
			help='Rotation angle (clockwise, in degrees)')
		self.arg_parser.add_argument('--inner-circle',
			action='store', type=inkex.Boolean, dest='inner_circle', default=False,
			help='Connect points via inner circle')
		self.arg_parser.add_argument('--show-inner-circle',
			action='store', type=inkex.Boolean, dest='show_inner_circle', default=True,
			help='Show inner circle')
		self.arg_parser.add_argument('--inner-ratio',
			action='store', type=int, dest='inner_ratio', default=50,
			help='Inner radius percentage (inner radius as a percentage of the outer radius)')

	def effect(self):
		layer = self.svg.get_current_layer();

		if len(self.svg.selected) == 0:
			inkex.errormsg('Please select a circle or ellipse.')
			exit()

		numValid = 0
		for id, obj in self.svg.selected.items():
			cx,cy, rx,ry = 0,0, 0,0
			style = ''
			isValid = False
			if obj.tag == inkex.addNS('circle','svg'):
				isValid = True
				cx = float(obj.get('cx'))
				cy = float(obj.get('cy'))
				rx = float(obj.get('r'))
				ry = rx
			elif obj.tag == inkex.addNS('ellipse', 'svg'):
				isValid = True
				cx = float(obj.get('cx'))
				cy = float(obj.get('cy'))
				rx = float(obj.get('rx'))
				ry = float(obj.get('ry'))
			elif obj.tag == inkex.addNS('path', 'svg'):
				if obj.get(inkex.addNS('type', 'sodipodi')) == 'arc':
					isValid = True
					cx = float(obj.get(inkex.addNS('cx', 'sodipodi')))
					cy = float(obj.get(inkex.addNS('cy', 'sodipodi')))
					rx = float(obj.get(inkex.addNS('rx', 'sodipodi')))
					ry = float(obj.get(inkex.addNS('ry', 'sodipodi')))

			if not isValid:
				continue;

			numValid += 1
			style = obj.get('style')
			transform = obj.get('transform')
			isEllipse = False
			if rx != ry:
				isEllipse = True

			sides = self.options.points
			skip = self.options.skip
			rotate = self.options.rotate
			useInnerCircle = self.options.inner_circle
			showInnerCircle = self.options.show_inner_circle
			innerRatio = float(self.options.inner_ratio) / 100.0

			if useInnerCircle and showInnerCircle:
				if not isEllipse:
					cin = inkex.etree.SubElement(layer, inkex.addNS('circle','svg'))
					cin.set('r', str(rx * innerRatio))
				else:
					cin = inkex.etree.SubElement(layer, inkex.addNS('ellipse','svg'))
					cin.set('rx', str(rx * innerRatio))
					cin.set('ry', str(ry * innerRatio))
				cin.set('cx', str(cx))
				cin.set('cy', str(cy))
				cin.set('style', style)
				if transform:
					cin.set('transform', transform)

			tau = 2*pi
			origin = -(tau / 4) + (rotate * pi / 180)
			out_pts = []
			in_pts = []
			for i in range(sides):
				# Outer points (on outer circle)
				theta = (i * (tau / sides))
				px = cx + rx * cos(origin + theta)
				py = cy + ry * sin(origin + theta)
				out_pts.append([px, py])

				# Inner points (on inner circle)
				theta = ((i + (skip / 2.0)) * (tau / sides))
				px = cx + rx * innerRatio * cos(origin + theta)
				py = cy + ry * innerRatio * sin(origin + theta)
				in_pts.append([px, py])

			pts = []
			pt_done = {}
			for i in range(sides):
				if i in pt_done:
					continue;

				p1 = out_pts[i]
				addPathCommand(pts, ['M', p1[0], p1[1]])

				pt_done[i] = True
				start_index = i
				curr = start_index
				next = (curr + skip) % sides
				while next != start_index:
					p = out_pts[next]
					pt_done[next] = True

					if useInnerCircle:
						addPathCommand(pts, ['L', in_pts[curr][0], in_pts[curr][1]])

					addPathCommand(pts, ['L', p[0], p[1]])

					curr = next
					next = (curr + skip) % sides
				if useInnerCircle:
					addPathCommand(pts, ['L', in_pts[curr][0], in_pts[curr][1]])
				addPathCommand(pts, ['z'])

			# Create star polygon as a single path.
			l1 = etree.SubElement(layer, inkex.addNS('path','svg'))
			l1.set('style', style)
			if transform:
				l1.set('transform', transform)
			l1.set('d', ' '.join(pts))

		if numValid == 0:
			inkex.errormsg('Selection must contain a circle or ellipse.')

if __name__ == '__main__':
	effect = XGramEffect()
	effect.run()
