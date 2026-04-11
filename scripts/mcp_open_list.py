import json
import urllib.request
import urllib.error
import os
import pathlib

kb_dir = r'C:\Users\ANTONIOJOSE\GeneXus\KBs\NextTest1'
working_dir = r'C:\Dev\Test\NextTest1'
export_dir = r'C:\Dev\Test\NextTest1\ExportedTransactions'
url = 'http://127.0.0.1:8001/mcp'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}


def parse_mcp_response(resp):
    body = resp.read().decode('utf-8', errors='replace')
    data_lines = [line[len('data:'):].strip() for line in body.splitlines() if line.startswith('data:')]
    if not data_lines:
        raise ValueError(f'No data: lines in response body:\n{body}')
    return json.loads(''.join(data_lines)), resp.getheader('Mcp-Session-Id'), body


def mcp_call(payload, session_id=None):
    req_headers = headers.copy()
    if session_id:
        req_headers['Mcp-Session-Id'] = session_id
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            parsed, session_header, raw = parse_mcp_response(resp)
            print('--- RESPONSE RAW ---')
            print(raw)
            print('--- PARSED ---')
            print(json.dumps(parsed, indent=2, ensure_ascii=True))
            return parsed, session_header
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print('HTTPError', e.code)
        print(body)
        return None, None
    except Exception as e:
        print('ERROR', str(e).encode('utf-8', errors='replace').decode('utf-8'))
        return None, None

print('KB dir exists:', os.path.isdir(kb_dir))
print('Working dir exists:', os.path.isdir(working_dir))

print('initialize...')
init, session_header = mcp_call({
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'initialize',
    'params': {
        'protocolVersion': '2025-03-26',
        'capabilities': {},
        'clientInfo': {'name': 'claude', 'version': '1.0'}
    }
})
print('session_header:', session_header)
if init is None:
    raise SystemExit(1)

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
                'directory': kb_dir
            },
            'currentDirectory': working_dir
        }
    }
}, session_header)
if open_resp is None:
    raise SystemExit(1)

os.makedirs(export_dir, exist_ok=True)
print('export_kb_to_text transactions...')
export_resp, _ = mcp_call({
    'jsonrpc': '2.0',
    'id': 3,
    'method': 'tools/call',
    'params': {
        'name': 'export_kb_to_text',
        'arguments': {
            'request': {'names': ['type:Transaction'], 'rootDirectory': export_dir}
        }
    }
}, session_header)
if export_resp is None:
    raise SystemExit(1)

print('Exported file list:')
for p in sorted(pathlib.Path(export_dir).rglob('*.gx')):
    print(p.relative_to(export_dir))
