import pathlib
kb = pathlib.Path(r'C:\Dev\Test\NextTest1\src')
count = 0
for p in kb.rglob('*.gx'):
    text = p.read_text(encoding='utf-8', errors='replace')
    if 'DataType = ' in text and 'Codigo' in text:
        print('---', p)
        for line in text.splitlines():
            if 'DataType' in line and 'Codigo' in line:
                print(line)
        count += 1
print('TOTAL', count)
