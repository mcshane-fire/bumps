#!/bin/python3

import sys, re, re
import abbreviations

def add_div(list, output, abbrev):
    if len(list) == 0:
        return
    output.write("Division")
    for line in list:
        done = 0
        line = line.replace("St.", "St")
        for n in abbrev:
            if line.startswith(abbrev[n]):
                rest = line[len(abbrev[n]):].strip()
                if len(rest) > 0:
                    for p in reversed(range(0, len(abbreviations.roman))):
                        if rest.startswith(abbreviations.roman[p]):
                            n = "%s%d" % (n, p+1)
                            break
                output.write(",%s" % n)
                done = 1
                break

        if done == 0:
            print("Failed %s" % line)
    output.write("\n")

def convert_file(name, outname):
    input = open(name, "r")
    output = open(outname, "w")

    abbrev = {}
    
    p = name.split("/")
    for i in p:
        if i.startswith("lents"):
            output.write("Set,Lent Bumps\n")
            output.write("Short,Lents\n")
            output.write("Year,%d\n" % int(i[5:]))
            abbrev = abbreviations.ccol
        elif i.startswith("mays"):
            output.write("Set,May Bumps\n")
            output.write("Short,Mays\n")
            output.write("Year,%d\n" % int(i[4:]))
            abbrev = abbreviations.ccol
        elif i.startswith("cra"):
            output.write("Set,CRA Bumps\n")
            output.write("Short,CRA\n")
            output.write("Year,%d\n" % int(i[3:]))
            abbrev = abbreviations.ctown

    if name.find("women") >= 0:
        output.write("Gender,Women\n")
    else:
        output.write("Gender,Men\n")

    output.write("\n")

    p = None
    ex0 = []
    ex1 = []
    ex2 = []
    for line in input:
        c = line.count("DIVISION")
        if c > 0:

            add_div(ex0, output, abbrev)
            add_div(ex1, output, abbrev)
            add_div(ex2, output, abbrev)

            ex0 = []
            ex1 = []
            ex2 = []

            p = line.split("D")
            pos = []
            pos.append(len(p[0]))
            pos.append(pos[0] + len(p[1]) + 1)
            if len(p) > 2:
                pos.append(pos[1] + len(p[2]) + 1)
            if len(p) > 3:
                pos.append(pos[2] + len(p[3]) + 1)
            continue

        line = line.strip("\r\n")

        if len(line.split(",")) > 3:
            output.write("Division,%s\n" % line)
            continue

        if p == None or len(line.strip()) == 0:
            continue
            
        if len(pos) == 4:
            ex0.append(line[pos[0]:pos[1]].strip())
            ex1.append(line[pos[1]:pos[2]].strip())
            ex2.append(line[pos[2]:].strip())

        elif len(pos) == 3:
            ex0.append(line[pos[0]:pos[1]].strip())
            ex1.append(line[pos[1]:].strip())

        elif len(pos) == 2:
            ex0.append(line[pos[0]:].strip())


    add_div(ex0, output, abbrev)
    add_div(ex1, output, abbrev)
    add_div(ex2, output, abbrev)
    output.write("\n")
    output.close()

def print_div(msg, div):
    print(msg)
    for i in range(len(div)):
        if div[i] is None:
            print("%d: [None]" % (i+1))
        else:
            print("%d: %s %s" % (i+1, div[i]['name'], div[i]['results']))
    print("")
    
    
