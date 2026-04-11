import pathlib

kb = pathlib.Path(r'C:\Dev\Test\NextTest1')
src = kb / 'src'
print('src exists:', src.exists())
if not src.exists():
    raise SystemExit(1)

matches = []
for p in src.rglob('*transaction*'):
    matches.append(p.relative_to(kb))
print('count:', len(matches))
for p in sorted(matches):
    print(p)
