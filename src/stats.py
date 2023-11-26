def addn(d, k, n, label = None):
    if k in d:
        d[k]['total'] += n
    else:
        d[k] = {'total' : n, 'labels' : []}

    if label is not None:
        d[k]['labels'].append(label)

def get_stats(event, stats):
    if 'set' not in stats:
        stats['set'] = event['set']
    if 'years' not in stats:
        stats['years'] = []
    if 'all' not in stats:
        stats['all'] = {'day' : {}, 'set' : {}, 'blades' : [], 'crews' : {}, 'clubs' : {}}
        addn(stats['all'], 'withdrew', 0)
    if 'club' not in stats:
        stats['club'] = {}
    if 'genders' not in stats:
        stats['genders'] = [event['gender']]
    else:
        if event['gender'] not in stats['genders']:
            stats['genders'].append(event['gender'])

    erec = {'gender' : event['gender'], 'year' : event['year']}
    sall = stats['all']
    club_count = {}
    headships = {}
    if event['year'] not in stats['years']:
        stats['years'].append(event['year'])

    # to get the correct stats when crews withdraw or don't race that day
    # we can't just take the individual move array
    # work out which crews withdraw on each day
    # - all crews below wihtdrawing crews are assumed to actually go up
    #   one less than the move array (or n less for n withdrawn crews above)
    # - all crews crossing over a virtual moving crew need to go up or down
    #   less than the number of virtual crews crossed
    missing = []
    skip = 0
    for day in range(event['days']):
        withdrawn = []
        virtual = []
        for num in range(len(event['crews'])-skip):
            if event['move'][day][num] is None:
                #print("Day %d crew %d withdraws" % (day, num))
                withdrawn.append(num)
                skip += 1
            if event['skip'][day][num] is True:
                #print("Day %d crew %d-%d virtual" % (day, num, num-event['move'][day][num]))
                virtual.append((num, num-event['move'][day][num]))
        missing.append({'withdrawn' : withdrawn, 'virtual' : virtual})

    for num in range(len(event['crews'])):
        pos = num
        crew = event['crews'][num]
        if len(crew['club']) == 0:
            continue
        if crew['club'] not in stats['club']:
            stats['club'][crew['club']] = {'day' : {}, 'set' : {}, 'blades' : [], 'crews' : {}, 'headships' : {}, 'highest' : {}, 'years' : [], 'points' : 0, 'count' : 0}
            stats['club'][crew['club']]['safename'] = ''.join(ch for ch in crew['club'] if ch.isalnum())
            addn(stats['club'][crew['club']], 'withdrew', 0)
        club = stats['club'][crew['club']]
        addn(club_count, crew['club'], 1)
        club['count'] += 1
        if event['year'] not in club['years']:
            club['years'].append(event['year'])


        gained = 0
        for day in range(event['days']):
            crec = {'club' : crew['club'], 'number' : crew['number'], 'gender' : event['gender'], 'day' : day, 'year' : event['year']}
            m = event['move'][day][pos]
            if m == None:
                addn(sall, 'withdrew', 1, crec)
                addn(club, 'withdrew', 1, crec)
                break

            # work out which division this crew was in and whether that division raced
            div_head = 0
            div = 0
            while div < len(event['div_size'][day])-1:
                if pos < div_head + event['div_size'][day][div]:
                    break
                div_head += event['div_size'][day][div]
                div += 1

            div_raced = event['completed'][day][div]
            if div_raced == False and div > 0 and pos == div_head:
                div_raced = event['completed'][day][div-1]

            # add stats if the crew didn't skip this day
            if event['skip'][day][pos] == False and div_raced:
                # work out the actual number of places gained, taking into account crews withdrawing or not racing that day
                adjust = 0
                for n in missing[day]['withdrawn']:
                    # a crew higher up withdraws, so discount one place gained
                    if n < pos:
                        adjust -= 1
                for (s,e) in missing[day]['virtual']:
                    # going up but crossing a virtual crew, so discount one place gained
                    if s < pos and e > pos-m:
                        adjust -= 1
                    # going down but crossing a virtual crew, so add one place gained
                    if s > pos and e < pos-m:
                        adjust += 1

                club['points'] += m + adjust
                if m == 0 and pos == 0:
                    club['points'] += 1

                addn(sall['day'], m + adjust, 1, crec)
                addn(club['day'], m + adjust, 1, crec)
                gained += m+adjust

            pos -= m

            if event['skip'][day][pos] == False:
                # if the division didn't race, then just skip this code, but don't reset any current run
                if div_raced:
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
            else:
                # if the crew didn't race this day then just stop any run that was previously ongoing
                if crew['number'] in club['highest']:
                    club['highest'][crew['number']]['run'] = 0

        crec = {'club' : crew['club'], 'number' : crew['number'], 'gender' : event['gender'], 'year' : event['year']}
        addn(sall['set'], gained, 1, crec)
        addn(club['set'], gained, 1, crec)

        if crew['number'] not in headships:
            headships[crew['number']] = {'club' : crew['club'], 'num' : pos}
        elif pos < headships[crew['number']]['num']:
            headships[crew['number']]['club'] = crew['club']
            headships[crew['number']]['num'] = pos

        if crew['blades']:
            sall['blades'].append(crec)
            club['blades'].append(crec)

    addn(sall['crews'], len(event['crews']), 1, erec)
    for club in club_count:
        addn(stats['club'][club]['crews'], club_count[club]['total'], 1, erec)
        addn(sall['clubs'], club_count[club]['total'], 1, {'club' : club, 'year' : event['year'], 'gender' : event['gender']})

    if 'skip_headship' not in event['flags']:
        for num in headships:
            addn(stats['club'][headships[num]['club']]['headships'], num, 1, erec)

