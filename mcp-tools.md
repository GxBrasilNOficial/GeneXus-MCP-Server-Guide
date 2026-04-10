# GeneXus MCP Server — Ferramentas Disponíveis

## ✅ Como conectar corretamente — leia isso primeiro

Tudo abaixo foi validado em sessão real em 2026-04-09. Houve muita tentativa e erro nessa descoberta. O que está aqui é o que funciona.

### Protocolo correto

```
protocolVersion: "2025-03-26"
```

**Não usar `"2024-11-05"`** — o servidor aceita, mas operações de KB falham silenciosamente.

### Autenticação

**Nenhuma.** Não há Bearer token, não há header especial. Só o `Mcp-Session-Id` retornado pelo `initialize`.

O campo `"IsValid": false` no `settings.json` **não bloqueia operações** — é red herring. Pode ignorar.

### Handshake mínimo funcional

```http
POST http://localhost:8001/mcp
Content-Type: application/json
Accept: application/json, text/event-stream

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"meu-cliente","version":"1.0"}}}
```

Resposta inclui `Mcp-Session-Id` no header. Usar esse ID em todas as chamadas seguintes.

---

## ⚠️ Armadilhas confirmadas em produção

### 1. Escaping de backslash em paths Windows

**É a armadilha mais crítica.** Caminhos Windows têm `\` — em JSON isso precisa ser `\\`. Em Python, usar sempre raw strings:

```python
# CERTO
kb_dir = r"C:\Users\ANTONIOJOSE\GeneXus\KBs\NextTest1"

# ERRADO — SyntaxError ou JSON inválido
kb_dir = "C:\Users\ANTONIOJOSE\GeneXus\KBs\NextTest1"
```

Em curl, `\\\\` no shell vira `\\` no JSON vira `\` no path — qualquer erro nessa cadeia causa `500` silencioso sem aparecer no log.

**Recomendação:** fazer chamadas MCP via Python, não via curl, para evitar o problema de escaping de shell.

### 2. `open_knowledge_base` retorna `Content-Length: 0` via curl

Quando o curl envia JSON com escaping incorreto, o servidor retorna `HTTP 500` com body vazio — sem mensagem de erro, sem log. Parece sucesso mas não é. Confirmar sempre pelo log `GXMBLServices.log`.

### 3. `listOnly: true` não retorna lista no payload MCP

```json
{"result":{"content":[{"type":"text","text":"✓ Export completed successfully"}]}}
```

O flag `listOnly:true` só confirma que completou. A lista de objetos **não vem no payload MCP** — ela só existe no filesystem depois de um export real.

### 4. KB bloqueada pela IDE

Se a KB estiver aberta no GeneXus Next IDE ao mesmo tempo, `open_knowledge_base` via MCP retorna `HTTP 500`. O arquivo `GXLOCK/LOCKS` na pasta da KB indica se há lock ativo. Solução: fechar a KB na IDE antes de operar via MCP.

### 5. Dois servidores MCP sobem quando a IDE está aberta

A IDE inicia seu próprio `GeneXus.Services.Host.exe` — normalmente na porta `8002` — além do standalone na `8001`. São instâncias independentes com estados de sessão separados. Usar sempre a porta do servidor que está ativo (`netstat -ano | grep LISTENING`).

---

## Fluxo operacional correto (Python)

```python
import urllib.request, json

BASE = "http://localhost:8001/mcp"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

def mcp_call(payload, session_id=None):
    h = dict(HEADERS)
    if session_id:
        h["Mcp-Session-Id"] = session_id
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE, data=data, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=90) as r:
        session = r.headers.get("Mcp-Session-Id")
        body = r.read().decode("utf-8", errors="replace")
        return session, r.status, body

# 1. initialize
session, _, _ = mcp_call({
    "jsonrpc":"2.0","id":1,"method":"initialize",
    "params":{"protocolVersion":"2025-03-26","capabilities":{},
              "clientInfo":{"name":"claude","version":"1.0"}}
})

# 2. open KB — currentDirectory deve existir e preferencialmente ter pasta src
_, _, body = mcp_call({
    "jsonrpc":"2.0","id":2,"method":"tools/call",
    "params":{
        "name":"open_knowledge_base",
        "arguments":{
            "request":{
                "knowledgeBaseName":"NextTest1",
                "directory": r"C:\Users\ANTONIOJOSE\GeneXus\KBs\NextTest1"
            },
            "currentDirectory": r"C:\Dev\Test\NextTest1-FullExport"
        }
    }
}, session)

