#!/bin/python3

import re
import abbreviations

# crew name syntax: (apologies for abuse of BNF)
# <name> ::= <club><opt-suffix><opt-number>
# <club> ::= <abbreviated code> | <full club name, any characters apart from parenthesis>
# <opt-suffix> ::= "(" <suffix> ")" | ""
# <opt-number> ::= <number> | ""
# <suffix> ::= <any characters apart from parenthesis>
# <number> ::= <number in decimal>

def add_crew(crew_state, crews, str, abbrev):
    crew = {'gain' : 0, 'blades' : False, 'highlight' : False}

    if 'pat' not in crew_state:
        crew_state['pat'] = re.compile("^(.*?)(\([^\)]*\))?[ ]*([0-9]*)$")

    m = crew_state['pat'].match(str)
    if m is None:
        print("Can't understand crew name '%s'" % str)
        return

    club = m.group(1).strip()
    extra = m.group(2)
    number = m.group(3)

    if club in abbrev:
        club = abbrev[club]['name']

    if number == "":
        num = 1
    else:
        num = int(number)

    if club not in crew_state:
        crew_state[club] = 1

    if num != crew_state[club]:
        print("Club %s crews out of order (found %d, expecting %d)" % (club, num, crew_state[club]))

    crew_state[club] = num+1

    name = club
    if extra is not None:
        name += " " + extra
    if num > 1:
        if num < len(abbreviations.roman):
            name += " " + abbreviations.roman[num-1]
        else:
            name += " %d" % num

    #print("'%s' -> '%s' (club=%s)" % (str, name, club))
            
    crew['start'] = name
    crew['end'] = None
    crews.append(crew)

def read_file(name, highlight = None):
    abbrev = {}

    crew_state = {}
    
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
            if ret['set'] in abbreviations.sets:
                abbrev = abbreviations.sets[ret['set']]
            
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
                    add_crew(crew_state, ret['crews'], i, abbrev)
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

def swap_crews(move, back, pos_a, pos_b):
    orig_a = back[pos_a]
    if orig_a is None:
        orig_a = pos_a
        if move[orig_a] is not None:
            print("Crew %d not expected to have a result" % orig_a)
            return False
        move[orig_a] = 0

    orig_b = back[pos_b]
    if orig_b is None:
        orig_b = pos_b
        if move[orig_b] is not None:
            print("Crew %d not expecting to have a result" % orig_b)
            return False
        move[orig_b] = 0

    #print("Swapping cur: %d,%d orig:%d,%d move:%d->%d,%d->%d" % (pos_a, pos_b, orig_a, orig_b, move[orig_a], move[orig_a] - pos_b + pos_a, move[orig_b], move[orig_b] + pos_b - pos_a))
        
    move[orig_a] -= pos_b - pos_a
    move[orig_b] += pos_b - pos_a

    back[pos_a] = orig_b
    back[pos_b] = orig_a
    return True

def process_bump(move, back, crew_num, up, div_head):
    if crew_num - up < div_head:
        print("Bumping up above the top of the division: div_head %d, crew %d, up %d" % (div_head, crew_num, up))
        return False
    if move[crew_num - up] is not None:
        print("Bumping a crew that has already got a result")
        return False

    return swap_crews(move, back, crew_num, crew_num-up)

def process_chain(move, back, crew_num, num):
    for i in range(num):
        if swap_crews(move, back, crew_num, crew_num+1) == False:
            return False
        crew_num += 1
    return True

def check_results(event, move, back, debug):
    results = []
    ret = True
    for i in range(len(event['crews'])):
        if back[i] is None and i < len(event['crews']) - event['crews_withdrawn']:
            print("Error: back[%d] is None" % i)
            ret = False
        else:
            if back[i] in results and back[i] is not None:
                print("Error: back[%d]=%s is already a back entry" % (i, back[i]))
                ret = False
            results.append(back[i])

        if debug:
            out = "%2d: %25s " % (i, event['crews'][i]['start'])
            for j in range(event['days']):
                out += "| %3s %3s " % (event['move'][j][i], event['back'][j][i])
            print(out)

    return ret