def print_k(conf, d, k, club=None, fmt="%s"):
    out = "<tr><td>"
    out += fmt % k
    out += "<td>%s<td>" % d[k]['total']
    sep = ""
    labels = d[k]['labels']
    if len(labels) > 10:
        sep = "... , "
        labels = labels[-10:]

    for i in labels:
        yr = "" if not conf['years'] or 'year' not in i else " (%s)" % i['year']
        dy = "" if 'day' not in i else " day %d" % (i['day']+1)
        gs = "" if 'gender' not in i or not conf['genders'] else " - %s" % i['gender']
        #cl = "%s " % i['club'] if club is None else ""

        if club is not None:
            out += "%s%c%d%s%s" % (sep, i['gender'][0], i['number'], yr, dy)
        else:
            if 'number' in i:
                out += "%s%s %c%d%s%s" % (sep, i['club'], i['gender'][0], i['number'], yr, dy)
            elif 'club' in i:
                out += "%s%s%s%s" % (sep, i['club'], gs, yr)
            elif conf['genders'] and not conf['years']:
                out += "%s%s" % (sep, i['gender'])
            else:
                out += "%s%s%s" % (sep, i['year'], gs)
        sep = ", "

    print(out)

def print_d(conf, d, label, rev=True, club=None, fmt="%s", col=[]):
    if len(d.keys()) == 0:
        return

    if len(col) == 0:
        col.append("Result")
    if len(col) == 1:
        col.append("Times")
    if len(col) == 2:
        col.append("Details")

    print("\n<h4>%s</h4>\n" % label)
    print("<table>")
    print("<tr><th>%s<th>%s<th>%s" % (col[0], col[1], col[2]))
    for k in sorted(d.keys(), reverse=rev):
        print_k(conf, d, k, club=club, fmt=fmt)
    print("</table>")

def print_l(conf, arr, label, club = None):
    if len(arr) == 0:
        return

    print("<h4>%s: %d</h4>" % (label, len(arr)))

    sep = ""
    out = ""
    if len(arr) > 25:
        arr = arr[-25:]
        sep = "... , "

    for i in arr:
        yr = " (%s)" % i['year'] if conf['years'] else ""
        cl = "%s " % i['club'] if club is None else ""
        out += "%s%s%c%d%s" % (sep, cl, i['gender'][0], i['number'], yr)
        sep = ", "

    print(out)