def convert_ad_format(name, outname):
    input = open(name, 'r')
    output = open(outname, 'w')
    debug = False

    title_map = {'TOWN' : ['Town Bumps', 'Town', None],
                 'EIGHTS' : ['Summer Eights', 'Eights', abbreviations.ocol],
                 'TORPIDS' : ['Torpids', 'Torpids', abbreviations.ocol],
                 'MAYS' : ['May Bumps', 'Mays', abbreviations.ccol],
                 'LENTS' : ['Lent Bumps', 'Lents', abbreviations.ccol]}
    
    tpat = re.compile("^([A-Z]*) ([0-9]*)$")
    cpat = re.compile("^ ([0-9]*) *([0-9]*) *([0-9]*) *= NDay, NDiv, NCrew$")
    dpat = re.compile("^ ([0-9]*) *([A-Za-z]*).*$")

    ret = {}
    ret['set'] = None
    ret['days'] = None
    ret['gender'] = None
    ret['crews'] = []
    ret['divisions'] = []
    ret['results'] = []

    divisions = None
    crews = None
    days = None

    div_crews = None
    div_title = None
    abbrev = None

    curdiv = []
    
    for line in input:
        if line == "":
            continue
        if ret['set'] is None:
            m = tpat.match(line)
            if m and m.group(1) in title_map:
                ret['set'] = title_map[m.group(1)][0]
                ret['short'] = title_map[m.group(1)][1]
                ret['year'] = m.group(2);
                abbrev = title_map[m.group(1)][2]
        elif divisions is None:
            m = cpat.match(line)
            if m:
                days = int(m.group(1))
                divisions = int(m.group(2))
                crews = int(m.group(3))
        else:
            m = dpat.match(line)
            if m:
                if len(curdiv) > 0:
                    if len(curdiv) != div_crews:
                        print("Mismatch in division length (advert:%d vs found:%d)" % (div_crews, len(curdiv)))
                    ret['divisions'].append(curdiv)
                    crews -= len(curdiv)
                    curdiv = []
                    
                div_crews = int(m.group(1))
                div_gender = m.group(2)
                if ret['gender'] is None:
                    ret['gender'] = div_gender
                elif ret['gender'] != div_gender:
                    print("Different genders in the same set of results")
            else:
                p = line.strip().split(" ")
                crew = {'results' : []}
                for i in range(days):
                    while p[-1] == '':
                        p.pop()
                    crew['results'].insert(0, int(p.pop()))
                while p[-1] == '':
                    p.pop()
                crew['name'] = ' '.join(p)
                curdiv.append(crew)

    if len(curdiv) != 0:
        if len(curdiv) != div_crews:
            print("Mismatch in division length (advert:%d vs found:%d)" % (div_crews, len(curdiv)))
            return
        ret['divisions'].append(curdiv)
        crews -= len(curdiv)

    if crews != 0:
        print("Mismatch in number of crews found")
        return

    if divisions != len(ret['divisions']):
        print("Mismatch in number of divisions")
        return

    output.write("Set,%s\n" % ret['set'])
    output.write("Short,%s\n" % ret['short'])
    output.write("Gender,%s\n" % ret['gender'])
    output.write("Year,%s\n" % ret['year'])
    if days != 4:
        output.write("Days,%s\n\n" % days)
    else:
        output.write("\n")

    npat = re.compile("^(.*) ([0-9]+)$")

    for div in ret['divisions']:
        s = "Division"
        for c in div:
            out = c['name']
            if abbrev is not None:
                cand = None
                for k in abbrev.keys():
                    if out.startswith(abbrev[k]['name']):
                        if cand is None or len(abbrev[k]['name']) > len(abbrev[cand]['name']):
                            cand = k
                if cand is not None:
                    rest = out[len(abbrev[cand]['name']):].strip()
                    num = ''
                    if len(rest) > 0:
                        num = None
                        for i in range(len(abbreviations.roman)):
                            if rest == abbreviations.roman[i]:
                                num = i+1
                                break

                    if num is not None:
                        out = "%s%s" % (cand, num)
                        c['name'] = out
                else:
                    for i in range(len(abbreviations.roman)):
                        if out.endswith(abbreviations.roman[i]):
                            if cand is None or len(abbreviations.roman[i]) > len(abbreviations.roman[cand]):
                                cand = i
                    if cand is not None:
                        pref = out[:(len(out) - len(abbreviations.roman[cand]))]
                        out = "%s%s" % (pref, cand+1)
                        c['name'] = out
            
            s += ",%s" % out
        output.write("%s\n" % s)

    output.write("\nResults\n")

    cur_day = []
    for div in range(divisions):
        cur_day.append([])
        for c in ret['divisions'][div]:
            cur_day[-1].append(c)
        if div != divisions-1:
            cur_day[-1].append(None) # except for last div, add empty entry for sandwich boat
        
    for day in range(days):
        if debug:
            print("\n\n-------------- DAY %s --------------\n\n" % (day+1))

        next_day = []
        for div in range(divisions):
            next_day.append([None] * len(ret['divisions'][div]))
            if div != divisions-1:
                next_day[-1].append(None) # except for last div, add dummy entry for sandwich boat

        results = ""
        for div in range(divisions-1, -1, -1):
            d = cur_day[div]
            squash = [False] * len(d)
            if debug:
                print_div("Division %d at start of race" % (div+1), d)

            for ci in range(len(d)-1, -1, -1):
                c = d[ci]
                if c is None:
                    print("Missing crew at position %d" % (ci+1))
                    return

                if debug:
                    print("Pos:%d, crew %s, result:%d" % (ci+1, c['name'], c['results'][day]))
                npos = ci - c['results'][day]
                ndiv = div
                tpos = npos
                tdiv = ndiv
                tres = c['results'][day]
                sandwich = False
                if npos < 0:
                    if div == 0:
                        print("Bumping up above headship")
                        return
                    else:
                        ndiv -= 1
                        npos += len(cur_day[ndiv])
                        tpos = 0 # end of the first race they ended up top of that division
                        tres = ci # in the first race they went up ci places
                        # put them in sandwich boat for next division
                        cur_day[div-1][-1] = {'name' : c['name'], 'results' : []}
                        for rd in range(days):
                            cur_day[div-1][-1]['results'].append(c['results'][rd])
                        cur_day[div-1][-1]['results'][day] -= ci
                        if debug:
                            print("\tPromoted to sandwich in div %d (up): %s" % (div, cur_day[div-1][-1]))
                        sandwich = True

                elif npos == 0 and div > 0:
                    # copy crew into sandwich for next division
                    cur_day[div-1][-1] = {'name' : c['name'], 'results' : []}
                    for rd in range(days):
                        cur_day[div-1][-1]['results'].append(c['results'][rd])
                    cur_day[div-1][-1]['results'][day] -= ci
                    if debug:
                        print("\tPromoted to sandwich in div %d (level): %s" % (div, cur_day[div-1][-1]))
                    sandwich = True
                    
                elif npos >= len(d):
                    if div == divisions-1:
                        print("Bumping down below footship")
                        return
                    else:
                        ndiv += 1
                        npos -= len(d)
                        if npos != 0:
                            print("Bumped down below sandwich boat in a single race")
                            return

                if not sandwich:
                    if debug:
                        print("\tEnd of day: %d/%d  End of race: %d/%d" % (ndiv+1, npos+1, tdiv+1, tpos+1))
                    if next_day[ndiv][npos] is not None:
                        print_div("Error, collision in crew: div %d, position %d" % (ndiv+1, npos+1), next_day[ndiv])
                        return
                    else:
                        next_day[ndiv][npos] = c

                # work out whether we need to add a result code
                if not squash[ci]:
                    if tres == 0:
                        results += "r"
                    elif tres == 1 and cur_day[tdiv][tpos]['results'][day] == -1:
                        results += "u"
                        squash[tpos] = True
                    elif tres > 0 and (tres - 1) % 2 == 0 and cur_day[tdiv][tpos]['results'][day] == -tres:
                        results += "o%d" % tres
                        squash[tpos] = True
                    elif tres == 1:
                        j = ci-1
                        # see how many crews went up 1 above
                        # need to cope if the crew starting second went up more than one (bumping from sandwich in the next division)
                        while j > 0 and (cur_day[tdiv][j]['results'][day] == 1 or (j == 1 and cur_day[tdiv][j]['results'][day] > 1)):
                            j -= 1
                        # need the next crew to go down that many places
                        if cur_day[tdiv][j]['results'][day] == j-ci:
                            results += "w%d" % (ci-j)
                            for k in range(j, ci, 1):
                                squash[k] = True
                        else:
                            results += "e1"
                    else:
                        results += "e%d" % (tres)

            if div != divisions-1:
                if next_day[div+1][0] is not None:
                    print_div("Expecting empty slot at head of division %d" % (div+2), next_day[div+1])
                    return

                if debug:
                    print("\tMoving sandwich boat %s back to head of div %d" % (next_day[div][-1]['name'], div))
                next_day[div+1][0] = next_day[div][-1]
                next_day[div][-1] = None

            if debug:
                print("Results: %s" % results)
                results = ""
                print_div("Division %d for next day" % (div+1), next_day[div])
            results += " "

        output.write("%s\n" % results.strip())

        cur_day = next_day


while len(sys.argv) > 0:
    arg = sys.argv.pop(0)

    if arg == '-c':
        src = sys.argv.pop(0)
        dest = sys.argv.pop(0)
        convert_file(src, dest)
    elif arg == '-ad':
        src = sys.argv.pop(0)
        dest = sys.argv.pop(0)
        convert_ad_format(src, dest)
        
