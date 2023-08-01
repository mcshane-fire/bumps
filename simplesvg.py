#!/bin/python3

# Drawing class
# out = svgwrite.Drawing(name, profile="tiny")
# out.tostring() <- returns string
# out.save()
# out.add(out.line(start=(xpos, ypos), end=(xpos+scale, ypos-(up*scale)), stroke=colour, stroke_width=linewidth))
# out.add(out.polyline(points=linepoints, stroke=colours[0], stroke_width=3, fill='none'))
# polyline = out.polyline(points=linepoints, stroke=c, stroke_width=3, fill='none')
# polyline.dasharray(arr, offset=off)
# out.add(polyline)
# out.add(out.polyline(points=linepoints, stroke=colour, stroke_width=linewidth, fill='none'))
# out.add(out.rect(insert=(xoff-space,top), size=((event['days'] * scale)+(space*2), len(d) * scale), stroke='black', fill='none'))
# out.add(out.text(label, insert=(xoff, top+5), font_size=fontsize, stroke_width=0, fill=colour))
# text = out.add(out.text(label, insert=(xoff, top+5), font_size=fontsize, stroke_width=0, fill=colour))
# text.rotate(90, [xoff, top+5])
# rect = out.add(out.rect(insert=(x2off + (r * scale), yoff), size=(scale, top-yoff), fill='lightgray', stroke_width=0))
# rect.fill(opacity=0.15)
# out.add(out.line(start=(xpos, crew['height']), end=(xpos, ynext), stroke = 'gray', stroke_width = 1))

class Image:
    def __init__(self, position, suffix, data, width, height, name):
        self.defs = {'position':position,
                     'width':width,
                     'height':height,
                     'suffix':suffix,
                     'data':data,
                     'name':name}

    def output(self):
        args = 'x="%g"' % self.defs['position'][0]
        args += ' y="%g"' % self.defs['position'][1]

        if self.defs['width'] != None:
            args += ' width="%g"' % self.defs['width']
        if self.defs['height'] != None:
            args += ' height="%g"' % self.defs['height']
        if self.defs['name'] != None:
            args += ' id="%s"' % self.defs['name']

        args += ' xlink:href="data:image/%s;base64,%s"' % (self.defs['suffix'], self.defs['data'])

        return '<image %s />\n' % args


class Polyline:
    def __init__(self, points, stroke, stroke_width, fill, name):
        self.defs = {'points':points,
                     'stroke':stroke,
                     'stroke_width':stroke_width,
                     'fill':fill,
                     'name' : name}

    def dasharray(self, array, offset):
        self.defs['array'] = array
        self.defs['offset'] = offset

    def fill(self, opacity):
        self.defs['opacity'] = opacity

    def output(self):
        args = 'fill="%s"' % self.defs['fill']
        args += ' stroke="%s"' % self.defs['stroke']
        args += ' stroke-width="%g"' % self.defs['stroke_width']
        
        ex = ' points="'
        for p in self.defs['points']:
            args += ex + ("%g,%g" % (p[0], p[1]))
            ex = " "
        args += '"'
            
        if 'array' in self.defs:
            al = ""
            ex = ""
            for p in self.defs['array']:
                al = al + ex + ("%d" % p)
                ex = " "
            

            args += ' stroke-dasharray="%s"' % al
            args += ' stroke-dashoffset="%d"' % self.defs['offset']

        if 'opacity' in self.defs:
            args += ' stroke-opacity="%g"' % self.defs['opacity']
        if self.defs['name'] != None:
            args += ' id="%s"' % self.defs['name']
            
        return '<polyline %s />\n' % args


class Path:
    def __init__(self, draw, fill, transform, name):
        self.defs = {'draw' : draw,
                     'fill' : fill,
                     'transform' : transform,
                     'id' : name}

    def output(self):
        args = 'd="%s" fill="%s"' % (self.defs['draw'], self.defs['fill'])
        if self.defs['transform'] is not None:
            args += ' transform="%s"' % self.defs['transform']
        if self.defs['id'] is not None:
            args += ' id="%s"' % self.defs['id']
        
        
        return '<path %s />\n' % args
    