def print_s(conf, s, club = None):
    print_l(conf, s['blades'], "Blades awarded", club=club)
    print_l(conf, s['withdrew']['labels'], "Crews withdrawn", club=club)
    print_d(conf, s['crews'], "Number of crews:", col=["Crews"])
    print_d(conf, s['set'], "Each set outcome:", club=club, fmt="%+d")
    print_d(conf, s['day'], "Each day outcome:", club=club, fmt="%+d")

def add_rank(rank, stats, name, description, title, val, rev = True):
    rank[name] = {'description' : description}
    rclubs = {}
    for club in stats['club']:
        res = val(stats['club'][club])
        if res is not None:
            rclubs[club] = res
    sclubs = sorted(rclubs.keys(), reverse = rev, key = lambda x : rclubs[x])
    out = "<table><tr><th>Rank<th>Club<th>%s\\\n" % title
    i = 1
    pr = 1
    prev = None
    for club in sclubs:
        if prev is None or prev != rclubs[club]:
            pr = i
        out += "<tr><td>%d<td>%s<td>%s\\\n" % (pr, club, rclubs[club])
        prev = rclubs[club]
        i += 1

    out += "</table>"
    rank[name]['html'] = out

def ord(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, "th")

def generate_ranks(stats):
    rank = {}

    add_rank(rank, stats, '01_crews', 'Crews entered', 'Crews', lambda x : x['count'])
    add_rank(rank, stats, '02_points', 'Pegasus Cup score', 'Score', lambda x : int(12 * x['points'] / x['count']))
    add_rank(rank, stats, '03_headships', 'Headships', 'Number', lambda x : None if 1 not in x['headships'] else x['headships'][1]['total'])
    add_rank(rank, stats, '04_headdays', 'Total days at headship', 'Days', lambda x : None if x['highest'][1]['high'] > 0 else x['highest'][1]['days'])
    add_rank(rank, stats, '05_headlong', 'Continuous days at headship', 'Days', lambda x : None if x['highest'][1]['high'] > 0 else x['highest'][1]['longest'])
    add_rank(rank, stats, '06_blades', 'Blades awarded', 'Number', lambda x : None if len(x['blades']) == 0 else len(x['blades']))
    add_rank(rank, stats, '07_blades_crew', 'Blades per 1000 crews', 'Score', lambda x : None if len(x['blades']) == 0 else int(1000 * len(x['blades']) / x['count']))

    crews = sorted(stats['all']['clubs'].keys())
    for i in crews[1:]:
        add_rank(rank, stats, '1%02d_head' % i, '%s crew headships' % ord(i), 'Number', lambda x : None if i not in x['headships'] else x['headships'][i]['total'])

    for i in crews:
        add_rank(rank, stats, '2%02d_high' % i, '%s crew highest position' % ord(i), 'Position', lambda x : None if i not in x['highest'] else x['highest'][i]['high']+1, False)

    return rank

def output_span(stats, years):
    desc = "%s, " % stats['set']
    if len(stats['genders']) == 1:
        desc += "%s, " % stats['genders'][0]

    uniq = []
    for y in years:
        p = y.split(' ')
        if p[0] not in uniq:
            uniq.append(p[0])
    if len(uniq) == 1:
        return "%s%s" % (desc, uniq[0])
    else:
        return "%sacross %d years: %s to %s</h3>" % (desc, len(uniq), uniq[0], uniq[-1])

