Code and data for representing bumps results
============================================

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


Results file format
===================

The results file format has three sections:
1) metadata about the racin
2) list of crews in each division
3) results from racing

Section 1
---------
A set <keyword>,<value> pairs, one per line.
Of these only Days is optional, it will default to 4 if omitted.

Set,<description of the name of the series of bumps racing>
Short,<short version of the name above>
Gender,<Men|Women>
Year,<year of racing>
Days,<days of racing>

Section 2
---------

One line per division, starting with the word Division, followed by a comma separated list of crew names.
Crew names can be fully written out, or can be short codes.  The relevant short codes are defined in abbreviations.py
There are different sets of abbreviations available depending on the 'Set' name from the metadata.
A short code is the club name, followed by an optional number (if the number is omitted it defaults to 1).

Section 3
---------

This section starts with the keyword 'Results', followed by a set of strings.
The strings are separated by commas or linebreaks, any string starting with a # character is discarded.
The strings contain a set of codes, which are results applied to crews.  Any unrecognised code is discarded.
Results are given for each day in order.
Results for each division are given in reverse order, the lowest division first.
Results for a single division are listed starting with the bottom crew in that division, then proceeding towards the top.
For each division apart from the bottom division, the first result code for that division will be for the sandwich crew.
If there are not enough results for all days of racing then all subsequent divisions are assumed not to have been raced.

Valid result codes:
  r        This crew remained level for the day, likely rowing over.
  u        This crew bumped up one place, and the crew above went down one place.
  o<num>   This crew overbumped up <num> places, exchanging positions with the crew starting <num> places above.
  t        This result terminates the current division, if given at the start of that division it means that division didn't race.
  x        This crew withdraws from racing and will not race any further.  Division size is reduced by one for subsequent days.
  e<num>   This crew goes up <num> places, <num> can be negative for a crew going down.
  v<num>   Similar to above, but that crew will be shown with a lighter line to indicate they didn't race that day.
  w<num>   The next <num> crews all went up by one, the next crew went down <num> places.
  d<1.2.3> The division sizes change for the next day.  Inside literal <> brackets is a dot separated list of division sizes.
  p        The next crew with an e or v code receives a penalty bump after the e/v code has been applied.

For codes u, o & w that indicate the results for multiple crews no further codes need to be included for any of the crews specified.
For ease of reading, codes from each division are typically seperated by a space, results from each day occur on a newline.
