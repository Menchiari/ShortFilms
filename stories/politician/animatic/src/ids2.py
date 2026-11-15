import sys, os, re
scenes = sys.argv[2].split(",") if len(sys.argv) > 2 else None
k, n = map(int, sys.argv[1].split("/"))
ids = []
for f in sorted(os.listdir(".")):
    m = re.match(r"shots_(s\d\d)\.py$", f)
    if not m or (scenes and m.group(1).upper() not in scenes): continue
    ids += re.findall(r"^def (S\d\d_SH\d\d\d)\(", open(f).read(), re.M)
print(" ".join(ids[k::n]))
