#!/bin/python3

import sys
import bumps, stats, draw

state = {
    'sets' : [],
    'highlight' : None,
    'readstdin' : False,
    'web' : False,
    'output' : None,
    'stepon' : None,
    'svg_config' : {'scale' : 16,
                    'sep' : 32, #scale*2
                    'dash' : 6,
                    'colours' : False},
    'stats' : None,
}

def join_stats(event1, event2):
    diffs = {}

    for num2 in range(len(event2['crews'])):
        found = False
        for num1 in range(len(event1['crews'])):
            if event2['crews'][num2]['start'] == event1['crews'][num1]['end']:
                found = True
                d = num1 - num2
                if d < 0:
                    d = -d

                d = int(d / (int(num2/10)+1))

                if d not in diffs:
                    diffs[d] = 0
                diffs[d] += 1
                break

    total = 0
    count = 0
    for d in diffs:
        count += diffs[d]
        total += d * diffs[d]

    if count > 10 and total / count > 0.5:
        print("Warning: %s->%s: %.3f %s" % (event1['year'], event2['year'], total / count, diffs))

def output_web(state):
    series = {}
    for s in state['sets']:
        name = "%s - %s" % (s['short'], s['gender'])
        if name not in series:
            series[name] = []
        series[name].append(s['year'])
        
    print("# results currently available\n")
    print("results = {")
    for s in sorted(series.keys()):
        print("    '%s' : %s," % (s, sorted(series[s])))
    print("}")

cmd = sys.argv.pop(0)
if len(sys.argv) == 0:
    print("%s   Usage notes" % cmd)
    print(" -c          : Enables per-club colours in results lines")
    print(" -r          : Enables reading results from stdin")
    print(" -h <prefix> : Enables highlights for crews with names starting with <prefix>")
    print(" -w <file>   : Writes svg output to <file>")
    print(" -s <file>   : Writes template for next year into <file>")
    print(" -stats      : Output statistics")
    print(" -web        : Output python summary of all results files")
    print(" Any additional arguments are treated as files containing results to be read in")
    sys.exit()

while len(sys.argv) > 0:
    arg = sys.argv.pop(0)
    
    if arg == '-c':
        state['svg_config']['colours'] = True
    elif arg == '-r':
        state['readstdin'] = True
    elif arg == '-h':
        state['highlight'] = sys.argv.pop(0)
    elif arg == '-w':
        state['output'] = sys.argv.pop(0)
    elif arg == '-s':
        state['stepon'] = sys.argv.pop(0)
    elif arg == '-stats':
        state['stats'] = {}
    elif arg == '-web':
        state['web'] = True
    else:
        sys.argv.insert(0, arg)
        break

while len(sys.argv) > 0:
    s = bumps.read_file(sys.argv.pop(0), state['highlight'])
    if s is not None:
        state['sets'].append(s)

if state['readstdin']:
    s = bumps.read_file(None, state['highlight'])
    if s is not None:
        state['sets'].append(s)

for s in state['sets']:
    bumps.process_results(s)
    if state['stats'] is not None:
        stats.get_stats(s, state['stats'])

for i in range(len(state['sets'])-1):
    join_stats(state['sets'][i], state['sets'][i+1])

if state['web']:
    output_web(state)
elif len(state['sets']) == 1:
    if state['stepon'] is None:
        draw.write_svg(state['output'], state['sets'][0], state['svg_config'])
    else:
        bumps.step_on(state['sets'][0])
        bumps.write_file(state['sets'][0], state['stepon'])
elif len(state['sets']) == 2 and state['sets'][0]['set'] == state['sets'][1]['set'] and state['sets'][0]['year'] == state['sets'][1]['year'] and state['sets'][0]['gender'] != state['sets'][1]['gender']:
    draw.write_pair(state['output'], state['sets'], state['svg_config'])
elif len(state['sets']) > 1:
    draw.write_multi_svg(state['output'], state['sets'], state['svg_config'])

if state['stats'] is not None:
    stats.html_stats(state['stats'])
