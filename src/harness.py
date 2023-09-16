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
    'stats' : False,
    'day_stats' : [],
}

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
    print(" -stats      : Output statistics on position changes per divison, set & day")
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
        state['stats'] = True
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
    if state['stats']:
        stats.get_stats(s, state['day_stats'])

if state['web']:
    output_web(state)
elif len(state['sets']) == 1:
    if state['stepon'] is None:
        draw.write_svg(state['output'], state['sets'][0], state['svg_config'])
    else:
        bumps.step_on(state['sets'][0])
        bumps.write_file(state['sets'][0], state['stepon'])
else:
    draw.write_multi_svg(state['output'], state['sets'], state['svg_config'])

if state['stats']:
    stats.output_days(state['day_stats'])
