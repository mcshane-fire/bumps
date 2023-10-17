#web interface to create bumps charts

import sys, os, cgi
import bumps, draw, results, abbreviations
import datetime, string

data = cgi.FieldStorage()

file = None
manual = None

fullpage = True
if 'submit' in data and data['submit'].value == "Just see the chart":
    fullpage = False

if fullpage:
    print("""Content-type: text/html

<html>
<head>
<title>bumps charts creation</title>
<link rel="stylesheet" type="text/css" href="/mcshane.css">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body>
<div class="menu">
<a href="/">Home</a>
<a href="/rowing/">Rowing</a>
<a href="/planes/">Planes</a>
<a href="/bumps/">Bumps</a>
</div>
<div class="content">
<h1>Bumps charts creation</h1>

<form action="create.py" method="post">
<select name="populate">""")

    p = None
    if 'populate' in data:
        p = data['populate'].value.split(",")
        print(p)
    for set in sorted(results.results.keys()):
        for g in ['Men', 'Women']:
            if g in results.results[set]:
                for year in results.results[set][g]:
                    extra = ""
                    if p is not None and p[0] == set and p[1] == g and p[2] == year:
                        extra = "selected"
                    print("<option %s value=\"%s,%s,%s\">%s %s: %s</option>" % (extra, set, g, year, set, g, year))

    print("""</select><input type="submit" value="Populate with archive chart"></form>

<form id="form" action="create.py" method="post">
<textarea rows="20" cols="100" name="text" id="textid">""")

if 'text' in data:
    manual = data['text'].value.replace(">","").replace("<","")
    if fullpage:
        print(manual)

if 'populate' in data:
    p = data['populate'].value.split(",")
    if p[0] in results.results and p[1] in results.results[p[0]] and p[2] in results.results[p[0]][p[1]]:
        try:
            file = "/home/mcshane/src/bumps/results/%s%s_%s.txt" % (p[0].lower(), p[2], p[1].lower())
            if fullpage:
                fp = open(file)
                for line in fp:
                    print(line.strip())
                fp.close()
        except:
            file = None

if fullpage:
    print("""</textarea><p>
<input type="submit" value="Draw chart"><input type="submit" name="submit" value="Just see the chart">
</form>
</div>

<div class="row">
<div class="column">""")

svg_config = {'scale' : 16, 'sep' : 32, 'dash' : 6, 'colours' : False}

set = None
if file is not None:
    set = bumps.read_file(file)
elif manual is not None:
    set = bumps.read_file(None, data = manual)

if not fullpage:
   print("Content-type: svg+xml\n")

if set is not None:
   bumps.process_results(set)
   draw.write_svg(None, set, svg_config)

if fullpage:
    print("""</div>
<div class="column">

<table><tr><th>Code<th>Explanation
<tr><td>r<td>Crew rowed over
<tr><td>u<td>Crew bumped up one
<tr><td>o&lt;num&gt;<td>Crew overbumped &lt;num&gt; places
<tr><td>t<td>Division did not race
<tr><td>x<td>This crew withdraws, division size reduces
<tr><td>e&lt;num&gt;<td>Crew moves up &lt;num&gt; places
<tr><td>v&lt;num&gt;<td>Crew doesn't race, moves up &lt;num&gt; places
<tr><td>w&lt;num&gt;<td>&lt;num&gt; crews go up one, next crew goes down &lt;num&gt;
<tr><td>p<td>Next crew with e or v code gets penalty bump applied
<tr><td>d(1.2.3)<td>Changes division sizes to numbers listed in bracket
</table><p>""")

if fullpage and set is not None and 'set' in set and set['set'] in abbreviations.sets:
    abbrev = abbreviations.sets[set['set']]
    print("<table><tr><th>Code<th>Club")
    for code in sorted(abbrev.keys()):
        print("<tr><td>%s<td>%s" % (code, abbrev[code]['name']))
    print("</table>")

if fullpage:
    print("""</div>
</div>
</body>
</html>""")


