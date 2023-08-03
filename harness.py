#!/bin/python3

# todo:
#
# check that crews from the same college appear in order
# collect results/crews for each college for summary statistics
#   most/least bumps in a division all week
#   which day overbumps occur, etc
# add cra club names
# figure out how to tell how long a piece of text is

import sys, re
import abbreviations, draw

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
    crew['end'] = None
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

    full_set = False
    if day_num == event['days']-1 and crew_num == -1:
        if debug:
            print("Completed all divisions & days")
        full_set = True
        
    # work out finishing names and blades, etc
    for crew_num in range(len(event['crews'])):
        nc = crew_num;
        gain = 0
        blades = True
        finished = True
        for m in event['move']:
            if m[nc] == None:
                event['crews'][crew_num]['gain'] = None
                finished = False
                break
            
            gain = gain + m[nc]
            if m[nc] <= 0:
                blades = False
            nc = nc - m[nc]

        if finished:
            # only award headship blades if we've completed all the racing
            if nc == 0 and full_set == True:
                blades = True

            event['crews'][crew_num]['gain'] = gain
            event['crews'][crew_num]['blades'] = blades
            event['crews'][nc]['end'] = event['crews'][crew_num]['start']
            

def step_on(event):
    for crew in event['crews']:
        crew['start'] = crew['end']
        crew['gain'] = 0
        crew['blades'] = False

    event['year'] = event['year']+1
    del event['move']
    del event['completed']
    del event['skip']
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

    crew_num = 0
    for div_size in event['div_size'][-1]:
        output.write("Division")
        for i in range(div_size):
            crew = event['crews'][crew_num+i]
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
        crew_num += div_size
        
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
    'sets' : [],
    'highlight' : None,
    'readstdin' : False,
    'output' : None,
    'stepon' : None,
    
    'svg_config' : {'scale' : 16,
                    'right' : 128, #scale*8
                    'sep' : 32, #scale*2
                    'dash' : 6,
                    'colours' : False},
    'abbrev_map' : {'Summer Eights' : abbreviations.ocol,
                    'Lent Bumps' : abbreviations.ccol,
                    'May Bumps' : abbreviations.ccol,
                    'Torpids' : abbreviations.ocol}
}
    
cmd = sys.argv.pop(0)
if len(sys.argv) == 0:
    print("%s   Usage notes" % cmd)
    print(" -c          : Enables per-club colours in results lines")
    print(" -r          : Enables reading results from stdin")
    print(" -h <prefix> : Enables highlights for crews with names starting with <prefix>")
    print(" -w <file>   : Writes svg output to <file>")
    print(" -s <file>   : Writes template for next year into <file>")
    print(" Any additional arguments are treated as files containing results to be read in")
    sys.exit()

while len(sys.argv) > 0:
    arg = sys.argv.pop(0)
    
    if arg == '-c':
        state['svg_config']['colours'] = True
    elif arg == '-r':
        state['readstdin'] = True
    elif arg == '-h':
        state['highlight'] = sys.argv.pop(0)
    elif arg == '-w':
        state['output'] = sys.argv.pop(0)
    elif arg == '-s':
        state['stepon'] = sys.argv.pop(0)
    else:
        sys.argv.insert(0, arg)
        break

while len(sys.argv) > 0:
    state['sets'].append(read_file(state, sys.argv.pop(0), state['highlight']))

if state['readstdin']:
    state['sets'].append(read_file(state, None, state['highlight']))

for s in state['sets']:
    process_results(s)
    #get_stats(s, days)

if len(state['sets']) == 1:
    if state['stepon'] is None:
        draw.write_svg(state['output'], state['sets'][0], state['svg_config'])
    else:
        step_on(state['sets'][0])
        write_file(state, state['stepon'])
else:
    draw.write_multi_svg(state['output'], state['sets'], state['svg_config'])
