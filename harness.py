#!/bin/python3

# todo:
#
# check that crews from the same college appear in order
# collect results/crews for each college for summary statistics
#   most/least bumps in a division all week
#   which day overbumps occur, etc
# add cra club names
# figure out how to tell how long a piece of text is
# ability to cancel a division, so we don't see the lines (2001 & 2002 lents men)


import sys, re
import simplesvg, abbreviations


def add_crew(crews, str, abbrev):
    #print str
    crew = {'gain' : 0, 'blades' : False, 'highlight' : False}

    str = str.strip()
    short = str.strip("0123456789")
    if short in abbrev:
        num = str.strip("abcdefghijklmnopqrtsuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        if len(num) > 0:
            str = "%s %s" % (abbrev[short]['name'], abbreviations.roman[int(num)-1])
        else:
            str = abbrev[short]['name']
        crew['college'] = abbrev[short]

    crew['start'] = str
    crew['end'] = str
    crews.append(crew)
  

def read_file(state, name, highlight = None):
    abbrev = {}
    
    if name != None:
        input = open(name, "r")
    else:
        input = sys.stdin
    ret = {}
    ret['title'] = "Set name"
    ret['days'] = 4
    ret['crews'] = []
    ret['div_size'] = None
    ret['results'] = []

    results = False
    for line in input:
        line = line.strip(" \t\r\n")
        if line == "":
            continue
        p = line.split(",")
        if p[0] == "Set":
            ret['set'] = p[1]
            if ret['set'] in state['abbrev_map']:
                abbrev = state['abbrev_map'][ret['set']]
            
        elif p[0] == "Short":
            ret['short'] = p[1]
        elif p[0] == "Gender":
            ret['gender'] = p[1]
        elif p[0] == "Year":
            ret['year'] = int(p[1])
        elif p[0] == "Days":
            ret['days'] = int(p[1])
        elif p[0] == "Division":
            if ret['div_size'] is None:
                ret['div_size'] = []
                for d in range(ret['days']):
                    ret['div_size'].append([])
            for d in ret['div_size']:
                d.append(len(p)-1)
            if len(p) > 1:
                for i in p[1:]:
                    add_crew(ret['crews'], i, abbrev)
        elif p[0] == "Results":
            results = True
            p.pop(0)

        if results:
            for i in p:
                i = i.strip()
                if not i.startswith("#"):
                    ret['results'].append(i)

    if name != None:
        input.close()

    if highlight != None:
        for crew in ret['crews']:
            if crew['start'].startswith(highlight):
                crew['highlight'] = True
                    
    return ret

#def create_blank_move(event):
#    event['move'] = []
#    event['completed'] = []
#    for d in range(0, event['days']):
#        today = []
#        comp = []
#        for n in event['divisions']:
#            div = []
#            for c in n:
#                div.append(0)
#            today.append(div)
#            comp.append(False)
#        event['move'].append(today)
#        event['completed'].append(comp)

def find_sandwich_boat(move, position):
    c = position
    while c < len(move) and c - move[c] != position:
        c += 1

    if c == len(move):
        return None
    return c
    
def process_bump(move, crew_num, up, div_head):
    if crew_num - up < div_head:
        print("Bumping up above the top of the division: div_head %d, crew %d, up %d" % (div_head, crew_num, up))
        return False
    if move[crew_num - up] != 0:
        print("Bumping a crew that has already got a result")
        return False
    move[crew_num - up] = -up

    # find the boat that is currently pointing to this spot
    # it might be a crew that has bumped already into the sandwich boat slot
    c = find_sandwich_boat(move, crew_num)
    if c is None:
        return False
    
    move[c] += up
    return True

def process_results(event):
    debug = False

    event['move'] = []
    event['completed'] = []
    event['skip'] = []
    for d in range(event['days']):
        event['move'].append([0] * len(event['crews']))
        event['skip'].append([False] * len(event['crews']))
        event['completed'].append([False] * len(event['div_size'][0]))
    
    all = ""
    for r in event['results']:
        all = all + r

    pat = re.compile('r|t|u|o[0-9]+|e-?[0-9]+|v-?[0-9]+|w[0-9]+|x|d<[^>]*>')
    m = pat.findall(all)
    day_num = 0                                                   # 0 is the first day
    div_num = len(event['div_size'][day_num])-1                   # 0 is the first division
    crew_num = len(event['crews'])-1                              # 0 is the headship crew
    div_head = crew_num - event['div_size'][day_num][div_num] + 1 # index of the head crew in the current division
    crews_withdrawn = 0
    
    for c in m:
        move = event['move'][day_num]
        
        if debug:
            print("\nNew command:%s (day:%d div:%d crew:%d div_head:%d)" % (c, day_num, div_num, crew_num, div_head))

            
        # only allow division size changes between full days of racing, and not before the first day
        if c[0] == 'd' and crew_num == -1 and day_num < event['days']-1:
            # division size change
            sizes = c.replace("<"," ").replace(">"," ").replace("."," ").split()[1:]
            sizes = [ int(x) for x in sizes ]

            if debug:
                print("Div size change: %s" % sizes)
            if len(sizes) == len(event['div_size'][0]):
                num = 0
                for s in sizes:
                    num += s
                if num == len(event['crews']) - crews_withdrawn:
                    for day in range(day_num+1, event['days'], 1):
                        event['div_size'][day] = sizes


        # if we've already got a result for this crew, then we can skip over it
        while crew_num >= div_head and move[crew_num] != 0:
            if debug:
                print("Skipping crew:%d, got %s" % (crew_num, move[crew_num]))
            crew_num = crew_num - 1

        if crew_num < div_head:
            # move to the next division
            if div_num == 0:
                # move to the next day
                day_num += 1
                if day_num == event['days']:
                    print("Run out of days of racing with more results still to go")
                    return

                if debug:
                    print("\nMoving to day %d" % day_num)
                move = event['move'][day_num]
                div_num = len(event['div_size'][day_num])-1
                crew_num = len(event['crews'])-1-crews_withdrawn
                div_head = crew_num - event['div_size'][day_num][div_num] + 1
            else:
                div_num -= 1
                crew_num += 1
                div_head -= event['div_size'][day_num][div_num]

            if debug:
                print("\nMoving to division %d" % (div_num))

        if debug:
            print("Processing command:%s (day:%d div:%d crew:%d div_head:%d: pos:%d)" % (c, day_num, div_num, crew_num, div_head, crew_num - div_head + 1))

        if c == 'r':
            # row over, move to the next crew
            crew_num = crew_num - 1
            if debug:
                print("Rowover, moving to crew %d" % crew_num)
        elif c == 'u':
            # up 1
            if process_bump(move, crew_num, 1, div_head) == False:
                return
            crew_num = crew_num - 2
            if debug:
                print("Bumped up, moving to crew %d" % crew_num)
        elif c.startswith("o"):
            up = int(c[1:])
            if process_bump(move, crew_num, up, div_head) == False:
                return
            crew_num = crew_num - 1
            if debug:
                print("Overbumped %d, moving to crew %d" % (up, crew_num))
        elif c.startswith("e") or c.startswith("v"):
            up = int(c[1:])

            # safe to call even if this isn't a sandwich crew position
            p = find_sandwich_boat(move, crew_num)
            if p is None:
                return

            move[p] += up
            crew_num = crew_num - 1
            if debug:
                print("Exact move %d to crew %d, was %d now %d, moving to crew %d" % (up, p, move[p]-up, move[p], crew_num))
            if c.startswith("v"):
                if debug:
                    print("Virtual result, crew %d didn't race" % (p))
                event['skip'][day_num][p] = True
                
        elif c.startswith("w"):
            size = int(c[1:])
            if crew_num - size < div_head:
                print("Washing machine size %d get above head of division %d" % (size, div_head))
                return

            # first crew going up might be a sandwich crew
            p = find_sandwich_boat(move, crew_num)
            if p is None:
                return

            move[p] +=1
            if debug:
                print("Washing machine, crew %d up one" % p)

            for j in range(crew_num-1, crew_num - size, -1):
                if debug:
                    print("Washing machine crew %d up one" % j)
                move[j] = 1
            if debug:
                print("Washing machine crew %d down %d.  Moving to crew %d" % (crew_num-size, size, crew_num-size-1))
            move[crew_num - size] = -size
            crew_num = crew_num - (size+1)

        elif c == 'x':
            if debug:
                print("Crew %d withdrawn, moving to crew %d" % (crew_num, crew_num-1))
            move[crew_num] = None
            crews_withdrawn += 1
            crew_num -= 1
            event['div_size'][day_num][div_num] -= 1
            for day in range(day_num+1, event['days'], 1):
                event['div_size'][day][div_num] = event['div_size'][day_num][div_num]
            
        elif c == 't':
            if debug:
                print("Skipping division, setting crew from %d to div_head-1 %d" % (crew_num, div_head-1))
            crew_num = div_head-1
            continue

        # if we've seen at least one result, mark this division as completed
        event['completed'][day_num][div_num] = True

    # work out finishing names and blades, etc
    for crew_num in range(len(event['crews'])):
        nc = crew_num;
        gain = 0
        blades = True
        for m in event['move']:
            if m[nc] == None:
                event['crews'][crew_num]['gain'] = None
                break
            
            gain = gain + m[nc]
            if m[nc] <= 0:
                blades = False
            nc = nc - m[nc]

            if nc == 0 and event['completed'][-1][0] == True:
                blades = True

            event['crews'][crew_num]['gain'] = gain
            event['crews'][crew_num]['blades'] = blades
            event['crews'][nc]['end'] = event['crews'][crew_num]['start']
            

def draw_divisions(out, xoff, yoff, event, space, draw_colours = False):
    top = yoff
    for crew_num in range(len(event['crews'])):
        ypos = top + (state['scale']/2)
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

            if up is None:
                out.add(out.circle(center=last, r=3, fill=colour))
                break
            
            tmp = c
            raceday = True
            for d in range(len(event['div_size'][day])):
                if tmp < event['div_size'][day][d]:
                    if event['completed'][day][d] == False and up == 0:
                        #print("Day %d, crew %d in div %d not raced" % (day, c, d))
                        raceday = False
                    break
                tmp -= event['div_size'][day][d]

            if event['skip'][day][c] == True:
                raceday = False
                
            xpos = xpos + state['scale']
            ypos = ypos - (up*state['scale'])

            if raceday:
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
                arr = [state['dash'], (state['dash']/2) * (len(colours)-1)]
                off = 0
                nextoff = arr[1]
                for l in lines:
                    for c in colours:
                        polyline = out.polyline(points=l, stroke=c, stroke_width=3, fill='none')
                        polyline.dasharray(arr, offset=off)
                        out.add(polyline)
                        off = nextoff
                        nextoff = nextoff - (state['dash']/2)
                        arr = [state['dash']/2, (state['dash']/2) * len(colours)]

        else:
            for l in lines:
                out.add(out.polyline(points=l, stroke=colour, stroke_width=linewidth, fill='none'))

        for line in skipped:
            out.add(out.polyline(points=line, stroke="lightgray", stroke_width=1, fill='none'))
                
                    
        top = top + state['scale']


    #top = yoff
    # box around all divisions
    out.add(out.rect(insert=(xoff-space,yoff), size=((event['days'] * state['scale'])+(space*2), len(event['crews']) * state['scale']), stroke='black', fill='none'))

    # draw in lines between divisions
    left = xoff-space
    right = left + space + state['scale']
    prev_div_height = None
    for day in range(event['days']):
        div_height = []
        top = yoff
        if day == event['days']-1:
            right += space
        for div in range(len(event['div_size'][day])-1):
            top += event['div_size'][day][div] * state['scale']
            div_height.append(top)
            out.add(out.line(start=(left, top), end=(right, top), stroke='black', stroke_width=1))

            if prev_div_height is not None and prev_div_height[div] != div_height[div]:
                out.add(out.line(start=(left, prev_div_height[div]), end=(left, div_height[div]), stroke='black', stroke_width=1))

        prev_div_height = div_height
        left = right
        right += state['scale']

    return yoff + (len(event['crews']) * state['scale'])

def draw_extra_text(out, xoff, yoff, event, extra):
    top = yoff
    for div_num in range(len(event['div_size'][0])):
        label = None
        fontsize = 25
        colour = 'lightgray'
        num = event['div_size'][0][div_num]

        if extra == 'number' and num > 8:
            label = "Division %d" % (div_num+1)
        elif extra == 'title' and num > 12:
            label = "%s %d - %s" % (event['short'], event['year'], event['gender'])
        elif extra == 'both':
            fontsize = 12
            colour = 'darkred'
            if num > 10:
                label = "%s %d - %s, Division %d" % (event['short'], event['year'], event['gender'], div_num+1)
            else:
                label = "Division %d" % (div_num+1)

        if label != None:
            text = out.add(out.text(label, insert=None, font_size=fontsize, stroke_width=0, fill=colour))
            text.rotate(90, [xoff, top+5])

        top = top + (state['scale'] * num)


def draw_numbers(out, xoff, yoff, event, align, reset = False):
    top = yoff
    number = 1
    div_num = 0
    
    for crew in event['crews']:
        top = top + state['scale']
        out.add(out.text(str(number), insert=(xoff, top-3), font_size=13, stroke_width=0, fill='gray', text_anchor=align))
        number = number + 1
        if reset and number-1 == event['div_size'][0][div_num]:
            number = 1
            div_num += 1

def draw_crews(out, xoff, yoff, event, gain, align):
    top = yoff
    for crew in event['crews']:
        top = top + state['scale']
        offset = 0        
        if gain == 1:
            if crew['gain'] is None:
                continue
            offset = state['scale'] * crew['gain']
        colour = 'black'
        if crew['highlight']:
            colour = 'blue'
        elif crew['blades']:
            colour = 'red'
        out.add(out.text(crew['start'], insert=(xoff,top-3-offset), font_size=13, stroke_width=0, fill=colour, text_anchor=align))

def draw_stripes(out, xoff, yoff, width, x2off, event, event2 = None, extra = 0):
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
            rect = out.add(out.rect(insert=(xoff,top), size=(swidth, state['scale']), fill='lightgray', stroke_opacity=0, stroke_width=0))
            rect.fill(opacity=0.35)
        alt = 1 - alt
        top = top + state['scale']
        cn = cn + 1

    if x2off != None and False:
        alt = 0
        for r in range(0, event['days']):
            if alt == 1:
                rect = out.add(out.rect(insert=(x2off + (r * state['scale']), yoff), size=(state['scale'], top-yoff), fill='lightgray', stroke_width=0))
                rect.fill(opacity=0.15)
            alt = 1 - alt

def draw_join(out, xoff, yoff, event, event2):
    added = []
    yoff = yoff + (state['scale']/2)
    cn2 = 0
    for div2 in event2['divisions']:
        for crew2 in div2:
            cn = 0
            found = False
            for div in event['divisions']:
                for crew in div:
                    if crew2['start'] == crew['end']:
                        found = True
                        break
                    cn = cn + 1
                if found:
                    break
            if found:
                out.add(out.line(start=(xoff, yoff + (state['scale']*cn)), end=(xoff + state['sep'], yoff + (state['scale']*cn2)), stroke = 'lightgray', stroke_width = 1))
            else:
                added.append({'height' : (yoff + (state['scale'] * cn2)), 'crew' : crew2})
            cn2 = cn2 + 1

    xsep = state['sep'] / (len(added)+1)
    xpos = xoff + xsep
    ynext = yoff + (state['scale'] * event['crews']) - (state['scale']/2) + 4
    ysep = 12
    for crew in added:
        out.add(out.line(start=(xpos, crew['height']), end=(xpos, ynext), stroke = 'gray', stroke_width = 1))
        out.add(out.line(start=(xpos, crew['height']), end=(xoff + state['sep'], crew['height']), stroke = 'gray', stroke_width = 1))
        out.add(out.text(crew['crew']['start'], insert=(xpos, ynext+8), font_size=9, stroke_width=0, fill='black', text_anchor='end'))
        xpos = xpos + xsep
        ynext = ynext + ysep

    return ynext
    

def write_svg(state):
    out = simplesvg.Drawing()

    event = state['sets'][0]
    left = 15+25
    
    draw_stripes(out, left, 0, (state['right']*2) + (state['scale'] * event['days']), state['right'], event)
    draw_numbers(out, left+3, 0, event, 'start', True)
    draw_numbers(out, left + (2*state['right']) + (state['scale'] * event['days']) -3, 0, event, 'end', False)
    #draw_extra_text(out, left+20, 0, event, 'number')
    #draw_extra_text(out, left + (2*state['right']) + (state['scale'] * event['days']) -40, 0, event, 'name') 
    draw_extra_text(out, left-15, 0, event, 'both')

    draw_crews(out, left + state['right']-3, 0, event, 0, 'end')
    draw_crews(out, left + state['right'] + (state['scale'] * event['days']) + 3, 0, event, 1, 'start')

    h = draw_divisions(out, left + state['right'], 0, event, state['right'], draw_colours = state['colours'])
    
    out.setsize(left + (state['right']*2) + (state['scale'] * event['days']), h)

    if state['output'] is None:
        print(out.tostring())
    else:
        fp = open(state['output'], 'w')
        fp.write(out.tostring())
        fp.close()
                    

def write_multi_svg(state):
    out = simplesvg.Drawing()
    sets = state['sets']
    
    width = 0
    height = 0
    top = 20

    xpos = state['right']
    eleft = state['right']
    for event_num in range(0, len(sets)):
        event = sets[event_num]
        event2 = event
        extra = state['sep']
        if event_num < len(sets)-1:
            event2 = sets[event_num+1]
        else:
            extra = state['right']

        out.add(out.text(str(event['year']), insert=(xpos+(state['scale'] * event['days'])/2, top-3), font_size=13, stroke_width=0, fill='black', text_anchor='middle'))
        draw_stripes(out, xpos-eleft, top, eleft + (state['scale'] * event['days']), xpos, event, event2, extra)
        eleft = 0
        xpos = xpos + (state['scale'] * event['days']) + state['sep']

        if event_num < len(sets)-1:
            h = draw_join(out, xpos-state['sep'], top, event, event2)
            if h > height:
                height = h

    width = xpos - state['sep'] + state['right']
    draw_numbers(out, 3, top, sets[0], 'start', False)
    draw_numbers(out, xpos - state['sep'] + state['right'] - 3, top, sets[-1], 'end', False)

    draw_crews(out, state['right']-3, top, sets[0], 0, 'end')
    draw_crews(out, xpos - state['sep'] + 3, top, sets[-1], 1, 'start')

    xpos = state['right']
    for event in sets:
        h = draw_divisions(out, xpos, top, event, 0, draw_colours = state['colours'])
        if h > height:
            height = h
        xpos = xpos + (state['scale'] * event['days']) + state['sep']

    out.setsize(width, height)

    if state['output'] is None:
        print(out.tostring())
    else:
        fp = open(state['output'], 'w')
        fp.write(out.tostring())
        fp.close()

def step_on(event):
    for div in event['divisions']:
        for crew in div:
            crew['start'] = crew['end']
            crew['gain'] = 0
            crew['blades'] = False

    event['year'] = event['year']+1
    del event['move']
    del event['completed']
    event['results'] = []
        
        
def write_file(state, name):
    output = open(name, "w")
    event = state['sets'][0]
    output.write("Set,%s\n" % event['set'])
    output.write("Short,%s\n" % event['short'])
    output.write("Gender,%s\n" % event['gender'])
    output.write("Year,%s\n" % event['year'])
    if event['days'] != 4:
        output.write("Days,%s\n" % event['days'])

    output.write("\n")

    abbrev = {}
    if event['set'] in state['abbrev_map']:
        abbrev = state['abbrev_map'][event['set']]

    for i in event['divisions']:
        output.write("Division")
        for crew in i:
            for p in abbrev:
                if crew['start'].startswith(abbrev[p]['name']):
                    fin = p
                    sh = crew['start'][len(abbrev[p]['name']):].strip()
                    if len(sh) > 0:
                        for k in range(0, len(abbreviations.roman)):
                            if sh == abbreviations.roman[k]:
                                fin = fin + str(k+1)
                                break
                    output.write(",%s" % fin)
                    break
        output.write("\n")
    output.write("\n")
    if len(event['results']) > 0:
        output.write("Results\n")
        for i in event['results']:
            output.write("  %s\n" % i)

    output.close()

def addn(d, k, n):
    if k in d:
        d[k] = d[k] + n
    else:
        d[k] = n

def get_ave(d):
    total = 0
    num = 0
    for k in d:
        total = total + (k * d[k])
        num = num + d[k]
    return float(total) / float(num)

def get_stats(event, days):
    up = []
    for d in event['divisions']:
        up.append({})
    upa = {}

    for day_num in range(0, len(event['move'])):
        m = event['move'][day_num]
        for div_num in range(0, len(m)):
            if event['completed'][day_num][div_num]:
                dstat = up[div_num]
                for s in m[div_num]:
                    if s < 0:
                        s = -s
                    addn(days[day_num], s, 1)
                    addn(dstat, s, 1)
                    addn(upa, s, 1)

    #for d in range(0, len(up)):
    #    print "%s/%s/%s %d %g %s" % (event['short'], event['year'], event['gender'], d+1, get_ave(up[d]), up[d])

    #print "%s/%s/%s %g %s" % (event['short'], event['year'], event['gender'], get_ave(upa), upa)

state = {
    'highlight' : None,
    'readstdin' : False,
    'colours' : False,
    'output' : None,
    'stepon' : False,
    'scale' : 16,
    'right' : 130,
    'sep' : 32, #scale*2
    'dash' : 6,
    'sets' : [],
    'abbrev_map' : {'Summer Eights' : abbreviations.ocol,
                    'Lent Bumps' : abbreviations.ccol,
                    'May Bumps' : abbreviations.ccol,
                    'Torpids' : abbreviations.ocol}
}
    
sys.argv.pop(0)
while len(sys.argv) > 0:
    arg = sys.argv.pop(0)
    
    if arg == '-c':
        state['colours'] = True
    elif arg == '-w':
        state['output'] = sys.argv.pop(0)
    elif arg == '-s':
        state['stepon'] = True
    elif arg == '-h':
        state['highlight'] = sys.argv.pop(0)
    elif arg == '-r':
        state['readstdin'] = True
    else:
        sys.argv.insert(0, arg)
        break

while len(sys.argv) > 0:
    #print "doing %s" % sys.argv[0]
    state['sets'].append(read_file(state, sys.argv.pop(0), state['highlight']))

if state['readstdin']:
    state['sets'].append(read_file(state, None, state['highlight']))

#days = [{}, {}, {}, {}]

for s in state['sets']:
    process_results(s)
    #get_stats(s, days)

#for d in days:
#    print "%g %s" % (get_ave(d), d)

if len(state['sets']) == 1:
    if state['stepon'] == False:
        write_svg(state)
    else:
        step_on(state['sets'][0])
        write_file(state, "out.txt")
else:
    write_multi_svg(state)
