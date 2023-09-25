import simplesvg
from arial_16_metrics import font_metrics

def estimate_text_length(text, scale):
    tot = 0.0
    for c in text:
        if c in font_metrics:
            tot += font_metrics[c]
    return tot * scale

def estimate_max_length(crews, tag, scale):
    mlen = 0.0
    num = 1
    for c in crews:
        clen = estimate_text_length("%d %s" % (num, c[tag]), scale)
        if clen > mlen:
            mlen = clen
        num += 1
    return mlen

def draw_divisions(svg_config, out, xoff, yoff, event, space, draw_colours = False):
    top = yoff
    for crew_num in range(len(event['crews'])):
        ypos = top + (svg_config['scale']/2)
        xpos = xoff
        c = crew_num
        crew = event['crews'][crew_num]
        colour = "gray"
        linewidth = 1
        if draw_colours == False:
            if crew['highlight']: 
                colour = "blue"
                linewidth = 3
            elif crew['blades']:
                colour = "red"
                linewidth = 2

        lines = []
        skipped = []
        points = []
        last = [xpos, ypos]
            
        for day in range(0, event['days']):
            t = event['move'][day]
            up = t[c]

            tmp = c
            raceday = True
            div_raced = True
            for d in range(len(event['div_size'][day])):
                if tmp < event['div_size'][day][d]:
                    if event['completed'][day][d] == False:
                        div_raced = False
                    # cope with sandwich crews bumping up when their own division didn't race
                    if div_raced == False and up is not None and up > 0:
                        div_raced = True
                    break
                tmp -= event['div_size'][day][d]

            if event['skip'][day][c] == True:
                raceday = False

            if up is None:
                if div_raced:
                    out.add(out.circle(center=last, r=3, fill=colour))
                break

            xpos = xpos + svg_config['scale']
            ypos = ypos - (up*svg_config['scale'])

            if div_raced and raceday:
                if len(points) == 0:
                    points.append(last)
                points.append([xpos, ypos])
            else:
                if len(points) > 0:
                    lines.append(points)
                    points = []
                skipped.append([last, [xpos, ypos]])
                    
            last = [xpos, ypos]
                
            c = c - up;

        if len(points) > 0:
            lines.append(points)

        if draw_colours and 'college' in crew and 'colours' in crew['college']:
            colours = crew['college']['colours']
            if len(colours) == 1:
                for l in lines:
                    out.add(out.polyline(points=l, stroke=colours[0], stroke_width=3, fill='none'))
            else:
                arr = [svg_config['dash'], (svg_config['dash']/2) * (len(colours)-1)]
                off = 0
                nextoff = arr[1]
                for l in lines:
                    for c in colours:
                        polyline = out.polyline(points=l, stroke=c, stroke_width=3, fill='none')
                        polyline.dasharray(arr, offset=off)
                        out.add(polyline)
                        off = nextoff
                        nextoff = nextoff - (svg_config['dash']/2)
                        arr = [svg_config['dash']/2, (svg_config['dash']/2) * len(colours)]

        else:
            for l in lines:
                out.add(out.polyline(points=l, stroke=colour, stroke_width=linewidth, fill='none'))

        for line in skipped:
            out.add(out.polyline(points=line, stroke="lightgray", stroke_width=1, fill='none'))
                
                    
        top = top + svg_config['scale']


    #top = yoff
    # box around all divisions
    out.add(out.rect(insert=(xoff-space,yoff), size=((event['days'] * svg_config['scale'])+(space*2), len(event['crews']) * svg_config['scale']), stroke='black', fill='none'))

    # draw in lines between divisions
    left = xoff-space
    right = left + space + svg_config['scale']
    prev_div_height = None
    for day in range(event['days']):
        div_height = []
        top = yoff
        if day == event['days']-1:
            right += space
        for div in range(len(event['div_size'][day])-1):
            top += event['div_size'][day][div] * svg_config['scale']
            div_height.append(top)
            out.add(out.line(start=(left, top), end=(right, top), stroke='black', stroke_width=1))

            if prev_div_height is not None and prev_div_height[div] != div_height[div]:
                out.add(out.line(start=(left, prev_div_height[div]), end=(left, div_height[div]), stroke='black', stroke_width=1))

        prev_div_height = div_height
        left = right
        right += svg_config['scale']

    return yoff + (len(event['crews']) * svg_config['scale'])

