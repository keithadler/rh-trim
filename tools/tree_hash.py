"""One sha256 for a source tree: each file's relative path and contents, in sorted order.
Two trees with the same hash have byte-identical files.

usage: tree_hash.py DIR
"""
import hashlib, os, sys
root = sys.argv[1]; h = hashlib.sha256(); n = 0
paths = sorted(os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs)
for rel in paths:
    h.update(rel.encode() + b'\0')
    h.update(hashlib.sha256(open(os.path.join(root, rel), 'rb').read()).digest()); n += 1
print(h.hexdigest(), n)
