import re
import abbreviations

# crew name syntax: (apologies for abuse of BNF)
# <name> ::= <club><opt-suffix><opt-number><opt-escape>
# <club> ::= <abbreviated code> | <full club name, any characters apart from parenthesis, trailing whitespace is trimmed>
# <opt-suffix> ::= "(" <suffix> ")" | ""
# <opt-number> ::= <number> | ""
# <opt-escape> ::= "*"
# <suffix> ::= <any characters apart from parenthesis>
# <number> ::= <number in decimal>
# If <opt-esacpe> is "*" any club crew numbering error is ignored

def add_crew(crew_state, crews, str, abbrev):
    crew = {'gain' : None, 'blades' : False, 'highlight' : False, 'withdrawn' : False}

    if 'pat' not in crew_state:
        crew_state['pat'] = re.compile("^(.*?)(\([^\)]*\))?[ ]*([0-9]*)(\*)?$")

    m = crew_state['pat'].match(str)
    if m is None:
        print("Can't understand crew name '%s'" % str)
        return False

    club = m.group(1).strip()
    extra = m.group(2)
    number = m.group(3)
    escape = m.group(4)

    if club in abbrev:
        club = abbrev[club]['name']

    if number == "":
        num = 1
    else:
        num = int(number)

    if club not in crew_state:
        crew_state[club] = 1

    if num != crew_state[club] and escape != "*" and len(club) > 0:
        print("Club %s crews out of order (found %d, expecting %d)<br>" % (club, num, crew_state[club]))
        return False

    crew_state[club] = num+1

    name = club
    if extra is not None:
        name += " " + extra

    if num > 1:
        if num < len(abbreviations.roman):
            name += " " + abbreviations.roman[num-1]
        else:
            name += " %d" % num
        num_name = name
    else:
        num_name = "%s I" % name

    #print("'%s' -> '%s' (club=%s)" % (str, name, club))
            
    crew['start'] = name
    crew['num_name'] = num_name
    crew['club'] = club
    crew['number'] = num
    crew['end'] = None
    crews.append(crew)
    return True

def read_file(name, highlight = None, data = None):
    abbrev = {}
    crew_state = {}
    time = re.compile("([0-9]*):([0-9][0-9](\.[0-9]+)*)")
    
    if name != None:
        try:
            input = open(name, "r")
        except:
            print("Failed to open file<br>")
            return None
    elif data != None:
        input = data.splitlines()
    else:
        input = sys.stdin
    ret = {}
    ret['title'] = "Set name"
    ret['days'] = 4
    ret['distance'] = 2500
    ret['flags'] = []
    ret['crews'] = []
    ret['div_size'] = None
    ret['results'] = []
    ret['pace'] = []

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
            ret['year'] = p[1]
        elif p[0] == "Days":
            ret['days'] = int(p[1])
        elif p[0] == "Distance":
            ret['distance'] = int(p[1])
        elif p[0] == "Flags":
            ret['flags'] += p[1:]
        elif p[0] == "Division":
            if ret['div_size'] is None:
                ret['div_size'] = []
                for d in range(ret['days']):
                    ret['div_size'].append([])
            for d in ret['div_size']:
                d.append(len(p)-1)
            if len(p) > 1:
                for i in p[1:]:
                    if add_crew(crew_state, ret['crews'], i, abbrev) == False:
                        return None
        elif p[0] == "Pace":
            for i in p[1:]:
                m = time.match(i)
                seconds = 0.0
                try:
                    seconds += int(m.group(1)) * 60.0
                    seconds += float(m.group(2))
                    ret['pace'].append(seconds)
                except:
                    print("Pace '%s' doesn't match required format of M:SS[.s]\n" % i)
                    return None
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
            print("Crew %d not expected to have a result<br>" % (orig_a+1))
            return False
        move[orig_a] = 0

    orig_b = back[pos_b]
    if orig_b is None:
        orig_b = pos_b
        if move[orig_b] is not None:
            print("Crew %d not expecting to have a result<br>" % (orig_b+1))
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
        print("Crew %d bumps up above the top of the division at position %d<br>" % (crew_num+1, div_head+1))
        return False
    if move[crew_num - up] is not None:
        print("Crew %d is bumping a crew at position %d that has already got a result<br>" % (crew_num+1, crew_num-up+1))
        return False

    return swap_crews(move, back, crew_num, crew_num-up)

def process_chain(move, back, crew_num, num):
    for i in range(num):
        if swap_crews(move, back, crew_num, crew_num+1) == False:
            return False
        crew_num += 1
    return True

