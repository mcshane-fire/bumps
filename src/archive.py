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
first = None
last = None
highlight = None
for s in sorted(results.results.keys()):
	extra = ""
	if 'set' in args and args['set'][0] == short[s]:
		extra = " selected"
		years = results.results[s]
	print('<option value="%s"%s>%s</option>' % (short[s], extra, s))

if 'start' in args and args['start'][0] == '-1' and len(years) > 0:
	if 'output' in args and args['output'][0] == 'Show statistics':
		args['start'][0] = str(years[0])
	else:
		args['start'][0] = str(years[-1])
	args['stop'] = [str(years[-1])]

print("""</select>
<select id="start" name="start" onChange=selectStart()>
<option value="none">Select year</option>""")
for y in years:
	extra = ""
	if 'start' in args and args['start'][0] == str(y):
		extra = " selected"
		first = y
	print('<option value="%s"%s>%s</option>' % (y, extra, y))
print('''</select>
<select id="stop" name="stop">
<option value="none">Select finish year</option>''')
for y in years:
	extra = ""
	if 'stop' in args and args['stop'][0] == str(y):
		extra = " selected"
		last = y
	if first is None or y >= first:
		print('<option value="%s"%s>%s</option>' % (y, extra, y))
print('''</selection>''')
if 'highlight' in args and len(args['highlight'][0]) > 0:
	highlight = args['highlight'][0]
	hi_value = highlight
else:
	hi_value = "Highlight crews starting with"

print('''<input type="text" id="highlight" name="highlight" value="%s">
<input type="submit" name="output" value="Generate chart"><input type="submit" name="output" value="Show statistics">
</form>''' % hi_value)


if len(years) > 0 and first is not None and last is not None and last >= first:
	sets = []
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
		svg_config = {'scale' : 16, 'sep' : 32, 'dash' : 6, 'colours' : False}
		if len(sets) == 1:
			draw.write_svg(None, sets[0], svg_config)
		else:
			draw.write_multi_svg(None, sets, svg_config)

print('''<script language="JavaScript">''')
for s in results.results:
	print('var %s = %s;' % (short[s], results.results[s]))
print('var all = [')
for s in sorted(results.results.keys()):
	print('    "%s", %s,' % (short[s], short[s]))
print("""];
function onChangeHandler() {
    set = document.getElementById("set").value;
    for(var i = 0; i<all.length; i+=2) {
        if(set === all[i]) {
            var ys = all[i+1];
            var stop = document.getElementById("stop");
            for(var j = stop.options.length - 1; j > 0; j--) {
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
        }
     }
}
function selectStart() {
    set = document.getElementById("set").value;
    for(var i = 0; i<all.length; i+=2) {
        if(set === all[i]) {
            var ys = all[i+1];
            var st = document.getElementById("start").value;
            var stop = document.getElementById("stop");
            for(var j = stop.options.length - 1; j > 0; j--) {
                stop.remove(j);
            }
            var found = 0;
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
</script>
</body>
</html>""")