def draw_extra_text(svg_config, out, xoff, yoff, event, extra):
    top = yoff
    for div_num in range(len(event['div_size'][0])):
        label = None
        fontscale = 0.8
        fontsize = svg_config['scale']*fontscale
        colour = 'darkred'
        height = event['div_size'][0][div_num] * svg_config['scale']

        label = "%s %d - %s, Division %d" % (event['short'], event['year'], event['gender'], div_num+1)
        if estimate_text_length(label, fontscale) > height - svg_config['scale']:
            label = "%s %d - %s, Div %d" % (event['short'], event['year'], event['gender'], div_num+1)
            if estimate_text_length(label, fontscale) > height - svg_config['scale']:
                label = "%s %s,%s%s" % (event['short'], event['year'], event['gender'][0], div_num+1)
                if estimate_text_length(label, fontscale) > height - svg_config['scale']:
                    label = "%s%s, %s%s" % (event['short'][0], event['year'], event['gender'][0], div_num+1)
                    if estimate_text_length(label, fontscale) > height - svg_config['scale']:
                        label = "Division %d" % (div_num+1)
                        if estimate_text_length(label, fontscale) > height - svg_config['scale']:
                            label = "Div %d" % (div_num+1)
                            if estimate_text_length(label, fontscale) > height - svg_config['scale']:
                                label = "%d" % (div_num+1)
                                if estimate_text_length(label, fontscale) > height - svg_config['scale']:
                                    label = None

        if label != None:
            text = out.add(out.text(label, insert=None, font_size=fontsize, font_family='Arial', stroke_width=0, fill=colour))
            text.rotate(90, [xoff - fontsize - 2, top+5])

        top = top + height


def draw_numbers(svg_config, out, xoff, yoff, event, align, reset = False):
    top = yoff
    number = 1
    div_num = 0
    fontsize = svg_config['scale'] * 0.8
    
    for crew in event['crews']:
        top = top + svg_config['scale']
        out.add(out.text(str(number), insert=(xoff, top-3), font_size=fontsize, stroke_width=0, fill='gray', font_family='Arial', text_anchor=align))
        number = number + 1
        if reset and number-1 == event['div_size'][0][div_num]:
            number = 1
            div_num += 1

def draw_crews(svg_config, out, xoff, yoff, event, gain, align):
    top = yoff
    fontsize = svg_config['scale'] * 0.8

    for crew in event['crews']:
        top = top + svg_config['scale']
        offset = 0        
        if gain == 1:
            if crew['gain'] is None:
                continue
            offset = svg_config['scale'] * crew['gain']
        colour = 'black'
        if crew['highlight']:
            colour = 'blue'
        elif crew['blades']:
            colour = 'red'
        out.add(out.text(crew['start'], insert=(xoff,top-3-offset), font_size=fontsize, font_family='Arial', stroke_width=0, fill=colour, text_anchor=align))

def draw_stripes(svg_config, out, xoff, yoff, width, x2off, event, event2 = None, extra = 0):
    top = yoff
    alt = 0

    num = 0
    if event2 != None:
        num = len(event2['crews'])

    cn = 0
    for crew in event['crews']:
        swidth = width
        if cn < num:
            swidth = swidth + extra
        if alt == 1:
            rect = out.add(out.rect(insert=(xoff,top), size=(swidth, svg_config['scale']), fill='lightgray', stroke_opacity=0, stroke_width=0))
            rect.fill(opacity=0.35)
        alt = 1 - alt
        top = top + svg_config['scale']
        cn = cn + 1

    if x2off != None:
        alt = 1
        for r in range(1, event['days']):
            if False:
                if alt == 1:
                    rect = out.add(out.rect(insert=(x2off + (r * svg_config['scale']), yoff), size=(svg_config['scale'], top-yoff), fill='lightgray', stroke_width=0))
                    rect.fill(opacity=0.2)
                alt = 1 - alt
            else:
                out.add(out.line(start=(x2off + (r * svg_config['scale']), yoff), end=(x2off + (r * svg_config['scale']), top), stroke_width=0.2, stroke='lightgray'))

def draw_join(svg_config, out, xoff, yoff, event, event2):
    added = []
    yoff = yoff + (svg_config['scale']/2)
    fontsize = svg_config['scale'] * 0.6
    ynext = yoff + (svg_config['scale'] * len(event['crews'])) - (svg_config['scale']/2) + 4
    ysep = svg_config['scale'] * 0.75
    verticals = 0

    for crew_num2 in range(len(event2['crews'])):
        found = False
        for crew_num in range(len(event['crews'])):
            if event2['crews'][crew_num2]['start'] == event['crews'][crew_num]['end']:
                found = True
                break

        if found:
            colour = 'lightgray'
            if 'highlight' in event2['crews'][crew_num2] and event2['crews'][crew_num2]['highlight']:
                colour = 'blue'
            out.add(out.line(start=(xoff, yoff + (svg_config['scale']*crew_num)), end=(xoff + svg_config['sep'], yoff + (svg_config['scale']*crew_num2)), stroke = colour, stroke_width = 1))
        else:
            height = yoff + (svg_config['scale'] * crew_num2)
            adjacent = False
            if ynext < height:
                adjacent = True
                ynext = height-(fontsize/2)
            else:
                verticals += 1

            added.append({'height' : height, 'adjacent' : adjacent, 'label' : ynext, 'crew' : event2['crews'][crew_num2]})

            ynext += ysep

    xsep = (svg_config['sep'] - 4) / (verticals+1)
    xpos = xoff + xsep
    for crew in added:
        colour = 'black'
        linecolour = 'gray'
        if 'highlight' in crew['crew'] and crew['crew']['highlight']:
            colour = 'blue'
            linecolour = 'blue'

        out.add(out.text(crew['crew']['start'], insert=(xpos, crew['label']+fontsize-1), font_size=fontsize, font_family='Arial', stroke_width=0, fill=colour, text_anchor='end'))

        if crew['adjacent'] == False:
            out.add(out.line(start=(xpos, crew['height']), end=(xpos, crew['label']), stroke = linecolour, stroke_width = 1))
            out.add(out.line(start=(xpos, crew['height']), end=(xoff + svg_config['sep'], crew['height']), stroke = linecolour, stroke_width = 1))
            xpos = xpos + xsep

    return ynext
    