def process_results(event):
    debug = False

    event['move'] = []
    event['back'] = []
    event['completed'] = []
    event['skip'] = []
    for d in range(event['days']):
        event['move'].append([None] * len(event['crews']))
        event['back'].append([None] * len(event['crews']))
        event['skip'].append([False] * len(event['crews']))
        event['completed'].append([False] * len(event['div_size'][0]))
    
    all = ""
    for r in event['results']:
        all = all + r

    pat = re.compile('r|t|u|o[0-9]+|e-?[0-9]+|v-?[0-9]+|w[0-9]+|x|d<[^>]*>|p')
    m = pat.findall(all)
    day_num = 0                                                   # 0 is the first day
    div_num = len(event['div_size'][day_num])-1                   # 0 is the first division
    crew_num = len(event['crews'])-1                              # 0 is the headship crew
    div_head = crew_num - event['div_size'][day_num][div_num] + 1 # index of the head crew in the current division
    event['crews_withdrawn'] = 0
    penalty = 0
    
    for c in m:
        move = event['move'][day_num]
        back = event['back'][day_num]
        
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
                if num == len(event['crews']) - event['crews_withdrawn']:
                    for day in range(day_num+1, event['days'], 1):
                        event['div_size'][day] = sizes

        # if we've already got a result for this crew, then we can skip over it
        while crew_num >= div_head and move[crew_num] is not None:
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

                if check_results(event, move, back, debug) == False:
                    return

                move = event['move'][day_num]
                back = event['back'][day_num]
                div_num = len(event['div_size'][day_num])-1
                crew_num = len(event['crews']) - 1 - event['crews_withdrawn']
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
            if back[crew_num] is None:
                back[crew_num] = crew_num
                move[crew_num] = 0
            crew_num = crew_num - 1
            if debug:
                print("Rowover, moving to crew %d" % crew_num)
        elif c == 'u':
            # up 1
            if process_bump(move, back, crew_num, 1, div_head) == False:
                return
            crew_num = crew_num - 2
            if debug:
                print("Bumped up, moving to crew %d" % crew_num)
        elif c.startswith("o"):
            up = int(c[1:])
            if process_bump(move, back, crew_num, up, div_head) == False:
                return
            crew_num = crew_num - 1
            if debug:
                print("Overbumped %d, moving to crew %d" % (up, crew_num))
        elif c.startswith("e") or c.startswith("v"):
            up = int(c[1:])

            if move[crew_num] is None:
                p = crew_num
                move[crew_num] = 0
            else:
                p = back[crew_num]

            move[p] += up
            back[crew_num-up] = p

            if penalty != 0:
                if debug:
                    print("Applying penalty %d to crew %d" % (penalty, crew_num-up))
                if process_chain(move, back, crew_num-up, penalty) == False:
                    return
                penalty = 0
            
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

            if debug:
                print("Washing machine, crew %d, size %d" % (crew_num, size))
            if process_chain(move, back, crew_num-size, size) == False:
                return
            crew_num = crew_num - (size+1)

        elif c == 'x':
            if debug:
                print("Crew %d withdrawn, moving to crew %d" % (crew_num, crew_num-1))
            event['crews_withdrawn'] += 1
            crew_num -= 1
            event['div_size'][day_num][div_num] -= 1
            for day in range(day_num+1, event['days'], 1):
                event['div_size'][day][div_num] = event['div_size'][day_num][div_num]
            
        elif c == 't':
            for i in range(div_head, crew_num+1):
                if move[i] is None:
                    move[i] = 0
                if back[i] is None:
                    back[i] = i

            if debug:
                print("Skipping division, setting crew from %d to div_head-1 %d" % (crew_num, div_head-1))
            crew_num = div_head-1
            continue

        elif c == 'p':
            penalty += 1
            if debug:
                print("Storing %d penalty bump to apply to crew %d" % (penalty, crew_num))
                
        # if we've seen at least one result, mark this division as completed
        event['completed'][day_num][div_num] = True

    full_set = False
    if day_num == event['days']-1 and crew_num == -1:
        if check_results(event, move, back, debug) == False:
            return

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
        
def write_file(event, name):
    output = open(name, "w")
    output.write("Set,%s\n" % event['set'])
    output.write("Short,%s\n" % event['short'])
    output.write("Gender,%s\n" % event['gender'])
    output.write("Year,%s\n" % event['year'])
    if event['days'] != 4:
        output.write("Days,%s\n" % event['days'])

    output.write("\n")

    abbrev = {}
    if event['set'] in abbreviations.sets:
        abbrev = abbreviations.sets[event['set']]

    crew_num = 0
    for div_size in event['div_size'][-1]:
        output.write("Division")
        for i in range(div_size):
            crew = event['crews'][crew_num+i]
            found = False
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
                    found = True
                    break
            if not found:
                output.write(",%s" % crew['start'])
        output.write("\n")
        crew_num += div_size
        
    output.write("\n")
    if len(event['results']) > 0:
        output.write("Results\n")
        for i in event['results']:
            output.write("  %s\n" % i)

    output.close()
