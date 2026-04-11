import pathlib

wd = pathlib.Path(r'C:\Dev\Test\NextTest1')
print('workdir exists:', wd.exists())
print('src exists:', (wd / 'src').exists())
print('src.ns exists:', (wd / 'src.ns').exists())

src = wd / 'src'
if src.exists():
    entries = sorted(src.rglob('*'))
    print('src entries count:', len(entries))
    for p in entries[:200]:
        print(p.relative_to(wd))
else:
    print('src folder missing')
