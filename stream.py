#streaming
#!/usr/bin/env python3
from subprocess import Popen, PIPE

with Popen(["MiniZinc", "test.mzn", "-a"], stdout=PIPE, bufsize=1, universal_newlines=True) as p:
    for line in p.stdout:
        print(line, end='')