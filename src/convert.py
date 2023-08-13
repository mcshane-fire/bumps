#!/bin/python3

import sys, re, os
import abbreviations, escapes

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

def skipped(results, day, div, position):
    if 'skipped' not in results[div][position]:
        return False

    return results[div][position]['skipped'][day]

def generate_from_moves(output, ret, debug):
    output.write("Set,%s\n" % ret['set'])
    output.write("Short,%s\n" % ret['short'])
    output.write("Gender,%s\n" % ret['gender'])
    output.write("Year,%s\n" % ret['year'])
    if ret['days'] != 4:
        output.write("Days,%s\n\n" % ret['days'])
    else:
        output.write("\n")

    npat = re.compile("^(.*) ([0-9]+)$")

    for div in ret['divisions']:
        s = "Division"
        for c in div:
            s += ",%s" % c['name']
        output.write("%s\n" % s)

    output.write("\nResults\n")

    cur_day = []
    for div in range(ret['num_divisions']):
        cur_day.append([])
        for c in ret['divisions'][div]:
            cur_day[-1].append(c)
        if div != ret['num_divisions']-1:
            cur_day[-1].append(None) # except for last div, add empty entry for sandwich boat
        
    for day in range(ret['days']):
        if debug:
            print("\n\n-------------- DAY %s --------------\n\n" % (day+1))

        next_day = []
        for div in range(ret['num_divisions']):
            next_day.append([None] * len(cur_day[div]))

        results = ""
        for div in range(ret['num_divisions']-1, -1, -1):
            d = cur_day[div]
            squash = [False] * len(d)
            if debug:
                print_div("Division %d at start of race" % (div+1), d)

            withdraw = []
                
            for ci in range(len(d)-1, -1, -1):
                c = d[ci]
                if c is None:
                    print("Missing crew at position %d" % (ci+1))
                    return False

                if debug:
                    print("Pos:%d, crew %s, result:%s" % (ci+1, c['name'], c['results'][day]))

                if c['results'][day] is None:
                    # crew withdrew
                    withdraw.append(ci)
                    results += "x"
                    continue
                    
                npos = ci - c['results'][day]
                ndiv = div
                tpos = npos
                tdiv = ndiv
                tres = c['results'][day]
                sandwich = False
                if npos < 0:
                    if div == 0:
                        print("Bumping up above headship")
                        return False
                    else:
                        ndiv -= 1
                        npos += len(cur_day[ndiv])
                        tpos = 0 # end of the first race they ended up top of that division
                        tres = ci # in the first race they went up ci places
                        # put them in sandwich boat for next division
                        cur_day[div-1][-1] = {'name' : c['name'], 'results' : []}
                        for rd in range(ret['days']):
                            cur_day[div-1][-1]['results'].append(c['results'][rd])
                        cur_day[div-1][-1]['results'][day] -= ci
                        if debug:
                            print("\tPromoted to sandwich in div %d (up): %s" % (div, cur_day[div-1][-1]))
                        sandwich = True

                elif npos == 0 and div > 0:
                    # copy crew into sandwich for next division
                    cur_day[div-1][-1] = {'name' : c['name'], 'results' : []}
                    for rd in range(ret['days']):
                        cur_day[div-1][-1]['results'].append(c['results'][rd])
                    cur_day[div-1][-1]['results'][day] -= ci
                    if debug:
                        print("\tPromoted to sandwich in div %d (level): %s" % (div, cur_day[div-1][-1]))
                    sandwich = True
                    
                elif npos >= len(d):
                    if div == ret['num_divisions']-1:
                        print("Bumping down below footship")
                        return False
                    else:
                        ndiv += 1
                        npos -= len(d)
                        if npos != 0:
                            print("Bumped down below sandwich boat in a single race")
                            return False

                if not sandwich:
                    if debug:
                        print("\tEnd of day: %d/%d  End of race: %d/%d" % (ndiv+1, npos+1, tdiv+1, tpos+1))
                    if next_day[ndiv][npos] is not None:
                        print_div("Error, collision in crew: div %d, position %d" % (ndiv+1, npos+1), next_day[ndiv])
                        return False
                    else:
                        next_day[ndiv][npos] = c

                # work out whether we need to add a result code
                if not squash[ci]:
                    if 'skipped' in c and c['skipped'][day]:
                        results += "v%d" % tres
                    elif tres == 0:
                        results += "r"
                    elif tres == 1 and cur_day[tdiv][tpos]['results'][day] == -1 and not skipped(cur_day, day, tdiv, tpos):
                        results += "u"
                        squash[tpos] = True
                    elif tres > 0 and (tres - 1) % 2 == 0 and cur_day[tdiv][tpos]['results'][day] == -tres and not skipped(cur_day, day, tdiv, tpos):
                        results += "o%d" % tres
                        squash[tpos] = True
                    elif tres == 1:
                        j = ci-1
                        # see how many crews went up 1 above
                        # need to cope if the crew starting second went up more than one (bumping from sandwich in the next division)
                        while j > 0 and cur_day[tdiv][j]['results'][day] is not None and (cur_day[tdiv][j]['results'][day] == 1 or (j == 1 and cur_day[tdiv][j]['results'][day] > 1)) and not skipped(cur_day, day, tdiv, j):
                            j -= 1
                        # need the next crew to go down that many places
                        if cur_day[tdiv][j]['results'][day] is not None and cur_day[tdiv][j]['results'][day] == j-ci and not skipped(cur_day, day, tdiv, j):
                            results += "w%d" % (ci-j)
                            for k in range(j, ci, 1):
                                squash[k] = True
                        else:
                            results += "e1"
                    else:
                        results += "e%d" % (tres)

            for ci in withdraw:
                if debug:
                    print("Removing last crew in division for next day due to withdrawal")
                next_day[div].pop(-1)

            if div != ret['num_divisions']-1:
                if next_day[div+1][0] is not None:
                    print_div("Expecting empty slot at head of division %d" % (div+2), next_day[div+1])
                    return False
                if next_day[div][-1] is None:
                    print_div("Expecting to find sandwich boat at bottom of div %d" % (div+1), next_day[div])
                    return False

                if debug:
                    print("\tMoving sandwich boat %s back to head of div %d" % (next_day[div][-1]['name'], div))
                next_day[div+1][0] = next_day[div][-1]
                next_day[div][-1] = None

            if debug:
                print("Results: %s" % results)
                output.write("%s " % results)
                results = ""
                print_div("Division %d for next day" % (div+1), next_day[div])
            else:
                results += " "

        output.write("%s\n" % results.strip())

        if ret['div_size_change'] and day < ret['days']-1:
            line = "d<"
            for i in range(len(next_day)-1):
                next_day[i].insert(-1, next_day[i+1].pop(0))
                line += "%d." % (len(next_day[i])-1)
            line += "%d>" % len(next_day[-1])
            output.write("%s\n" % line)

        cur_day = next_day

    return True