def draw_chart(out, event, svg_config, xoffset):
    # leave space for division titles down the left hand side
    left = xoffset + svg_config['scale'] * 2

    svg_config['right'] = estimate_max_length(event['crews'], 'start', 0.8) + svg_config['scale']

    draw_stripes(svg_config, out, left, 0, (svg_config['right']*2) + (svg_config['scale'] * event['days']), left+svg_config['right'], event)
    draw_numbers(svg_config, out, left+3, 0, event, 'start', True)
    draw_numbers(svg_config, out, left + (2*svg_config['right']) + (svg_config['scale'] * event['days']) -3, 0, event, 'end', False)
    #draw_extra_text(svg_config, out, left+20, 0, event, 'number')
    #draw_extra_text(svg_config, out, left + (2*svg_config['right']) + (svg_config['scale'] * event['days']) -40, 0, event, 'name') 
    draw_extra_text(svg_config, out, left, 0, event, 'both')

    draw_crews(svg_config, out, left + svg_config['right']-3, 0, event, 0, 'end')
    draw_crews(svg_config, out, left + svg_config['right'] + (svg_config['scale'] * event['days']) + 3, 0, event, 1, 'start')

    h = draw_divisions(svg_config, out, left + svg_config['right'], 0, event, svg_config['right'], draw_colours = svg_config['colours'])

    return (left + (svg_config['right']*2) + (svg_config['scale'] * event['days'])+1, h+1)

def write_svg(output, event, svg_config):
    out = simplesvg.Drawing()

    size = draw_chart(out, event, svg_config, 0)
    out.setsize(size[0], size[1])

    if output is None:
        print(out.tostring())
    else:
        fp = open(output, 'w')
        fp.write(out.tostring())
        fp.close()

def write_pair(output, sets, svg_config):
    out = simplesvg.Drawing()

    sizeL = draw_chart(out, sets[0], svg_config, 0)
    sizeR = draw_chart(out, sets[1], svg_config, sizeL[0])
    out.setsize(sizeR[0], sizeL[1] if sizeL[1] > sizeR[1] else sizeR[1])

    if output is None:
        print(out.tostring())
    else:
        fp = open(output, 'w')
        fp.write(out.tostring())
        fp.close()

def write_multi_svg(output, sets, svg_config):
    out = simplesvg.Drawing()
    
    width = 0
    height = 0
    top = svg_config['scale'] * 1.25
    fontsize = svg_config['scale'] * 0.8

    m1 = estimate_max_length(sets[0]['crews'], 'start', 0.8)
    m2 = estimate_max_length(sets[-1]['crews'], 'end', 0.8)
    if m2 > m1:
        m1 = m2

    svg_config['right'] = m1 + svg_config['scale']

    xpos = svg_config['right']
    eleft = svg_config['right']
    for event_num in range(0, len(sets)):
        event = sets[event_num]
        event2 = event
        extra = svg_config['sep']
        if event_num < len(sets)-1:
            event2 = sets[event_num+1]
        else:
            extra = svg_config['right']

        out.add(out.text(str(event['year']), insert=(xpos+(svg_config['scale'] * event['days'])/2, top-3), font_size=fontsize, font_family='Arial', stroke_width=0, fill='black', text_anchor='middle'))
        draw_stripes(svg_config, out, xpos-eleft, top, eleft + (svg_config['scale'] * event['days']), xpos, event, event2, extra)
        eleft = 0
        xpos = xpos + (svg_config['scale'] * event['days']) + svg_config['sep']

        if event_num < len(sets)-1:
            h = draw_join(svg_config, out, xpos-svg_config['sep'], top, event, event2)
            if h > height:
                height = h

    width = xpos - svg_config['sep'] + svg_config['right']
    draw_numbers(svg_config, out, 3, top, sets[0], 'start', False)
    draw_numbers(svg_config, out, xpos - svg_config['sep'] + svg_config['right'] - 3, top, sets[-1], 'end', False)

    draw_crews(svg_config, out, svg_config['right']-3, top, sets[0], 0, 'end')
    draw_crews(svg_config, out, xpos - svg_config['sep'] + 3, top, sets[-1], 1, 'start')

    xpos = svg_config['right']
    for event in sets:
        h = draw_divisions(svg_config, out, xpos, top, event, 0, draw_colours = svg_config['colours'])
        if h > height:
            height = h
        xpos = xpos + (svg_config['scale'] * event['days']) + svg_config['sep']

    out.setsize(width+1, height+1)

    if output is None:
        print(out.tostring())
    else:
        fp = open(output, 'w')
        fp.write(out.tostring())
        fp.close()
