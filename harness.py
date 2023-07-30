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


def add_crew(div, str, abbrev):
    #print str
    div.append({'gain' : 0, 'blades' : False, 'highlight' : False})

    str = str.strip()
    short = str.strip("0123456789")
    if short in abbrev:
        num = str.strip("abcdefghijklmnopqrtsuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        if len(num) > 0:
            str = "%s %s" % (abbrev[short]['name'], abbreviations.roman[int(num)-1])
        else:
            str = abbrev[short]['name']
        div[-1]['college'] = abbrev[short]

    div[-1]['start'] = str
    div[-1]['end'] = str

  

def read_file(state, name, highlight = None):
    abbrev = {}
    
    if name != None:
        input = open(name, "r")
    else:
        input = sys.stdin
    ret = {}
    ret['title'] = "Set name"
    ret['days'] = 4
    ret['crews'] = 0
    ret['divisions'] = []
    ret['results'] = []

    curdiv = []
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
            if len(curdiv) > 0:
                ret['divisions'].append(curdiv)
                curdiv = []
            if len(p) > 1:
                for i in p[1:]:
                    add_crew(curdiv, i, abbrev)
                    ret['crews'] = ret['crews'] + 1
        elif p[0] == "Results":
            if curdiv != None and len(curdiv) > 0:
                ret['divisions'].append(curdiv)
                curdiv = None
            for i in p[1:]:
                i = i.strip()
                if not i.startswith("#"):
                    ret['results'].append(i)
        elif curdiv == None:
            for i in p:
                i = i.strip()
                if not i.startswith("#"):
                    ret['results'].append(i)
        else:
            for i in p:
                add_crew(curdive, i, abbrev)
                ret['crews'] = ret['crews'] + 1

    if name != None:
        input.close()

    if highlight != None:
        for div in ret['divisions']:
            for crew in div:
                if crew['start'].startswith(highlight):
                    crew['highlight'] = True
                    
    return ret

def create_blank_move(event):
    event['move'] = []
    event['completed'] = []
    for d in range(0, event['days']):
        today = []
        comp = []
        for n in event['divisions']:
            div = []
            for c in n:
                div.append(0)
            today.append(div)
            comp.append(False)
        event['move'].append(today)
        event['completed'].append(comp)

def find_sandwich_boat(div):
    for p in range(0, len(div)):
        #print("crew %d, move %d, sum:%d" % (p, div[p], p - div[p]))
        if p - div[p] == 0:
            return p

    print("Can't find sandwich crew from division %d" & div_num)
    return None
        
def process_bump(move, div_num, crew, up):
    if crew - up < 1:
        print("Bumping up above the top of the division: div %d, crew %d, up %d" % (div_num, crew, up))
        return False
    if move[div_num-1][crew-1-up] != 0:
        print("Bumping a crew that has already got a result")
        return False
    move[div_num-1][crew-1-up] = -up
    if crew > len(move[div_num-1]):
        # sandwich boat bumping up, need to find out which crew is sandwich boat
        p = find_sandwich_boat(move[div_num])
        if p is None:
            return False
        move[div_num][p] = move[div_num][p] + up
    else:
        move[div_num-1][crew-1] = up
    return True

def process_results(event):
    debug = True

    create_blank_move(event)

    all = ""
    for r in event['results']:
        all = all + r

    pat = re.compile('r|t|u|o[0-9]+|e-?[0-9]+|w[0-9]+|d<[^>]*>')
    m = pat.findall(all)
    day_num = 0  # 1 is the first day
    div_num = 0  # 1 is the first division
    crew = 0     # 1 is the top crew in each division
    move = None
    for c in m:
        if debug:
            print("\nNew command:%s (day:%d div:%d crew:%d)" % (c, day_num, div_num, crew))

        while move != None and crew <= len(move[div_num-1]) and crew > 0 and move[div_num-1][crew-1] != 0:
            if debug:
                print("Skipping crew:%d, got %d" % (crew, move[div_num-1][crew-1]))
            # if we've already got a result for this crew, then we can 
            # ignore it
            crew = crew - 1

        # only allow division size changes between full days of racing, and not before the first day
        if c[0] == 'd' and crew == 0 and day_num > 0:
            # division size change
            sizes = c.replace("<"," ").replace(">"," ").replace("."," ").split()[1:]
            sizes = [ int(x) for x in sizes ]
            
            print("Div size change: %s" % sizes)
            if len(sizes) == len(event['divisions']):
                num = 0
                for s in sizes:
                    num += s
                if num == event['crews']:
                    print(event['move'])
                    for day in range(day_num, len(event['move']), 1):
                        for div in range(len(sizes)):
                            event['move'][day][div] = [0] * sizes[div]
                    print(event['move'])
            
        if crew == 0:
            if div_num <= 1:
                if day_num == event['days']:
                    print("Run out of days of racing with more results still to go")
                    return
                move = event['move'][day_num]
                day_num = day_num + 1
                div_num = len(event['divisions'])+1
                if debug:
                    print("Moving to day:%d" % (day_num))

            div_num = div_num - 1;
            crew = len(move[div_num-1])
            if div_num < len(event['divisions']):
                # add one for sandwich crew
                crew = crew + 1
            if debug:
                print("Moving to div:%d crew:%d" % (div_num, crew))

        if debug:
            print("Processing command:%s (day:%d div:%d crew:%d)" % (c, day_num, div_num, crew))

        if c == 'r':
            # row over, move to the next crew
            crew = crew - 1
            if debug:
                print("Rowover, moving to crew %d" % crew)
        elif c == 'u':
            # up 1
            if process_bump(move, div_num, crew, 1) == False:
                return
            crew = crew - 2
            if debug:
                print("Bumped up, moving to crew %d" % crew)
        elif c.startswith("o"):
            up = int(c[1:])
            if process_bump(move, div_num, crew, up) == False:
                return
            crew = crew - 1
            if debug:
                print("Overbumped %d, moving to crew %d" % (up, crew))
        elif c.startswith("e"):
            up = int(c[1:])
            if crew > len(move[div_num-1]):
                # sandwich boat bumping up, need to find out which crew is sandwich boat
                p = find_sandwich_boat(move[div_num])
                if p is None:
                    return
                if debug:
                    print("Exact move %d to crew %d, sandwich boat in div %d, was %d now %d" % (up, p, div_num, move[div_num][p], move[div_num][p]+up))
                move[div_num][p] = move[div_num][p] + up
            else:
                move[div_num-1][crew-1] = up
            crew = crew - 1
            if debug:
                print("Moved %d, moving to crew %d" % (up, crew))
        elif c.startswith("w"):
            size = int(c[1:])
            if crew - size < 1:
                print("Washing machine size %d get above head of division" % size)
                return
            if crew > len(move[div_num-1]):
                p = find_sandwich_boat(move[div_num])
                if p is None:
                    return
                if debug:
                    print("Washing machine sandwich crew up one")
                move[div_num][p] += 1
            else:
                if debug:
                    print("Washing machine crew %d up one" % crew)
                move[div_num-1][crew-1] = 1

            for j in range(1, size, 1):
                if debug:
                    print("Washing machine crew %d up one" % (crew-j))
                move[div_num-1][crew-j-1] = 1
            if debug:
                print("Washing machine crew %d down %d.  Moving to crew %d" % (crew-size, size, crew-size-1))
            move[div_num-1][crew-size-1] = -size
            crew = crew - (size+1)
                
        elif c == 't':
            crew = 0
            continue

        # if we've seen at least one result, mark this division as completed
        event['completed'][day_num-1][div_num-1] = True

    # work out finishing names and blades, etc
    for div_num in range(0, len(event['divisions'])):
        for crew_num in range(0, len(event['divisions'][div_num])):
            nc = crew_num;
            nd = div_num
            gain = 0
            blades = True
            for m in event['move']:
                gain = gain + m[nd][nc]
                if m[nd][nc] <= 0:
                    blades = False
                nc = nc - m[nd][nc]

                while nc < 0:
                    nd = nd - 1
                    nc = nc + len(m[nd])
                while nc >= len(m[nd]):
                    nc = nc - len(m[nd])
                    nd = nd + 1

            if nd == 0 and nc == 0 and event['completed'][-1][0] == True:
                blades = True

            event['divisions'][div_num][crew_num]['gain'] = gain
            event['divisions'][div_num][crew_num]['blades'] = blades
            event['divisions'][nd][nc]['end'] = event['divisions'][div_num][crew_num]['start']
            

def draw_divisions(out, xoff, yoff, event, space, draw_colours = False):
    top = yoff
    for div_num in range(0, len(event['divisions'])):
        for crew_num in range(0, len(event['divisions'][div_num])):
            ypos = top + (state['scale']/2)
            xpos = xoff
            c = crew_num
            d = div_num
            crew = event['divisions'][div_num][crew_num]
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
            points = []
            last = [xpos, ypos]
            
            for day in range(0, event['days']):
                t = event['move'][day]
                up = t[d][c]

                raceday = True
                if event['completed'][day][d] == False and up == 0:
                    raceday = False

                #out.add(out.line(start=(xpos, ypos), end=(xpos+state['scale'], ypos-(up*state['scale'])), stroke=colour, stroke_width=linewidth))
                xpos = xpos + state['scale']
                ypos = ypos - (up*state['scale'])

                if raceday:
                    if len(points) == 0:
                        points.append(last)
                    points.append([xpos, ypos])
                elif len(points) > 0:
                    lines.append(points)
                    points = []
                    
                last = [xpos, ypos]
                
                c = c - up;
                while c < 0:
                    d = d-1
                    c += len(t[d])
                while c >= len(t[d]):
                    c -= len(t[d])
                    d = d+1

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

            for i in range(len(lines) - 1):
                p = [lines[i][-1], lines[i+1][0]]
                out.add(out.polyline(points=p, stroke="lightgray", stroke_width=1, fill='none'))
                
                    
            top = top + state['scale']

    top = yoff
    for d in event['divisions']:
        out.add(out.rect(insert=(xoff-space,top), size=((event['days'] * state['scale'])+(space*2), len(d) * state['scale']), stroke='black', fill='none'))
        top = top + (state['scale'] * len(d))

    return top

def draw_extra_text(out, xoff, yoff, event, extra):
    top = yoff
    for div_num in range(0, len(event['divisions'])):
        d = event['divisions'][div_num]

        label = None
        fontsize = 25
        colour = 'lightgray'

        if extra == 'number' and len(d) > 8:
            label = "Division %d" % (div_num+1)
        elif extra == 'title' and len(d) > 12:
            label = "%s %d - %s" % (event['short'], event['year'], event['gender'])
        elif extra == 'both':
            fontsize = 12
            colour = 'darkred'
            if len(d) > 10:
                label = "%s %d - %s, Division %d" % (event['short'], event['year'], event['gender'], div_num+1)
            else:
                label = "Division %d" % (div_num+1)

        if label != None:
            text = out.add(out.text(label, insert=None, font_size=fontsize, stroke_width=0, fill=colour))
            text.rotate(90, [xoff, top+5])

        top = top + (state['scale'] * len(d))


def draw_numbers(out, xoff, yoff, event, align, reset = False):
    top = yoff
    number = 1
    for d in event['divisions']:
        for crew in d:
            top = top + state['scale']
            out.add(out.text(str(number), insert=(xoff, top-3), font_size=13, stroke_width=0, fill='gray', text_anchor=align))
            number = number + 1
        if reset:
            number = 1       

def draw_crews(out, xoff, yoff, event, gain, align):
    top = yoff
    for d in event['divisions']:
        for crew in d:
            top = top + state['scale']
            colour = 'black'
            if crew['highlight']:
                colour = 'blue'
            elif crew['blades']:
                colour = 'red'
            out.add(out.text(crew['start'], insert=(xoff,top-3-(gain * state['scale'] * crew['gain'])), font_size=13, stroke_width=0, fill=colour, text_anchor=align))

def draw_stripes(out, xoff, yoff, width, x2off, event, event2 = None, extra = 0):
    top = yoff
    alt = 0

    num = 0
    if event2 != None:
        num = event2['crews']

    cn = 0
    for d in event['divisions']:
        for crew in d:
            swidth = width
            if cn < num:
                swidth = swidth + extra
            if alt == 1:
                rect = out.add(out.rect(insert=(xoff,top), size=(swidth, state['scale']), fill='lightgray', stroke_width=0))
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