def create_short_name(name, abbrev):
    out = name
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
        else:
            for i in range(len(abbreviations.roman)):
                if out.endswith(abbreviations.roman[i]):
                    if cand is None or len(abbreviations.roman[i]) > len(abbreviations.roman[cand]):
                        cand = i
            if cand is not None:
                pref = out[:(len(out) - len(abbreviations.roman[cand]))]
                out = "%s%s" % (pref, cand+1)
    return out

                        
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
    ret['divisions'] = []
    ret['results'] = []
    ret['num_divisions'] = None
    ret['div_size_change'] = False
    
    crews = None

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

                if ret['short'] == 'Torpids' and int(ret['year']) >= 1960 and int(ret['year']) <= 1979:
                    ret['div_size_change'] = True
                    
        elif ret['num_divisions'] is None:
            m = cpat.match(line)
            if m:
                ret['days'] = int(m.group(1))
                ret['num_divisions'] = int(m.group(2))
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
                for i in range(ret['days']):
                    while p[-1] == '':
                        p.pop()
                    crew['results'].insert(0, int(p.pop()))
                while p[-1] == '':
                    p.pop()
                crew['name'] = create_short_name(' '.join(p), abbrev)
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

    if ret['num_divisions'] != len(ret['divisions']):
        print("Mismatch in number of divisions")
        return

    generate_from_moves(output, ret, debug)

