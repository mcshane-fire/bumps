#web interface to archive results

import os, cgi
import results, bumps, draw, stats

# return index of arg within years array
# supports exact match
#  or number equal to 0 (meaning first on the list)
#  or negative index (meaning backwards from the end of the list)
def get_index(years, arg):
    index = None
    try:
        index = years.index(arg)
    except:
        try:
            index = int(arg)
            if index < 0:
                if index < -len(years):
                    index = 0
                else:
                    index += len(years)
            elif index != 0:
                index = None
        except:
            index = None
    return index

args = {}
if 'REQUEST_URI' in os.environ:
    args = cgi.parse(os.environ['REQUEST_URI'])

fullpage = True
if 'output' in args and args['output'][0] == 'Download':
    fullpage = False

if fullpage:
    print("""Content-type: text/html

<html>
<head>
<title>bumps charts archive</title>
<link rel="stylesheet" type="text/css" href="/mcshane.css">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body onload="showStats(null, 'all')">
<div class="menu">
<a href="/">Home</a>
<a href="/rowing/">Rowing</a>
<a href="/planes/">Planes</a>
<a href="/bumps/">Bumps</a>
</div>
<div class="content">
<h1>Bumps charts archive</h1>
<form action="archive.py" method="get">
<select id="set" name="set" onChange=selectSet()>
<option value="none">Select set of bumps</option>""")

set = None
gender = None
years = []
first_index = None
last_index = None
highlight = None

for s in sorted(results.results.keys()):
    extra = ""
    if 'set' in args and args['set'][0] == s:
        extra = " selected"
        set = s
    if fullpage:
        print('<option value="%s"%s>%s</option>' % (s, extra, s))

if fullpage:
    print("""</select>
<select id="gender" name="gender" %s onChange=selectGender()>
<option value="none">Select display</option>""" % ("style=\"display:none\"" if set is None else ""))

if set is not None:
    gdisp = {'Men' : 'Men - multiple years',
             'Women' : 'Women - multiple years',
             'all' : 'Single year'}
    for g in sorted(results.results[set].keys()):
        extra = ""
        if 'gender' in args and args['gender'][0] == g:
            extra = " selected"
            gender = g
            years = results.results[set][gender]
        if fullpage:
            text = g
            if g in gdisp:
                text = gdisp[g]
            print('<option value="%s"%s>%s</option>' % (g, extra, text))

if fullpage:
    print("""</select>""")

if 'start' in args and len(years) > 0:
    first_index = get_index(years, args['start'][0])

if 'stop' in args and len(years) > 0:
    last_index = get_index(years, args['stop'][0])

if first_index is not None and last_index is not None and last_index < first_index:
    last_index = first_index
elif first_index is not None and 'stop' not in args and gender != 'all':
    last_index = len(years)-1

valid = False
if gender != 'all' and len(years) > 0 and first_index is not None and last_index is not None:
    valid = True
if gender == 'all' and len(years) > 0 and first_index is not None:
    valid = True

if fullpage:
    print("""<select id="start" name="start" %s onChange=selectStart()>
<option value="none">Select year</option>""" % ("style=\"display:none\"" if gender is None else ""))

for i in range(len(years)):
    extra = ""
    if first_index is not None and first_index == i:
        extra = " selected"
    if fullpage:
        print('<option value="%s"%s>%s</option>' % (years[i], extra, years[i]))

if fullpage:
    print('''</select>
<select id="stop" name="stop"%s onChange=selectStop()>
<option value="none">Select finish year</option>''' % (" style=\"display:none\"" if gender == 'all' or gender is None else ""))

for i in range(len(years)):
    extra = ""
    if last_index is not None and last_index == i:
        extra = " selected"
    if fullpage and (first_index is None or i >= first_index) and gender != 'all':
        print('<option value="%s"%s>%s</option>' % (years[i], extra, years[i]))

if fullpage:
    print('''</selection>''')
if 'highlight' in args and len(args['highlight'][0]) > 0:
    highlight = args['highlight'][0]
    hi_value = highlight
else:
    hi_value = "Highlight crews starting with"

if fullpage:
    disp = "" if valid else "style=\"display:none\""
    print('''<input type="text" id="highlight" name="highlight" %s value="%s">
<input type="submit" id="generate" name="output" %s value="Generate chart"><input type="submit" id="stats" name="output" %s value="Show statistics">
</form>''' % (disp, hi_value, disp, disp))

