import pathlib
kb = pathlib.Path(r'C:\Dev\Test\NextTest1\src')
for p in kb.rglob('*.gx'):
    text = p.read_text(encoding='utf-8', errors='replace')
    if text.lstrip().startswith('Domain '):
        print('---', p)
        for line in text.splitlines()[:40]:
            print(line)