def add_crew_data(all, code, crew, p):
    if len(p) != (p[1] * 2) + 3 and len(p) != (p[1] * 2) + 4 and len(p) != p[1] + 3:
        print("Wrong number of arguments in '%s'" % (p))
        return False

    if p[0] not in all[code]['data']:
        all[code]['data'][p[0]] = {'days' : p[1], 'start' : [], 'crew' : {}}
        for i in range(p[1]+1):
            all[code]['data'][p[0]]['start'].append([])

    b = all[code]['data'][p[0]]
    if b['days'] != p[1]:
        print("Different number of days in %d:%d != %d" % (p[0], b['days'], p[1]))
        return False

    b['crew'][crew] = p[2:]

    withdrawn = False
    for i in range(b['days']+1):
        if withdrawn and p[i+2] != 999:
            print("Withdrawn crew then races in %s:%s" % (filename, line.strip()))
            return False
        elif p[i+2] == 999:
            withdrawn = True
        else:
            while len(b['start'][i]) < p[i+2]:
                b['start'][i].append(None)
            other = b['start'][i][p[i+2]-1]
            if other != None:
                print("Overlapping crews in %s/%s/%d, day %d, position %d, %s and %s" % (all[code]['short'], all[code]['gender'], p[0], i, p[i+2], other, crew))
                print("  %s: %s" % (other, b['crew'][other]))
                print("  %s: %s" % (crew, b['crew'][crew]))
                #return
            b['start'][i][p[i+2]-1] = crew

    return True