class Line:
    def __init__(self, start, end, stroke, stroke_width, name):
        self.defs = {'start':start,
                     'end':end,
                     'stroke':stroke,
                     'stroke_width':stroke_width,
                     'id':name}

    def fill(self, opacity):
        self.defs['opacity'] = opacity

    def output(self):
        args = 'stroke="%s"' % self.defs['stroke']
        if self.defs['id'] != None:
            args += ' id="%s"' % self.defs['id']
        if 'opacity' in self.defs:
            args += ' stroke-opacity="%g"' % self.defs['opacity']
        args += ' stroke-width="%g"' % self.defs['stroke_width']
        args += ' x1="%g"' % self.defs['start'][0]
        args += ' y1="%g"' % self.defs['start'][1]
        args += ' x2="%g"' % self.defs['end'][0]
        args += ' y2="%g"' % self.defs['end'][1]

        return '<line %s />\n' % args

class Text:
    def __init__(self, label, insert, font_size, stroke_width, fill, text_anchor, mask, decoration, vertical_align):
        self.defs = {'label':label,
                     'insert':insert,
                     'font_size':font_size,
                     'stroke_width':stroke_width,
                     'fill':fill,
                     'text_anchor':text_anchor,
                     'mask':mask,
                     'decoration':decoration,
                     'vertical_align':vertical_align}

    def rotate(self, degrees, center = None):
        self.defs['degrees'] = degrees
        if center is None:
            center = self.defs['insert']
        self.defs['center'] = center

    def output(self):
        args = 'fill="%s"' % self.defs['fill']
        args += ' font-size="%g"' % self.defs['font_size']
        args += ' stroke-width="%g"' % self.defs['stroke_width']
        if self.defs['text_anchor'] is not None:
            args += ' text-anchor="%s"' % self.defs['text_anchor']
        
        if 'degrees' in self.defs:
            args += ' transform="translate(%g,%g)rotate(%g)"' % (self.defs['center'][0],
                                                                 self.defs['center'][1],
                                                                 self.defs['degrees'])

        if self.defs['mask'] is not None:
            args += ' mask="url(#%s)"' % self.defs['mask']
        if self.defs['decoration'] is not None:
            args += ' text-decoration="%s"' % self.defs['decoration']
        if self.defs['vertical_align'] is not None:
            args += ' dominant-baseline="%s"' % self.defs['vertical_align']

        if self.defs['insert'] is not None:
            args += ' x="%g"' % self.defs['insert'][0]
            args += ' y="%g"' % self.defs['insert'][1]
            
        return '<text %s>%s</text>\n' % (args, self.defs['label'])


class Rect:
    def __init__(self, insert, size, fill, stroke, stroke_width, stroke_opacity, name, mask):
        self.defs = {'insert':insert,
                     'size':size,
                     'fill':fill,
                     'stroke':stroke,
                     'stroke_width':stroke_width,
                     'stroke_opacity':stroke_opacity,
                     'mask':mask,
                     'id':name}
        
    def fill(self, opacity):
        self.defs['opacity'] = opacity

    def rx(self, value):
        self.defs['rx'] = value
        
    def output(self):
        args = 'fill="%s"' % self.defs['fill']
        args += ' width="%g"' % self.defs['size'][0]
        args += ' height="%g"' % self.defs['size'][1]
        args += ' stroke-width="%g"' % self.defs['stroke_width']
        args += ' x="%g"' % self.defs['insert'][0]
        args += ' y="%g"' % self.defs['insert'][1]
        
        if 'opacity' in self.defs:
            args += ' fill-opacity="%g"' % self.defs['opacity']
        if self.defs['stroke'] != None:
            args += ' stroke="%s"' % self.defs['stroke']
        if self.defs['stroke_opacity'] != None:
            args += ' stroke_opacity="%g"' % self.defs['stroke_opacity']
        if self.defs['id'] != None:
            args += ' id="%s"' % self.defs['id']
        if 'rx' in self.defs:
            args += ' rx="%s"' % self.defs['rx']
        if self.defs['mask'] != None:
            args += ' mask="url(#%s)"' % self.defs['mask']
            
        return '<rect %s />\n' % args

    
