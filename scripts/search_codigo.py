import pathlib
kb = pathlib.Path(r'C:\Dev\Test\NextTest1\src')
hits = []
for p in kb.rglob('*.gx'):
    text = p.read_text(encoding='utf-8', errors='replace')
    if 'codigo' in text.lower():
        lines = [line for line in text.splitlines() if 'codigo' in line.lower()]
        hits.append((p, lines))
print('matches:', len(hits))
for p, lines in hits[:50]:
    print('---', p)
    for line in lines:
        print(line)