# 3. exportar objetos para filesystem
_, _, body = mcp_call({
    "jsonrpc":"2.0","id":3,"method":"tools/call",
    "params":{
        "name":"export_kb_to_text",
        "arguments":{
            "request":{"names":["[all]"]}
        }
    }
}, session)
```

---

## Comportamento de `open_knowledge_base`

- Se `currentDirectory` **não tem** pasta `src` → exporta todos os objetos da KB para `src/` dentro desse diretório
- Se `currentDirectory` **já tem** pasta `src` → pula o export, só abre a KB
- O `currentDirectory` deve ser um caminho Windows válido e acessível
- A sessão fica vinculada à KB aberta — chamadas de outras sessões não enxergam essa KB

---

## Como validar se a operação chegou ao servidor

Monitorar o log:

```
C:\Users\ANTONIOJOSE\AppData\Local\Programs\GeneXus\GeneXus Next\GXMBLServices.log
```

Se a chamada não aparecer no log, o servidor **não processou** — o problema é no cliente (JSON malformado, path inválido, sessão expirada). O log confirma operações reais como:

```
INFO  == Open Knowledge Base Task:-:Executing Open Knowledge Base Task ended successfully ==
INFO  Exporting 560/560 - Done
INFO  Released 0 locks
```

---

## Como foi obtida esta lista de ferramentas

Via handshake MCP padrão em 2026-04-09:

1. `POST /mcp` com método `initialize` → servidor retornou `Mcp-Session-Id`
2. `POST /mcp` com método `tools/list` → servidor declarou as ferramentas com nome, descrição e schema

Não é conhecimento prévio — foi o servidor respondendo em tempo real.

**Endpoint:** `http://localhost:8001/mcp`

---

## Cobertura do protocolo MCP

| Método | Status |
|---|---|
| `initialize` | ✓ disponível |
| `ping` | ✓ disponível |
| `tools/list` | ✓ disponível |
| `tools/call` | ✓ disponível |
| `tools/get`, `tools/describe`, `tools/schema`, `tools/execute` | ✗ não disponíveis |
| `resources/list`, `resources/read` | ✗ não disponíveis |
| `prompts/list`, `prompts/get` | ✗ não disponíveis |
| `completion/complete` | ✗ não disponível |
| `sampling/createMessage` | ✗ não disponível |

O servidor implementa apenas o mínimo — foco exclusivo em `tools/call`.

---

## Observação sobre lista de KBs

O servidor **não expõe** `list_knowledge_bases`. Para saber quais KBs existem, buscar no filesystem em `C:\Users\ANTONIOJOSE\GeneXus\KBs\`.

---

## Ferramentas por categoria

### Knowledge Base

| Ferramenta | Descrição |
|---|---|
| `create_knowledge_base` | Cria uma nova KB. Só `knowledgeBaseName` é obrigatório. Após criação exporta objetos para `currentDirectory`. |
| `open_knowledge_base` | Abre KB existente. Requer `knowledgeBaseName`, `directory` e `currentDirectory`. |
| `close_knowledge_base` | Fecha a KB aberta. Requer `directory` da KB. |
| `get_kb_property` | Lê o valor de uma propriedade da KB. |
| `set_kb_property` | Define o valor de uma propriedade da KB. |
| `reset_kb_property` | Restaura uma propriedade ao valor padrão. |

### Build e execução

| Ferramenta | Descrição |
|---|---|
| `build_one` | Compila um objeto específico por nome ou GUID. |
| `build_all` | Compila todos os objetos do modelo ativo. |
| `compile_object` | Compila um objeto específico. |
| `run` | Executa a aplicação, com opção de build prévio. |
| `reorganize` | Executa reorganização do banco de dados. |
| `create_or_impact_database` | Cria ou impacta o banco de dados. |

### Exportação e importação de texto (`.gx`)

| Ferramenta | Descrição |
|---|---|
| `export_kb_to_text` | Exporta objetos da KB para arquivos de texto. Suporta `[all]`, nome simples, nome qualificado por módulo e filtro por tipo. |
| `import_text_to_kb` | Importa arquivos de texto de volta para a KB. |
| `validate_kb_text_files` | Valida arquivos `.gx` sem modificar a KB. |

### Knowledge Manager (XPZ)

| Ferramenta | Descrição |
|---|---|
| `export_knowledge_manager` | Exporta dados da KB (equivalente ao Export do Knowledge Manager). Suporta controle de referências, dependências, propriedades e timestamp. |
| `import_knowledge_manager` | Importa dados para a KB. Suporta backup automático, preview mode e controle de conflitos. |

### Módulos

| Ferramenta | Descrição |
|---|---|
| `install_module` | Instala um módulo por nome e opcionalmente por servidor. |
| `update_module` | Atualiza um módulo para versão especificada ou mais recente. |
| `search_modules` | Busca módulos com filtro opcional e servidor. |
| `package_module` | Empacota um módulo para distribuição. |
| `publish_module` | Publica um módulo em um servidor. |
| `restore_module` | Restaura módulos de um pacote ou repositório. |
| `add_modules_server` | Adiciona um servidor de módulos à KB. |

---

## Parâmetros comuns em export/import de texto

`names` suporta:
- `[all]` — processa toda a KB
- `ObjectName` — nome simples
- `QualifiedObjectName` — nome qualificado por módulo
- `type:X` — filtra por tipo
- Separador: `;`

| Parâmetro | Descrição |
|---|---|
| `rootDirectory` | Diretório raiz para saída no filesystem |
| `listOnly` | Executa sem gravar arquivos — mas **não retorna lista no payload**, só confirma conclusão |
| `stopOnError` | Para no primeiro erro |
| `skip` | Pula N objetos (útil para retomar exportações interrompidas) |
| `ignore` | Objetos a excluir do processamento |
