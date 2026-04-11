import json
import urllib.request
import urllib.error

url = 'http://127.0.0.1:8001/mcp'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
output_file = r'C:\Dev\Knowledge\GeneXus-MCP-Server-Guide\scripts\mcp_import_produto2_output.txt'


def log(msg):
    print(msg)
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(str(msg) + '\n')


def parse_sse(body):
    lines = [line for line in body.splitlines() if line.startswith('data:')]
    if not lines:
        raise ValueError('No data lines found')
    return json.loads(''.join(line[len('data:'):].strip() for line in lines))


def mcp_call(payload, session_id=None):
    req_headers = headers.copy()
    if session_id:
        req_headers['Mcp-Session-Id'] = session_id
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=req_headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode('utf-8', errors='replace')
        log('--- RAW RESPONSE ---')
        log(body)
        return parse_sse(body), resp.getheader('Mcp-Session-Id')


with open(output_file, 'w', encoding='utf-8') as f:
    f.write('')

log('initialize...')
init, session = mcp_call({
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'initialize',
    'params': {
        'protocolVersion': '2025-03-26',
        'capabilities': {},
        'clientInfo': {'name': 'claude', 'version': '1.0'}
    }
})
print(init)
print('session', session)

print('open_knowledge_base...')
open_resp, _ = mcp_call({
    'jsonrpc': '2.0',
    'id': 2,
    'method': 'tools/call',
    'params': {
        'name': 'open_knowledge_base',
        'arguments': {
            'request': {
                'knowledgeBaseName': 'NextTest1',
                'directory': r'C:\Users\ANTONIOJOSE\GeneXus\KBs\NextTest1'
            },
            'currentDirectory': r'C:\Dev\Test\NextTest1'
        }
    }
}, session)
print(open_resp)

print('validate_kb_text_files...')
validate_resp, _ = mcp_call({
    'jsonrpc': '2.0',
    'id': 3,
    'method': 'tools/call',
    'params': {
        'name': 'validate_kb_text_files',
        'arguments': {
            'request': {
                'names': ['Produto'],
                'rootDirectory': r'C:\Dev\Test\NextTest1\ProntosParaImportacao'
            }
        }
    }
}, session)
print(validate_resp)

print('import_text_to_kb...')
import_resp, _ = mcp_call({
    'jsonrpc': '2.0',
    'id': 4,
    'method': 'tools/call',
    'params': {
        'name': 'import_text_to_kb',
        'arguments': {
            'request': {
                'names': ['Produto'],
                'rootDirectory': r'C:\Dev\Test\NextTest1\ProntosParaImportacao'
            }
        }
    }
}, session)
print(import_resp)
