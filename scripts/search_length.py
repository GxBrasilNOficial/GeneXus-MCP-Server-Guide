import pathlib
kb = pathlib.Path(r'C:\Dev\Test\NextTest1\src')
for p in kb.rglob('*.gx'):
    text = p.read_text(encoding='utf-8', errors='replace')
    if 'Length =' in text:
        print('---', p)
        for line in text.splitlines():
            if 'Length =' in line:
                print(line)
