def addn(d, k, n, label = None):
    if k in d:
        d[k]['total'] += n
    else:
        d[k] = {'total' : n, 'labels' : []}

    if label is not None:
        d[k]['labels'].append(label)

def get_stats(event, stats):
    if 'years' not in stats:
        stats['years'] = []
    if 'all' not in stats:
        stats['all'] = {'day' : {}, 'set' : {}, 'blades' : 0, 'crews' : {}, 'clubs' : {}}
        addn(stats['all'], 'withdrew', 0)
    if 'club' not in stats:
        stats['club'] = {}

    sall = stats['all']
    club_count = {}
    headships = {}
    stats['years'].append(event['year'])

    for num in range(len(event['crews'])):
        pos = num
        crew = event['crews'][num]
        if crew['club'] not in stats['club']:
            stats['club'][crew['club']] = {'day' : {}, 'set' : {}, 'blades' : 0, 'crews' : {}, 'headships' : {}, 'highest' : {}}
            addn(stats['club'][crew['club']], 'withdrew', 0)
        club = stats['club'][crew['club']]
        addn(club_count, crew['club'], 1)

        for day in range(event['days']):
            m = event['move'][day][pos]
            if m == None:
                addn(sall, 'withdrew', 1, "%s (%s)" % (crew['start'], event['year']))
                addn(club, 'withdrew', 1, "%s (%s)" % (crew['start'], event['year']))
                break

            addn(sall['day'], m, 1, "%s (%s) day %s" % (crew['start'], event['year'], day+1))
            addn(club['day'], m, 1, "%s (%s) day %s" % (crew['start'], event['year'], day+1))
            pos -= m

            if crew['number'] not in club['highest']:
                club['highest'][crew['number']] = {'high' : pos, 'days' : 1, 'run' : 1, 'longest' : 1, 'end' : event['year']}
            else:
                rec = club['highest'][crew['number']]
                if pos < rec['high']:
                    club['highest'][crew['number']] = {'high' : pos, 'days' : 1, 'run' : 1, 'longest' : 1, 'end' : event['year']}
                elif pos == rec['high']:
                    rec['days'] += 1
                    rec['run'] += 1
                    if rec['run'] > rec['longest']:
                        rec['longest'] = rec['run']
                        rec['end'] = event['year']
                else:
                    rec['run'] = 0

        addn(sall['set'], num-pos, 1, "%s (%s)" % (crew['start'], event['year']))
        addn(club['set'], num-pos, 1, "%s (%s)" % (crew['start'], event['year']))

        if crew['number'] not in headships:
            headships[crew['number']] = {'club' : crew['club'], 'num' : pos}
        elif pos < headships[crew['number']]['num']:
            headships[crew['number']]['club'] = crew['club']
            headships[crew['number']]['num'] = pos

        if crew['blades']:
            sall['blades'] += 1
            club['blades'] += 1

    addn(sall['crews'], len(event['crews']), 1, event['year'])
    for club in club_count:
        addn(stats['club'][club]['crews'], club_count[club]['total'], 1, event['year'])
        addn(sall['clubs'], club_count[club]['total'], 1, "%s (%s)" % (club, event['year']))

    for num in headships:
        addn(stats['club'][headships[num]['club']]['headships'], num, 1, event['year'])

def print_k(d, k):
    if len(d[k]['labels']) < 10:
        print(k, d[k]['total'], d[k]['labels'])
    else:
        print(k, d[k]['total'])

def print_d(d, label, rev=True):
    print("\n%s\n" % label)
    for k in sorted(d.keys(), reverse=rev):
        print_k(d, k)

def print_s(s):
    print_d(s['crews'], "Number of crews:")
    print_d(s['day'], "Each day outcome:")
    print_d(s['set'], "Each set outcome:")
    print("\nBlades awarded: %s" % s['blades'])
    if s['withdrew']['total'] > 0:
        print("Crews withdrew:")
        print_k(s, 'withdrew')

def output_stats(stats):
    headships = {}
    for club in stats['club']:
        if 1 in stats['club'][club]['headships']:
            addn(headships, stats['club'][club]['headships'][1]['total'], 1, club)

    print("Stats across %d years, %s to %s" % (len(stats['years']), stats['years'][0], stats['years'][-1]))
    print_d(stats['all']['clubs'], "Crew from each club:")
    print_s(stats['all'])
    print_d(headships, "Number of headships:")

    for club in stats['club']:
        cs = stats['club'][club]
        print("---------------------\n%s" % club)
        print_s(cs)
        print_d(cs['headships'], "Headships:", False)
        print("Highest position for each crew:")
        for num in sorted(cs['highest'].keys()):
            n = cs['highest'][num]
            print("%s Highest %d, total %d days, longest run %d days to %s" % (num, n['high']+1, n['days'], n['longest'], n['end']))
    