if valid:
    sets = []
    if gender == 'all':
        fmt = "/home/mcshane/src/bumps/results/%s%s_%%s.txt" % (set.lower(), years[first_index])
        for g in ["women", "men"]:
            s = bumps.read_file(fmt % g, highlight)
            if s is not None:
                bumps.process_results(s)
                sets.append(s)
    else:
        fmt = "/home/mcshane/src/bumps/results/%s%%s_%s.txt" % (set.lower(), gender.lower())
        for i in range(first_index, last_index+1):
            s = bumps.read_file(fmt % years[i], highlight)
            if s is not None:
                bumps.process_results(s)
                sets.append(s)

    if 'output' in args and args['output'][0] == 'Show statistics':
        all = {}
        for s in sets:
            stats.get_stats(s, all)
        stats.html_stats(all)
    else:
        if fullpage:
            if gender == 'all':
                print("<a download=\"chart.svg\" href=\"archive.py?set=%s&gender=%s&start=%s&highlight=%s&output=Download\">Download this chart</a><p>" % (set, gender, years[first_index], hi_value))
            else:
                print("<a download=\"chart.svg\" href=\"archive.py?set=%s&gender=%s&start=%s&stop=%s&highlight=%s&output=Download\">Download this chart</a><p>" % (set, gender, years[first_index], years[last_index], hi_value))
        else:
            print("Content-type: svg+xml\n")
        svg_config = {'scale' : 16, 'sep' : 32, 'dash' : 6, 'colours' : False}
        if len(sets) == 1:
            draw.write_svg(None, sets[0], svg_config)
        elif gender == 'all':
            draw.write_pair(None, sets, svg_config)
        else:
            draw.write_multi_svg(None, sets, svg_config)

if fullpage:
    print('''<script language="JavaScript">''')
    for s in results.results:
        for g in results.results[s]:
            print('var %s_%s = %s;' % (s, g, results.results[s][g]))
    print('var all = [')
    for s in sorted(results.results.keys()):
        for g in sorted(results.results[s].keys()):
            print('    "%s", "%s", %s_%s,' % (s, g, s, g))
    print("""];
function clearHide(name) {
    var input = document.getElementById(name);
    for(var j = input.options.length - 1; j > 0; j--) {
       input.remove(j);
    }
    input.style.display = "none";
}

function hide(name) {
    var input = document.getElementById(name);
    input.style.display = "none";
}

function show(name) {
    var input = document.getElementById(name);
    input.style.display = "inline-block";
}

function selectSet() {
    set = document.getElementById("set").value;
    clearHide("gender");
    clearHide("start");
    clearHide("stop");

    hide("highlight");
    hide("generate");
    hide("stats");

    for(var i = 0; i<all.length; i+=3) {
        if(set === all[i]) {
            var opt = document.createElement("option");
            if(all[i+1] == 'all') {
                opt.innerHTML = 'Single year';
            } else {
                opt.innerHTML = all[i+1] + " - multiple years";
            }
            opt.value = all[i+1];
            gender.append(opt);
            gender.style.display = "inline-block";
        }
    }
}
function selectGender() {
    clearHide("start");
    clearHide("stop");
    hide("highlight");
    hide("generate");
    hide("stats");

    var set = document.getElementById("set").value;
    var gender = document.getElementById("gender").value;

    for(var i = 0; i<all.length; i+=3) {
        if(set === all[i] && gender === all[i+1]) {
            var years = all[i+2];
            var start = document.getElementById("start");

            for(var j = 0; j<years.length; j++) {
                var opt = document.createElement("option");
                opt.innerHTML = years[j];
                opt.value = years[j];
                start.append(opt);
            }
            if(gender == 'all') {
                start.options[0].innerHTML = 'Select year';
            } else {
                start.options[0].innerHTML = 'Select start year';
            }
            start.style.display = "inline-block";
        }
    }
}

function selectStart() {
    var gender = document.getElementById("gender").value;

    if(gender !== "all") {
        clearHide("stop");
        hide("highlight");
        hide("generate");
        hide("stats");
        var set = document.getElementById("set").value;
        var start = document.getElementById("start").value;

        for(var i = 0; i<all.length; i+=3) {
            if(set === all[i] && gender === all[i+1]) {
                var years = all[i+2];
                var stop = document.getElementById("stop");
                var found = 0;
                for(var j = 0; j<years.length; j++) {
                    if(years[j] === start) {
                        found = 1;
                    }
                    if(found == 1) {
                        var opt = document.createElement("option");
                        opt.innerHTML = years[j];
                        opt.value = years[j];
                        stop.append(opt);
                    }
                }
                if(found == 1) {
                    stop.style.display = "inline-block";
                }
            }
        }
    }
    else {
        show("highlight");
        show("generate");
        show("stats");
    }
}

function selectStop() {
    var stop = document.getElementById("stop").value;
    if(stop === 'none') {
        hide("highlight");
        hide("generate");
        hide("stats");
    }
    else {
        show("highlight");
        show("generate");
        show("stats");
    }
}
</script>
</body>
</html>""")