def check_results(event, move, back, head, debug):
    results = []
    ret = True
    for i in range(len(event['crews'])):
        if back[i] is None and i < len(event['crews']) - event['crews_withdrawn'] and i >= head:
            print("Error: no crew finishes in position %d<br>" % (i+1))
            ret = False
        elif back[i] is not None and (i < head or i >= len(event['crews']) - event['crews_withdrawn']):
            print("Error: a crew finishes in position %d where none was expected<br>" % (i+1))
            ret = False
        else:
            if back[i] in results and back[i] is not None:
                print("Error: got two crews starting from position %d, second ending position %d<br>" % (back[i]+1, i+1))
                ret = False
            results.append(back[i])

        if debug:
            out = "%2d: %25s " % (i, event['crews'][i]['start'])
            for j in range(event['days']):
                out += "|%s%3s%s%3s " % ('(' if event['skip'][j][i] else " ", event['move'][j][i], ')' if event['skip'][j][i] else ' ', event['back'][j][i])
            print(out)

    return ret

def generate_results_by_pace(event, debug = False):
    for d in range(event['days']):
        move = event['move'][d]
        back = event['back'][d]
        if debug:
            print("Day:%d" % d, event['pace'], event['move'][d], event['back'][d], event['completed'][d])

        bumped_out = []
        while True:
            gaps = []
            last = None
            for i in range(len(event['crews'])):
                if i not in bumped_out:
                    if last is not None and event['pace'][i] < event['pace'][last]:
                        # length of eight: 19m
                        # 1 place to make up: 28.5m + 0.5m = 29m
                        # 3 places to make up: (28.5m * 3) + (19 * 2) + 0.5m = 124m
                        # n places to make up: (28.5m * n) + (19 * (n-1)) + 0.5m = 47.5n - 18.5
                        gaps.append((((47.5 * (i-last)) - 18.5) * event['pace'][i] / (event['pace'][last] - event['pace'][i]), i, last))
                    last = i

            if len(gaps) == 0:
                break

            gaps.sort(key = lambda x : x[0])
            (where,up,down) = gaps[0]
            if where < event['distance']:
                move[up] = up-down
                move[down] = down-up
                back[up] = down
                back[down] = up
                bumped_out.append(up)
                bumped_out.append(down)
                tmp = event['pace'][up]
                event['pace'][up] = event['pace'][down]
                event['pace'][down] = tmp
            else:
                break

        for i in range(len(move)):
            if move[i] is None:
                move[i] = 0
            if back[i] is None:
                back[i] = i

        event['completed'][d] = [True]
        if debug:
            print("Day:%d" % d, event['pace'], event['move'][d], event['back'][d], event['completed'][d])

