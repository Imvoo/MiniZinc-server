import pymzn

print(pymzn.minizinc("queens.mzn", data={'n':4}, time=30000))
