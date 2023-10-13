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
<select id="set" name="set" onChange=selectSet()>
<option value="none">Select set of bumps</option>""")

years = []
pair = False
first_index = None
last_index = None
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

if fullpage:
    print("""</select>""")


if 'start' in args and len(years) > 0:
    first_index = get_index(years, args['start'][0])

if 'stop' in args and len(years) > 0:
    last_index = get_index(years, args['stop'][0])

if first_index is not None and last_index is not None and last_index < first_index:
    last_index = first_index

if fullpage:
    print("""<select id="start" name="start" onChange=selectStart()>
<option value="none">Select year</option>""")

for i in range(len(years)):
    extra = ""
    if first_index is not None and first_index == i:
        extra = " selected"
    if fullpage:
        print('<option value="%s"%s>%s</option>' % (years[i], extra, years[i]))

if fullpage:
    print('''</select>
<select id="stop" name="stop"%s>
<option value="none">%s</option>''' % (" style=\"display:none\"" if pair is True else "", "Select finish year" if pair is False else "-"))

for i in range(len(years)):
    extra = ""
    if last_index is not None and last_index == i:
        extra = " selected"
    if fullpage and (first_index is None or i >= first_index) and not pair:
        print('<option value="%s"%s>%s</option>' % (years[i], extra, years[i]))

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
if not pair and len(years) > 0 and first_index is not None and last_index is not None:
    valid = True
if pair and len(years) > 0 and first_index is not None:
    valid = True
       
if valid:
    sets = []
    if pair:
        fmt = "/home/mcshane/src/bumps/results/%s%s_%%s.txt" % (rshort[args['set'][0]].lower(), years[first_index])
        for gender in ["women", "men"]:
            set = bumps.read_file(fmt % gender, highlight)
            if set is not None:
                bumps.process_results(set)
                sets.append(set)
    else:
        p = rshort[args['set'][0]].split("-")
        fmt = "/home/mcshane/src/bumps/results/%s%%s_%s.txt" % (p[0].strip().lower(), p[1].strip().lower())
        for i in range(first_index, last_index+1):
            sets.append(bumps.read_file(fmt % years[i], highlight))
            bumps.process_results(sets[-1])

    if 'output' in args and args['output'][0] == 'Show statistics':
        all = {}
        for s in sets:
            stats.get_stats(s, all)
        stats.html_stats(all)
    else:
        if fullpage:
            if pair:
                print("<a download=\"chart.svg\" href=\"archive.py?set=%s&start=%s&highlight=%s&output=Download\">Download this chart</a><p>" % (args['set'][0], years[first_index], hi_value))
            else:
                print("<a download=\"chart.svg\" href=\"archive.py?set=%s&start=%s&stop=%s&highlight=%s&output=Download\">Download this chart</a><p>" % (args['set'][0], years[first_index], years[last_index], hi_value))
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
function selectSet() {
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
            if(all[i+1] == 1) {
                var opt = document.createElement("option");
                opt.innerHTML = "Select finish year";
                opt.value = "none";
                stop.append(opt);
                stop.style.display = "inline-block";
            } else {
                stop.style.display = "none";
            }
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