class Circle:
    def __init__(self, center, r, fill, stroke, stroke_width, name):
        self.defs = {'center':center,
                     'r':r,
                     'fill':fill,
                     'stroke':stroke,
                     'stroke_width':stroke_width,
                     'id':name}

    def output(self):
        args = 'cx="%g"' % self.defs['center'][0]
        args += ' cy="%g"' % self.defs['center'][1]
        args += ' r="%g"' % self.defs['r']
        args += ' fill="%s"' % self.defs['fill']

        if self.defs['stroke'] != None:
            args += ' stroke="%s"' % self.defs['stroke']
        if self.defs['stroke_width'] != None:
            args += ' stroke-width="%g"' % self.defs['stroke_width']
        if self.defs['id'] != None:
            args += ' id="%s"' % self.defs['id']

        return '<circle %s />\n' % args

class Group:
    def __init__(self, start, link, title, name):
        self.start = start
        self.link = link
        self.title = title
        self.name = name
        self.translate = None
        if self.title is not None:
            self.title = self.title.split('&')[0].replace("\"", "'")

    def add_translate(self, coord):
        self.translate = coord
        
    def output(self):
        args = ""
        if self.translate is not None:
            args += ' transform="translate(%g,%g)"' % (self.translate[0], self.translate[1])
        if self.name is not None:
            args += ' id="%s"' % self.name
        if self.start:
            ret = ""
            if self.link is not None:
                ret += '<a xlink:href="%s"' % self.link
                if self.title is not None:
                    ret += ' xlink:title="%s"' % self.title
                ret += '>'

            ret += "<g %s>\n" % args
        else:
            ret = "</g>"
            if self.link is not None:
                ret += '</a>'
            ret += "\n"

        return ret

class Drawing:
    def __init__(self, filename, profile):
        self.filename = filename
        self.profile = profile
        self.objects = []
        self.patterns = {}
        self.masks = []
        self.width = "100%"
        self.height = "100%"

    def __init__(self):
        self.objects = []
        self.width = "100%"
        self.height = "100%"
        self.patterns = {}
        self.masks = []

    def check(self):
        print ("Filename: %s, profile: %s\n" % (self.filename, self.profile))

    def setsize(self, width, height):
        self.width = width
        self.height = height

    def setpattern(self, name, definition):
        if not name in self.patterns:
            self.patterns[name] = definition

    def line(self, start=None, end=None, stroke=None, stroke_width=None, name=None):
        return Line(start, end, stroke, stroke_width, name)

    def polyline(self, points, stroke, stroke_width, fill, name=None):
        return Polyline(points, stroke, stroke_width, fill, name)
    
    def path(self, draw, fill, transform=None, name=None):
        return Path(draw, fill, transform, name)
    
    def text(self, label, insert, font_size, stroke_width, fill, text_anchor=None, mask=None, decoration=None, vertical_align=None):
        return Text(label, insert, font_size, stroke_width, fill, text_anchor, mask, decoration, vertical_align)

    def rect(self, insert=None, size=None, fill=None, stroke_width=1, stroke=None, stroke_opacity=None, name=None, mask=None):
        return Rect(insert, size, fill, stroke, stroke_width, stroke_opacity, name, mask)

    def circle(self, center, r, fill, stroke=None, stroke_width=None, name=None):
        return Circle(center, r, fill, stroke, stroke_width, name)

    def image(self, position, suffix, data, width=None, height=None, name=None):
        return Image(position, suffix, data, width, height, name)

    def group(self, start, link=None, title=None, name=None):
        return Group(start, link, title, name)
    
    def add(self, object):
        self.objects.append(object)
        return self.objects[-1]

    def addmask(self, object):
        self.masks.append(object)
        return "mask%d" % len(self.masks)
    
    def tostring(self):
        ret = '<?xml version="1.0" encoding="utf-8" ?>\n'
        ret += '<svg baseProfile="tiny" height="%s" version="1.2" width="%s" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">\n' % (self.height, self.width)

        if len(self.patterns) > 0 or len(self.masks) > 0:
            ret += '<defs>\n'
            for name in self.patterns:
                ret += self.patterns[name]+'\n'
            num = 1
            for mask in self.masks:
                ret += '<mask id="mask%d">\n' % num
                for m in mask:
                    ret += m.output()
                ret += '</mask>\n'
                num += 1
            ret += '</defs>\n'

        for i in self.objects:
            ret += i.output()

        ret += '</svg>\n'
        return ret;


