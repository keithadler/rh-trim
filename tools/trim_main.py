"""Main.lean's five theorems need only Statements and Supplements.Kernels.MainTheorems; drop the
other imports that prune.py carried over from the original's MainTheoremsAll. Text only.

usage: trim_main.py FORK_SRC
"""
import os, sys
p = os.path.join(sys.argv[1], 'Main.lean')
t = open(p, encoding='utf-8').read()
open(p, 'w', encoding='utf-8').write(
    'import Statements\nimport Supplements.Kernels.MainTheorems\n\n' + t[t.index('theorem'):])
print('Main.lean imports trimmed')
