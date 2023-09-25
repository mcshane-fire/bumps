#web interface to archive results

import os, cgi
import results, bumps, draw, stats

args = {}
if 'REQUEST_URI' in os.environ:
    args = cgi.parse(os.environ['REQUEST_URI'])

short = {}
rshort = {}
for s in results.results:
    short[s] = s.replace(" ","").replace("-","")
    rshort[short[s]] = s

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
<select id="set" name="set" onChange=onChangeHandler()>
<option value="none">Select set of bumps</option>""")

years = []
pair = False
first = None
last = None
highlight = None
for s in sorted(results.results.keys()):
    extra = ""
    if 'set' in args and args['set'][0] == short[s]:
        extra = " selected"
        years = results.results[s]
        if len(s.split(" ")) == 1:
            pair = True
    if fullpage:
        print('<option value="%s"%s>%s</option>' % (short[s], extra, s))

if 'start' in args and args['start'][0] == '-1' and len(years) > 0:
    if 'output' in args and args['output'][0] == 'Show statistics':
        args['start'][0] = str(years[0])
    else:
        args['start'][0] = str(years[-1])
    args['stop'] = [str(years[-1])]

if fullpage:
    print("""</select>
<select id="start" name="start" onChange=selectStart()>
<option value="none">Select year</option>""")

for y in years:
    extra = ""
    if 'start' in args and args['start'][0] == str(y):
        extra = " selected"
        first = y
    if fullpage:
        print('<option value="%s"%s>%s</option>' % (y, extra, y))

if fullpage:
    print('''</select>
<select id="stop" name="stop">
<option value="none">%s</option>''' % ("Select finish year" if pair is False else "-"))

for y in years:
    extra = ""
    if 'stop' in args and args['stop'][0] == str(y):
        extra = " selected"
        last = y
    if fullpage and (first is None or y >= first) and not pair:
        print('<option value="%s"%s>%s</option>' % (y, extra, y))

if fullpage:
    print('''</selection>''')
if 'highlight' in args and len(args['highlight'][0]) > 0:
    highlight = args['highlight'][0]
    hi_value = highlight
else:
    hi_value = "Highlight crews starting with"

if fullpage:
    print('''<input type="text" id="highlight" name="highlight" value="%s">
<input type="submit" name="output" value="Generate chart"><input type="submit" name="output" value="Show statistics">
</form>''' % hi_value)


valid = False
if not pair and len(years) > 0 and first is not None and last is not None and last >= first:
    valid = True
if pair and len(years) > 0 and first is not None:
    valid = True
        
if valid:
    sets = []
    if pair:
        fmt = "/home/mcshane/src/bumps/results/%s%s_%%s.txt" % (rshort[args['set'][0]].lower(), first)
        for gender in ["women", "men"]:
            set = bumps.read_file(fmt % gender, highlight)
            if set is not None:
                bumps.process_results(set)
                sets.append(set)
    else:
        p = rshort[args['set'][0]].split("-")
        fmt = "/home/mcshane/src/bumps/results/%s%%s_%s.txt" % (p[0].strip().lower(), p[1].strip().lower())
        for i in range(years.index(first), years.index(last)+1):
            sets.append(bumps.read_file(fmt % years[i], highlight))
            bumps.process_results(sets[-1])

    if 'output' in args and args['output'][0] == 'Show statistics':
        all = {}
        for s in sets:
                stats.get_stats(s, all)
        stats.html_stats(all)
    else:
        if fullpage:
            print("<a download=\"chart.svg\" href=\"archive.py?set=%s&start=%s&stop=%s&highlight=%s&output=Download\">Download this chart</a><p>" % (args['set'][0], first, last, hi_value))
        else:
            print("Content-type: svg+xml\n")
        svg_config = {'scale' : 16, 'sep' : 32, 'dash' : 6, 'colours' : False}
        if len(sets) == 1:
            draw.write_svg(None, sets[0], svg_config)
        elif pair == True:
            draw.write_pair(None, sets, svg_config)
        else:
            draw.write_multi_svg(None, sets, svg_config)

if fullpage:
    print('''<script language="JavaScript">''')
    for s in results.results:
        print('var %s = %s;' % (short[s], results.results[s]))
    print('var all = [')
    for s in sorted(results.results.keys()):
        print('    "%s", %d, %s,' % (short[s], 1 if len(s.split(" ")) > 1 else 0, short[s]))
    print("""];
function onChangeHandler() {
    set = document.getElementById("set").value;
    for(var i = 0; i<all.length; i+=3) {
        if(set === all[i]) {
            var ys = all[i+2];
            var stop = document.getElementById("stop");
            for(var j = stop.options.length - 1; j >= 0; j--) {
                stop.remove(j);
            }
            for(var j = start.options.length - 1; j > 0; j--) {
                start.remove(j);
            }
            for(var j = 0; j<ys.length; j++) {
                var opt = document.createElement("option");
                opt.innerHTML = ys[j];
                opt.value = ys[j];
                start.append(opt);
            }
            var opt = document.createElement("option");
            if(all[i+1] == 1) {
                opt.innerHTML = "Select finish year";
                opt.value = "none";
            } else {
                opt.innerHTML = "-";
                opt.value = "none";
            }
            stop.append(opt);
        }
     }
}
function selectStart() {
    set = document.getElementById("set").value;
    for(var i = 0; i<all.length; i+=3) {
        if(set === all[i]) {
            var ys = all[i+2];
            var st = document.getElementById("start").value;
            var stop = document.getElementById("stop");
            for(var j = stop.options.length - 1; j > 0; j--) {
                stop.remove(j);
            }
            var found = 0;
            if(all[i+1] == 1) {
                for(var j = 0; j<ys.length; j++) {
                    if(ys[j] == st) {
                        found = 1;
                    }
                    if(found == 1) {
                        var opt = document.createElement("option");
                        opt.innerHTML = ys[j];
                        opt.value = ys[j];
                        stop.append(opt);
                    }
                }
                stop.value = st;
            }
        }
    }
}
</script>
</body>
</html>""")
