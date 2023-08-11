Code and data for representing bumps results
--------------------------------------------

Bumps is a form of rowing competition, traditionally held between colleges at Cambridge
and Oxford Universities.

This repository contains:

LICENSE       License file
src/          Python code for manipulating bumps results
web/          Javascript code for displaying bumps results
results/      Files containing results from different bumps competitions
ox_per_crew/  Per-crew historical results for many Oxford college crews


In the python src directory, these are the user executable files:

./convert.py  Converts between different file formats for representing bumps results
./harness.py  Reads in one or more results file, can output svg format charts

Each will print a usage message when executed with no arguments.
