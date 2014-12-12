Garbage_Can_Model ver 4.0
=================

This is the recreation of the Cohen, March and Olsen (1972) Garbage Can Model of
organizational decision making using Python 2.7.6 and numpy

I wanted to recreate the model and rewrite it in Python to better understand how it works.
I don't know Fortran but I managed to use the original code from the Appendix as a guide
in building the model. 

For those interested in how the model works I would point you to the original article first.
You can then use the Python model I created to recreate the original results and play
with the assumptions. Wherever possible I tried to preserve the original names of variables,
vectors and matrices.

You will need numpy, random and xlwt to run the model. At the end you will receive a summary
Excel file (remember to edit the destination for the file). The file contains the 
results of the simulation for each of the combination of parameters (net energy load, energy
distribution, problems-to-choices access matrix, choices-to-decision makers access matrix).

The output has 81 rows, one for each combination of parameters and 18 columns for results,
which are (per number of column)
1. net energy load option
2. energy distribution option
3. problems-to-choices access matrix
4. choices-to-decision makers access matrix
5. mean # of resolutions
6. mean # of oversights
7. mean # of flights
8. mean # of quickies (my addition)
9. mean # of unresolved
10. mean # of problems shifting
11. mean # of active problems
12. mean of problem latency
13. mean # of active decision makers
14. mean # of shifts for decision makers
15. mean energy spent
16. mean excess energy
17. mean # of unresolved choices
18. mean # of active choices