def html_stats(stats, initial_tab = None, initial_rank = None):
    conf = {'years' : False, 'genders' : False}
    if len(stats['years']) > 1:
        conf['years'] = True
    if len(stats['genders']) > 1:
        conf['genders'] = True

    headships = {}
    for club in stats['club']:
        if 1 in stats['club'][club]['headships']:
            addn(headships, stats['club'][club]['headships'][1]['total'], 1, {'club' : club})

    sclubs = sorted(stats['club'].keys(), reverse = True, key = lambda x : stats['club'][x]['count'])

    print("""<div class="tab">
  <button %s class="tablinks" onclick="showStats(event, 'all')">All</button>
  <button %s class="tablinks" onclick="showStats(event, 'ranking')">Ranking</button>""" % ("id=\"default\"" if initial_tab is None or initial_tab == 'all' else "", "id=\"default\"" if initial_tab is not None and initial_tab == 'ranking' else ""))

    for club in sclubs:
        extra = ""
        if initial_tab is not None and initial_tab == stats['club'][club]['safename']:
            extra = "id=\"default\""
        print("  <button %s class=\"tablinks\" onclick=\"showStats(event, '%s')\">%s</button>" % (extra, stats['club'][club]['safename'], club))

    print("</div>")

    print("<div id=\"all\" class=\"tabcontent\">")
    ys = sorted(stats['years'])
    print("<h3>Stats for %s</h3>" % output_span(stats, ys))
    print_d(conf, headships, "Number of headships:", col=["Headships","Clubs"])
    print_d(conf, stats['all']['clubs'], "Crews from each club:", col=["Crews","Clubs"])
    print_s(conf, stats['all'])
    print("</div>")

    print("<div id=\"ranking\" class=\"tabcontent\">")
    print("<h3>Club rankings for %s</h3>" % output_span(stats, ys))
    print("<select id=\"rank\" name=\"rank\" onChange=setRanking()>")
    rank = generate_ranks(stats)
    for r in sorted(rank.keys()):
        extra = ""
        if initial_rank == r:
            extra = " selected"
        print("<option value=\"%s\"%s>%s</option>" % (r, extra, rank[r]['description']))
    print("</select><p>")
    print("<div id=\"order\">")
    print("</div>")
    print("</div>")

    for club in sclubs:
        cs = stats['club'][club]
        print("<div id=\"%s\" class=\"tabcontent\">" % cs['safename'])
        ys = sorted(cs['years'])
        print("<h3>%s stats for %s</h3>" % (club, output_span(stats, ys)))
        print_d(conf, cs['headships'], "Headships:", False, col=["Crew"])
        print("<h4>Highest position for each crew:</h4>")
        print("<table>\n<tr><th>Crew<th>Highest position<th>Total days<th>Longest run")
        for num in sorted(cs['highest'].keys()):
            n = cs['highest'][num]
            print("<tr><td>%s<td>%d<td>%d<td>%d days to %s" % (num, n['high']+1, n['days'], n['longest'], n['end']))
        print("</table>")
        print_s(conf, cs, club)
        print("</div>")


    print("""<script language="JavaScript">
function showStats(event, name) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the link that opened the tab
    document.getElementById(name).style.display = "block";
    if (event == null) {
        document.getElementById("default").className += " active";
    }
    else {
        event.currentTarget.className += " active";
    }

    // Update the direct link
    link = document.getElementById("direct");
    const s_regex = /&stats=[^&]*/i;
    link.href = link.href.replace(s_regex, "&stats=" + name);
    const r_regex = /&rank=[^&]*/i;
    link.href = link.href.replace(r_regex, "");

    if (name == 'ranking') {
        setRanking();
    }
}
""")
    for r in sorted(rank.keys()):
        print("var rank_%s = \"%s\";" % (r, rank[r]['html']))

    print("var ranks = [")
    for r in sorted(rank.keys()):
        print("    rank_%s," % r)
    print("    ];")

    print("""
function setRanking() {
    val = document.getElementById("rank");
    document.getElementById("order").innerHTML = ranks[val.selectedIndex];

    // Update the direct link
    link = document.getElementById("direct");
    const regex = /&rank=[^&]*/i;
    if (link.href.match(regex) == null) {
        link.href = link.href + "&rank=" + val.value;
    } else {
        link.href = link.href.replace(regex, "&rank=" + val.value);
    }
}
</script>""")