def convert_per_crew(source_directory, dest_directory, check_directory):
    pat = re.compile("^([a-z][a-z][a-z][a-z])_([mw])([1-9])([te])\.txt$")

    all = {'me' : {'file' : 'eights%d_men.txt', 'gender' : 'Men', 'set' : 'Summer Eights', 'short' : 'Eights', 'data' : {}},
           'we' : {'file' : 'eights%d_women.txt', 'gender' : 'Women', 'set' : 'Summer Eights', 'short' : 'Eights', 'data' : {}},
           'mt' : {'file' : 'torpids%d_men.txt', 'gender' : 'Men', 'set' : 'Torpids', 'short' : 'Torpids', 'data' : {}},
           'wt' : {'file' : 'torpids%d_women.txt', 'gender' : 'Women', 'set' : 'Torpids', 'short' : 'Torpids', 'data' : {}}}

    coll = {'ball' : 'B',
            'bras' : 'Br',
            'chri' : 'Ch',
            'corp' : 'Co',
            'exet' : 'E',
            'grte' : 'GT',
            'hert' : 'H',
            'jesu' : 'J',
            'kebl' : 'K',
            'lady' : 'LM',
            'lina' : 'L',
            'linc' : 'Lc',
            'magd' : 'Mg',
            'mans' : 'Mf',
            'mert' : 'Mt',
            'newc' : 'N',
            'orie' : 'O',
            'osle' : 'OG',
            'pemb' : 'P',
            'quee' : 'Q',
            'rege' : 'R',
            'sann' : 'SAn',
            'sant' : 'SAt',
            'sben' : 'SB',
            'scat' : 'SC',
            'sedm' : 'SE',
            'shil' : 'SHi',
            'shug' : 'SHu',
            'sjoh' : 'SJ',
            'some' : 'S',
            'spet' : 'SP',
            'trin' : 'T',
            'univ' : 'U',
            'wadh' : 'Wh',
            'wolf' : 'Wf',
            'worc' : 'Wt'}
    
    for filename in os.listdir(source_directory):
        f = os.path.join(source_directory, filename)
        if os.path.isfile(f):
            m = pat.match(filename)
            if m:
                # create two character code for men/women & eights/torpids
                code = "%s%s" % (m.group(2), m.group(4))
                if code in all and m.group(1) in coll:
                    if int(m.group(3)) == 1:
                        crew = coll[m.group(1)]
                    else:
                        crew = "%s%s" % (coll[m.group(1)], m.group(3))
                    fp = open(f, 'r')
                    i = 0
                    next(fp)
                    try:
                        for line in fp:
                            p = line.strip().split()
                            for i in range(len(p)):
                                p[i] = int(p[i])
                            if p[1] == 0:
                                continue
                            if add_crew_data(all, code, crew, p) == False:
                                return

                        fp.close()
                        #print(filename, i, coll[m.group(1)], m.group(3), code)
                    except ValueError:
                        print("Error in converting '%s:%s:%s'" % (filename, line.strip(), p[i]))
                        return

    # add escapes
    for m in escapes.missing:
        #print("Adding escape %s" % m)
        if add_crew_data(all, m['code'], m['name'], m['data']) == False:
            return

    mfp = open("missing.txt", 'w')

    for c in all:
        for y in sorted(all[c]['data'].keys()):
            # if a results file for this set of bumps exists, skip doing anything
            fn = all[c]['file'] % y
            if check_directory != None:
                cf = "%s/%s" % (check_directory, fn)
                if os.path.isfile(cf):
                    continue

            empty = 0
            for d in all[c]['data'][y]['start']:
                ec = 0
                for crew in d:
                    if crew is None:
                        ec += 1
                if ec > empty:
                    empty = ec
                    
            if empty == 0:
                # generate output
                data = all[c]['data'][y]

                ret = {}
                ret['set'] = all[c]['set']
                ret['short'] = all[c]['short']
                ret['gender'] = all[c]['gender']
                ret['year'] = y
                ret['days'] = data['days']
                ret['divisions'] = []
                ret['num_divisions'] = 1
                div_size = [len(data['start'][0])]

                ret['div_size_change'] = False
                if all[c]['short'] == 'Torpids' and y >= 1960 and y <= 1979:
                    ret['div_size_change'] = True
                    
                debug = False

                cw = "%s%d" % (c, y)
                if cw in escapes.div_size:
                    ret['num_divisions'] = len(escapes.div_size[cw])
                    div_size = escapes.div_size[cw]

                curdiv = []
                div_num = 0
                for crew in data['start'][0]:
                    crec = {'name' : crew, 'results' : [], 'skipped' : []}
                    for d in range(data['days']):
                        if data['crew'][crew][d+1] == 999:
                            crec['results'].append(None)
                        else:
                            crec['results'].append(data['crew'][crew][d] - data['crew'][crew][d+1])

                        if len(data['crew'][crew]) >= (2*data['days'])+1 and data['crew'][crew][d+data['days']+1] == -1:
                            crec['skipped'].append(True)
                        else:
                            crec['skipped'].append(False)
                        
                    curdiv.append(crec)
                    if len(curdiv) == div_size[div_num]:
                        div_num += 1
                        ret['divisions'].append(curdiv)
                        curdiv = []

                if len(curdiv) != 0:
                    print("Mismatch in division sizes")
                    return

                if len(ret['divisions']) == 0:
                    print("%s%s has no crews" % (c, y))
                    continue

                if debug:
                    print(c, y, ret)
                    
                fp = open("%s/%s" % (dest_directory, fn), 'w')
                if generate_from_moves(fp, ret, debug) == False:
                    return
                fp.close()
            else:
                print("Missing %d crews in %s/%s/%d" % (empty, all[c]['short'], all[c]['gender'], y))
                data = all[c]['data'][y]

                prefix = [y, data['days']]
                missing = []
                for i in range(empty):
                    missing.append([None] * (data['days']+1))

                for day_num in range(data['days']+1):
                    i = 0
                    crews = data['start'][day_num]
                    for crew_num in range(len(crews)):
                        if crews[crew_num] is None:
                            missing[i][day_num] = crew_num+1
                            i += 1
                            
                for i in range(len(missing)):
                    mfp.write("    {'code' : '%s', 'name' : '', 'data' : " % c)
                    flags = []
                    for day_num in range(data['days'], 0, -1):
                        if missing[i][day_num] is None:
                            missing[i][day_num] = 999
                        else:
                            break
                    
                    for day_num in range(len(missing[i])):
                        if missing[i][day_num] is None:
                            flags.append(-1)
                            missing[i][day_num] = len(data['start'][day_num])+1
                            data['start'][day_num].append("m%d" % i)
                        else:
                            flags.append(0)

                    mfp.write("%s},\n" % (prefix+missing[i]+flags[1:]))
                
                if False and c == 'me' and y == 1851:
                    mx = 0
                    for d in all[c]['data'][y]['start']:
                        if len(d) > mx:
                            mx = len(d)
                    for i in range(mx):
                        ln = "%3d: " % i
                        for d in all[c]['data'][y]['start']:
                            if i < len(d):
                                ln += "%5s" % d[i]
                            else:
                                ln += "     "
                        print(ln)
                    #return
                
    mfp.close()

cmd = sys.argv.pop(0)
if len(sys.argv) == 0:
    print("%s   Usage notes" % cmd)
    print(" -c <src file> <dest file>              : Converts a start order file containing lists of divisions")
    print(" -ad <src file> <dest file>             : Converts an 'ad_format' bumps results file")
    print(" -pc <src dir> <dest dir> [<check dir>] : Reads a set of per-crew files and outputs all valid results files [not in <check dir>]")
    
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
    elif arg == '-pc':
        src = sys.argv.pop(0)
        dest = sys.argv.pop(0)
        if len(sys.argv) > 0:
            cdir = sys.argv.pop(0)
        else:
            cdir = None
        convert_per_crew(src, dest, cdir)
        