def process_results(event):
    debug = False

    if event['div_size'] is None or len(event['crews']) == 0:
        return

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

    pat = re.compile('r|t|u|o[0-9]+|e-?[0-9]+|v-?[0-9]+|w[0-9]+|x|d\([^\)]*\)|p')
    m = pat.findall(all)
    day_num = 0                                                   # 0 is the first day
    div_num = len(event['div_size'][day_num])-1                   # 0 is the first division
    crew_num = len(event['crews'])-1                              # 0 is the headship crew
    div_head = crew_num - event['div_size'][day_num][div_num] + 1 # index of the head crew in the current division
    event['crews_withdrawn'] = 0
    penalty = 0
    move = None
    
    for c in m:
        move = event['move'][day_num]
        back = event['back'][day_num]
        
        if debug:
            print("\nNew command:%s (day:%d div:%d crew:%d div_head:%d)" % (c, day_num, div_num, crew_num, div_head))
            
        # only allow division size changes between full days of racing, and not before the first day
        if c[0] == 'd' and crew_num == -1 and day_num < event['days']-1:
            # division size change
            sizes = c.replace("("," ").replace(")"," ").replace("."," ").split()[1:]
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
            continue

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
                    print("Run out of days of racing with more results still to go<br>")
                    return

                if debug:
                    print("\nMoving to day %d" % day_num)

                if check_results(event, move, back, 0, debug) == False:
                    return

                move = event['move'][day_num]
                back = event['back'][day_num]
                div_num = len(event['div_size'][day_num])-1
                crew_num = len(event['crews']) - 1 - event['crews_withdrawn']
                div_head = crew_num - event['div_size'][day_num][div_num] + 1
            else:
                # not safe to call at the end of each division
                # this division may have crews skipping over a withdrawn crew
                # in the division above that hasn't been processed yet
                # (see cra2004_men.txt)
                #if check_results(event, move, back, div_head, debug) == False:
                #    return

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

            if p is None:
                print("Result %s applied to crew that can't be found in position %d" % (c, crew_num+1))
                return

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
            # work out the original crew number
            cn = crew_num
            dn = day_num-1
            while dn >= 0:
                cn = event['back'][dn][cn]
                dn -= 1
            event['crews'][cn]['withdrawn'] = True
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
        if debug:
            print("Marking day %d division %d has completed" % (day_num, div_num))
        event['completed'][day_num][div_num] = True

    if move is None and all == "" and len(event['pace']) == len(event['crews']) and len(event['div_size'][day_num]) == 1:
        generate_results_by_pace(event, debug)
        move = event['move'][-1]
        back = event['back'][-1]
        div_head = 0
        crew_num = -1
        day_num = event['days']-1

    if move is None:
        return

    if check_results(event, move, back, div_head, debug) == False:
        return

    event['full_set'] = False
    if day_num == event['days']-1 and crew_num == -1:
        if debug:
            print("Completed all divisions & days")
        event['full_set'] = True

    # work out finishing names and blades, etc
    for crew_num in range(len(event['crews'])):
        nc = crew_num;
        gain = 0
        blades = True
        finished = True
        for day in range(event['days']):
            m = event['move'][day][nc]
            if m == None:
                event['crews'][crew_num]['gain'] = None
                finished = False
                break
            
            gain = gain + m

            if m <= 0 or event['skip'][day][nc] == True:
                blades = False
            else:
                # in case this crew went up because of crews withdrawing or not racing that day
                # we need to check that we actually swapped places with another crew
                found = False
                for swap in range(nc-1,-1,-1):
                    if event['skip'][day][swap] == False and event['move'][day][swap] is not None and swap - event['move'][day][swap] > nc - m:
                        # found a crew starting ahead of this crew that crosses over
                        found = True
                        break
                if found is False:
                    blades = False

            nc = nc - m

        if finished:
            # award headship blades to the top crew if we've completed all the racing
            if nc == 0 and event['full_set'] == True and 'skip_headship' not in event['flags']:
                blades = True
        else:
            blades = False

        if event['crews'][crew_num]['withdrawn'] == False:
            event['crews'][crew_num]['gain'] = gain
            event['crews'][crew_num]['blades'] = blades
            event['crews'][nc]['end'] = event['crews'][crew_num]['start']
            

def step_on(event):
    newlist = [None] * len(event['crews'])
    for i in range(len(event['crews'])):
        crew = event['crews'][i]
        if crew['gain'] is not None:
            ep = i - crew['gain']
            if newlist[ep] is None:
                crew['gain'] = None
                crew['blades'] = False
                crew['highlight'] = False
                crew['withdrawn'] = False
                crew['end'] = None
                newlist[ep] = crew

    event['crews'] = newlist

    # reorder crews from the same club in order
    clubs = {}
    for c in event['crews']:
        if c['club'] not in clubs:
            clubs[c['club']] = 1

        c['number'] = clubs[c['club']]
        clubs[c['club']] += 1

        if c['number'] < len(abbreviations.roman):
            c['num_name'] = "%s %s" % (c['club'], abbreviations.roman[c['number']-1])
        else:
            c['num_name'] = "%s %s" % (c['club'], c['number'])

        if c['number'] > 1:
            c['start'] = c['num_name']
        else:
            c['start'] = c['club']

    try:
        year = int(event['year'])
        event['year'] = str(year+1)
    except:
        event['year'] = event['year']+".next"

    del event['move']
    del event['completed']
    del event['skip']
    del event['full_set']
    event['results'] = []

def write_string(event):
    out = ""

    out += "Set,%s\n" % event['set']
    out += "Short,%s\n" % event['short']
    out += "Gender,%s\n" % event['gender']
    out += "Year,%s\n" % event['year']
    if event['days'] != 4:
        out += "Days,%s\n" % event['days']

    out += "\n"

    abbrev = {}
    if event['set'] in abbreviations.sets:
        abbrev = abbreviations.sets[event['set']]

    crew_num = 0
    for div_size in event['div_size'][-1]:
        out += "Division"
        for i in range(div_size):
            crew = event['crews'][crew_num+i]
            found = False
            for p in abbrev:
                if crew['club'] == abbrev[p]['name']:
                    fin = p
                    if crew['number'] > 1:
                        fin += str(crew['number'])
                    out += ",%s" % fin
                    found = True
                    break
            if not found:
                if crew['number'] == 1:
                    out += ",%s" % crew['club']
                else:
                    out += ",%s %s" % (crew['club'], crew['number'])
        out += "\n"
        crew_num += div_size
        
    out += "\n"
    out += "Results\n"
    if len(event['results']) > 0:
        for i in event['results']:
            out += "  %s\n" % i

    return out

def write_file(event, name):
    output = open(name, "w")
    output.write(write_string(event))
    output.close()
