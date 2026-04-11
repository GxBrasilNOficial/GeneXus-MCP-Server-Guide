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

### 5. Schema correto de `open_knowledge_base` — parâmetros dentro de `request`

Os parâmetros `knowledgeBaseName` e `directory` ficam **dentro** do objeto `request`, não no nível raiz do `arguments`. Passar no nível raiz causa `"An error occurred invoking 'open_knowledge_base'"` sem log:

```json
// CERTO
{
  "request": {
    "knowledgeBaseName": "NextTest1",
    "directory": "C:\\Users\\...\\NextTest1"
  },
  "currentDirectory": "C:\\Dev\\Test\\NextTest1"
}

// ERRADO — erro silencioso
{
  "knowledgeBaseName": "NextTest1",
  "directory": "C:\\Users\\...\\NextTest1",
  "currentDirectory": "C:\\Dev\\Test\\NextTest1"
}
```

O mesmo padrão de `request` aninhado vale para todas as ferramentas GeneXus MCP.

### 6. `npm install` trava o `build_all` — solução via `.npmrc`

Durante o `build_all`, o GeneXus chama `npm install` para os UserControls (GeneXusUnanimo). Esse processo trava indefinidamente quando o npm tenta verificar o registry ou rodar `npm audit`.

Solução validada: adicionar ao `~/.npmrc` do usuário:

```
prefer-offline=true
```

Sem isso, o `build_all` nunca completa e precisa ser interrompido manualmente.

> **Em avaliação:** `audit=false` também suprime o hang, mas desativa verificações de segurança globalmente para todos os projetos Node da máquina. Ainda não confirmado se `prefer-offline=true` sozinho é suficiente — o próximo build dirá. Só adicionar `audit=false` se o hang persistir após `prefer-offline=true`, e nesse caso investigar o working dir real do processo npm para colocar o `.npmrc` no lugar certo em vez de desativar globalmente.

### 7. `build_all` pode ter múltiplas instâncias competindo

Chamar `build_all` enquanto outro ainda está rodando (mesmo que travado) faz dois processos competirem pelos mesmos arquivos em `NetModel\web\bin\`, causando `"The process cannot access the file ... because it is being used by another process"`. Verificar se há dotnet/npm pendentes antes de disparar um novo build.

### 8. `WorkWithWeb` — formato real, limitações e como criar via MCP

#### Tipo correto no text format: `WorkWith` (não `WorkWithWeb`)

O objeto raiz de um WorkWith for Web é do tipo `WorkWith` no formato textual — não `WorkWithWeb`. Tentar importar com o keyword `WorkWithWeb` causa:

```
TXP0006: Type WorkWithWeb is invalid
```

#### Localização no export: `src.ns/Patterns/`

O arquivo `.workwith.main.gx` **não fica em `src/`** — fica em `src.ns/Patterns/`:

```
src.ns/Patterns/WorkWithWebGrupoDeProduto.workwith.main.gx
src/GrupoDeProduto/WorkWithWebGrupoDeProduto/WWGrupoDeProduto.webpanel.main.gx
src/GrupoDeProduto/WorkWithWebGrupoDeProduto/ViewGrupoDeProduto.webpanel.main.gx
src/GrupoDeProduto/WorkWithWebGrupoDeProduto/GrupoDeProdutoGeneral.webcomponent.main.gx
```

#### Formato do arquivo `.workwith.main.gx`

O corpo usa sintaxe mista GeneXus + YAML embutido. Contém **GUIDs internos** de atributos e da transaction:

```
WorkWith WorkWithWebGrupoDeProduto
{
    updateTransaction: Apply WW Style
    transaction:
    - transaction: 1db606f2-af09-4cf9-a3b5-b481519d28f6-GrupoDeProduto
    level:
    - id: db348e6d-9938-44d4-82b0-e1428519b353:1
      attributes:
      - attribute: adbb33c9-0906-4971-833c-998de27e0676-GrupoDeProdutoDescricao
    ...
    #Properties
        Name = "WorkWithWebGrupoDeProduto"
    #End
}
```

#### Por que criar via MCP é inviável na prática

O corpo do `.workwith.main.gx` exige os GUIDs internos de cada atributo e da transaction. Esses GUIDs **não aparecem nos arquivos `.gx` exportados normalmente** — só ficam visíveis ao exportar o próprio WorkWith depois de criado pela IDE.

Sem os GUIDs corretos, não é possível montar o arquivo manualmente.

#### Round-trip textual não funciona para WorkWith/WorkWithDevices

O `validate_kb_text_files` e o `import_text_to_kb` rejeitam esses arquivos com:

```
While scanning a plain scalar, found a tab character that violate indentation.
```

**Mesmo arquivos exportados pelo próprio GeneXus falham na validação.** O GeneXus usa tabs no YAML interno desses formatos, mas o parser de importação não aceita tabs.

Conclusão: `WorkWith` e `WorkWithDevices` são **somente exportáveis** — não reimportáveis via MCP.

#### Fluxo correto

1. Criar via IDE: clique direito na Transaction → **Apply Pattern → Work With for Web** (ou WorkWith para devices)
2. Exportar via MCP somente para leitura/referência: `export_kb_to_text` com o nome do WorkWith
3. Os objetos gerados pelo WorkWithWeb (`WWxxx`, `ViewXxx`, `XxxGeneral`) SÃO WebPanels/WebComponents normais — esses suportam round-trip completo via MCP (ver §15)

---

### 8b. `WorkWithDevices` — WorkWith para dispositivos móveis (SD)

O pattern "WorkWith" (para Smart Devices / mobile) gera um objeto de tipo diferente:

| Aspecto | WorkWith for Web | WorkWith (devices) |
|---|---|---|
| Keyword no `.gx` | `WorkWith` | `WorkWithDevices` |
| Extensão do arquivo | `.workwith.main.gx` | `.workwithdevices.main.gx` |
| Localização no export | `src.ns/Patterns/` | `src/<Transaction>/` |
| Objetos gerados separados | Sim (WebPanels + WebComponent) | Não — tudo inline no arquivo |
| Formato interno | YAML + GUIDs de atributos | YAML + XML embutido + GUIDs |

O arquivo `.workwithdevices.main.gx` contém: propriedades do app (Android/iOS/Windows package names, versões), layout inline em YAML, eventos em block scalar YAML, e variáveis padrão em XML literal embutido dentro do YAML.

**Mesma conclusão:** não é possível criar ou reimportar via MCP. Criar pela IDE. O export funciona apenas para leitura/referência.

---

### 9. `Folder` é um tipo de objeto GeneXus — não é diretório Windows

`Folder` é um tipo de objeto registrado na KB, usado para organizar outros objetos hierarquicamente. Pode ser criado via `import_text_to_kb` com um arquivo de corpo vazio:

```
Folder ForaDeUso
{
}
```

Nome do arquivo: `ForaDeUso.folder.main.gx`. O tipo qualificado para `names` é `folder:ForaDeUso`.

**Atenção:** criar o `Folder` na KB e mover objetos para ele são operações separadas. Ver próxima seção.

---

### 10. Mover objetos entre pastas via MCP não funciona

Após criar o `Folder`, não é possível mover objetos para ele via text import. Duas abordagens testadas e confirmadas como ineficazes:

1. **Propriedade `Folder` no `#Properties` do objeto:** o GeneXus valida e importa sem erro, mas ignora a mudança de pasta — o objeto permanece na localização original.
2. **Colocar o arquivo em subdiretório durante o import:** o `rootDirectory` com o arquivo dentro de `ForaDeUso/` não move o objeto já existente.

**Conclusão:** mover objetos entre pastas (Folders) na KB só funciona pela IDE (arrastar ou menu de contexto).

---

### 11. MCP não tem ferramenta de exclusão de objetos

Não existe `delete_object` nem equivalente entre as ferramentas do servidor MCP. Uma vez que um objeto é importado na KB, **não é possível removê-lo via MCP**.

Alternativa parcial: criar um `Folder` com nome indicativo (ex: `ForaDeUso`) e mover o objeto pela IDE.

---

### 12. `BusinessComponent = true` em `#Properties` requer minúsculo (TOML)

A seção `#Properties` usa sintaxe TOML. Valores booleanos em TOML são `true`/`false` minúsculos. Usar `True` com maiúscula causa:

```
TXP0000: (2,21) : error : Unexpected token `True` for a value
```

**Correto:**
```
#Properties
    BusinessComponent = true
#End
```

---

### 13. Dois servidores MCP sobem quando a IDE está aberta

A IDE inicia seu próprio `GeneXus.Services.Host.exe` — normalmente na porta `8002` — além do standalone na `8001`. São instâncias independentes com estados de sessão separados. Usar sempre a porta do servidor que está ativo (`netstat -ano | grep LISTENING`).

### 14. Business Component — `Load()` requer o PK como parâmetro

Em WebPanel, ao usar uma variável de BC para excluir um registro, o método `Load()` **não aceita chamada sem parâmetro**. O GeneXus exige o valor da chave primária diretamente:

```genexus
// CERTO
&GrupoDeProdutoBC.Load(GrupoDeProdutoId)
&GrupoDeProdutoBC.Delete()

// ERRADO — erro de validação: "Load espera pelo menos 1 parâmetros"
&GrupoDeProdutoBC.GrupoDeProdutoId = GrupoDeProdutoId
&GrupoDeProdutoBC.Load()
&GrupoDeProdutoBC.Delete()
```

### 15. Round-trip de objetos gerados pelo WorkWithWeb — confirmado ✅

Os objetos criados pelo pattern Work With for Web (`WWxxx`, `ViewXxx`, `XxxGeneral`) são `WebPanel`/`WebComponent` comuns — **não têm nenhuma restrição especial**. Suportam o round-trip completo via MCP:

1. `export_kb_to_text` com o nome do objeto (ex: `names: ["WWGrupoDeProduto"]`)
2. Editar o `.layout.xml` — ex: corrigir caption, reordenar colunas, alterar classes CSS
3. `validate_kb_text_files` — deve passar sem erros
4. `import_text_to_kb` — importa a versão editada de volta à KB
5. `build_all` (ou `build_one`) — compila; resultado visível no browser imediatamente

Validado em 2026-04-10: alteração do `caption` de `"Grupo De Produtoes"` para `"Grupos de Produto"` no `WWGrupoDeProduto.webpanel.layout.xml`, confirmada no browser via `http://localhost:5000/wwgrupodeproduto.aspx`.

**Observação importante:** o `build_all` pode reportar falha geral por causa do lock no `execute.xml` (ver §16), mas o passo de compilação `.NET` (`dotnet publish`) **sempre é executado antes** e os DLLs são atualizados. A aplicação serve as mudanças corretamente mesmo com o relatório de falha do build.

---

### 16. `execute.xml` fica bloqueado após build — falha reportada, mas DLLs são atualizados

Durante e após o `build_all`, o GeneXus mantém aberto — e às vezes não libera — o arquivo:

```
C:\Users\ANTONIOJOSE\GeneXus\KBs\NextTest1\NetModel\web\execute.xml
```

Quando esse arquivo está bloqueado, o GeneXus reporta o `build_all` como **falho**, mesmo que a compilação `.NET` tenha concluído com sucesso e os DLLs em `NetModel\web\bin\` estejam atualizados.

**Comportamento confirmado:**
- O passo `dotnet publish` ocorre **antes** da gravação do `execute.xml`
- Os DLLs compilados já estão na pasta `bin\` quando o lock ocorre
- A aplicação web iniciada após o build serve as alterações corretamente
- Renomear ou excluir o `execute.xml` não adianta — o GeneXus o recria na próxima execução

**Diagnóstico:**

```powershell
# Verificar se execute.xml está bloqueado
$path = 'C:\Users\ANTONIOJOSE\GeneXus\KBs\NextTest1\NetModel\web\execute.xml'
try {
    $fs = New-Object System.IO.FileStream($path, [System.IO.FileMode]::Open,
          [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    $fs.Close()
    Write-Output 'livre'
} catch {
    Write-Output ("bloqueado: " + $_.Exception.Message)
}
```

**Conclusão prática:** quando o `build_all` reportar falha e o log indicar erro no `execute.xml`, verificar se os DLLs em `bin\` têm timestamp recente. Se sim, o build compilou — a falha é apenas do pós-processamento e pode ser ignorada para fins de teste.

---

### 18. `build_one` e `compile_object` não funcionam — ferramentas quebradas

Ambas as ferramentas de build individual retornam erro interno sem detalhes:

```
"An error occurred invoking 'build_one'."
"An error occurred invoking 'compile_object'."
```

Testado em 2026-04-10:
- `build_one` com `objectName: "WWGrupoDeProduto"` → "Erro interno, saída de dumping"
- `compile_object` com `objectName: "WWGrupoDeProduto"` → erro imediato sem log
- A KB estava aberta e respondendo a outras operações (export, import, build_all)

**Conclusão:** estas ferramentas não estão implementadas ou têm bug grave nesta versão do GeneXus Next. Use `build_all` como alternativa, mesmo que mais lento.

---

### 17. Processos daemon GeneXus ficam órfãos após fechar a IDE

Ao fechar o GeneXus Next IDE, alguns processos filhos **não são encerrados automaticamente**. Eles permanecem em execução, mantêm handles abertos em arquivos da KB (incluindo o `execute.xml` e DLLs em `bin\`) e causam falhas em builds subsequentes via MCP.

**Processos órfãos identificados:**

| Processo | Papel |
|---|---|
| `SpecifierDaemon` | Especificação de objetos |
| `GeneratorDaemon` | Geração de código |
| `ResidentBuilderDaemon` | Build residente / incremental |

Todos filhos do mesmo `GXProcessId` da sessão anterior da IDE. Ficam visíveis via:

```powershell
# Listar instâncias dotnet em execução com linha de comando
$procs = Get-WmiObject Win32_Process -Filter "name='dotnet.exe'"
foreach ($p in $procs) {
    Write-Output ("PID=" + $p.ProcessId + " CMD=" + $p.CommandLine)
}
```

**Solução:** matar os PIDs identificados antes de executar o próximo `build_all`:

```powershell
$ids = @(28936, 7364, 12948, 18496, 17816, 34576, 35796, 34860, 35156)
foreach ($id in $ids) {
    try {
        Stop-Process -Id $id -Force -ErrorAction Stop
        Write-Output ("Encerrado PID " + $id)
    } catch {
        Write-Output ("Nao encontrado PID " + $id)
    }
}
```

**Fluxo recomendado após fechar a IDE:**

1. Executar `find_lock.ps1` (lista processos `dotnet.exe` com linha de comando)
2. Identificar PIDs de `SpecifierDaemon`, `GeneratorDaemon`, `ResidentBuilderDaemon`
3. Encerrar com `Stop-Process -Id <PID> -Force`
4. Confirmar com `check_lock.ps1` que `execute.xml` está livre
5. Disparar o `build_all` via MCP

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
| `create_or_impact_database` | Cria ou impacta o banco de dados. Ver seção abaixo. |

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

---

## ⚠️ `create_or_impact_database` — verificação obrigatória antes de usar

Esta ferramenta pode **apagar todos os dados** do banco de aplicação se usada com `isCreate: true` quando o banco já existe.

**Verificar SEMPRE antes de chamar:**

```powershell
# 1. O banco de aplicação existe?
sqlcmd -S "(localdb)\MSSQLLocalDB" -Q "SELECT name FROM sys.databases WHERE name LIKE 'DB_%'"

# 2. Se existir, tem dados?
sqlcmd -S "(localdb)\MSSQLLocalDB" -d "<nome_do_banco>" -Q "
  SELECT t.name, p.row_count
  FROM sys.tables t
  JOIN sys.dm_db_partition_stats p ON t.object_id = p.object_id
  WHERE p.index_id IN (0,1) AND p.row_count > 0
  ORDER BY p.row_count DESC"
```

**Regra de decisão:**

| Situação | `isCreate` |
|---|---|
| Banco não existe | `true` — cria do zero |
| Banco existe, tabelas vazias | `true` — seguro |
| Banco existe com dados | `false` — apenas reorganiza/impacta, preserva dados |

**Atenção:** build falhou com "Erro na reorganização" **não significa** que o banco não existe. São estados independentes. O banco pode existir e ter dados mesmo que o último build tenha falhado.

---

## `run` via MCP — estado atual

A ferramenta `run` está declarada no schema MCP mas **não está funcional** nesta versão do GeneXus Next. Todos os testes retornam `"An error occurred invoking 'run'"` sem nenhuma entrada no `GXMBLServices.log` — o erro ocorre antes de chegar ao servidor.

Tentativas realizadas sem sucesso:
- Com `objectKey` obtido do banco da KB (`EntityGuid`)
- Com `objectKey` obtido do arquivo `.ari` gerado pelo build (`current_guid`)
- Sem `objectKey`, só com `build: false`
- Com o web app rodando e sem ele rodando

Conclusão: ferramenta prevista para versão futura ou requer condição não documentada.

**Alternativa validada:** subir o web app diretamente via dotnet:

```powershell
cd "C:\Users\ANTONIOJOSE\GeneXus\KBs\NextTest1\NetModel\web\bin"
dotnet GxNetCoreStartup.dll --urls "http://localhost:5000"
```

A aplicação inicia em `http://localhost:5000` e os objetos ficam acessíveis via `http://localhost:5000/<nomeObjeto>.aspx`.

**Importante:** encerrar o web app antes de buildar — o processo segura os `.dll` em `NetModel\web\bin\` e o build falha.

---

## GUID interno de objetos

O `run` requer `objectKey` com o GUID interno do objeto na KB. Esse GUID **não está nos arquivos `.gx` exportados**. Pode ser obtido via:

```powershell
# Consultar diretamente o banco da KB no LocalDB
sqlcmd -S "(localdb)\MSSQLLocalDB" -Q "
  SELECT TOP 1 e.EntityGuid
  FROM [GXKB-NextTest1-0abcb14b-53d1-41c9-a2f2-4f3e91f49636].dbo.Entity e
  JOIN [GXKB-NextTest1-0abcb14b-53d1-41c9-a2f2-4f3e91f49636].dbo.EntityVersion ev
    ON e.EntityLastVersionId = ev.EntityVersionId
  WHERE ev.EntityVersionName = 'GrupoDeProduto' AND e.EntityTypeId = 2"

# Ou via arquivo .ari gerado pelo build:
# NetModel\state\state<genId>_<modelId>_<nomeObjeto>.ari
# Contém: current_guid('<guid>').
```

---

## Round-trip de WebPanel validado

Fluxo completo testado e confirmado em 2026-04-10:

1. `export_kb_to_text` com `names: ["wpOiMundo"]` — gera `wpOiMundo.webpanel.main.gx` e `wpOiMundo.webpanel.layout.xml`
2. Editar o `.layout.xml` adicionando um `textblock`
3. `import_text_to_kb` com `names: ["wpOiMundo"]` — importa de volta para a KB
4. `build_one` com `objectName: "wpOiMundo"` — compila o objeto
5. Subir o web app — mudança visível na tela

**Formato correto do `textblock` no layout:**

```xml
<layout type="Web">
	<view>
		<responsive name="MainTable">
			<row>
				<cell>
					<textblock name="TextBlock1" controlName="TextBlock1" caption="OI MUNDO !" />
				</cell>
			</row>
		</responsive>
	</view>
</layout>
```

**Atenção:** o atributo `controlName` é obrigatório no `textblock`. Sem ele o import falha com:
```
A value is required for the property 'Control Name' in '<textblock>'
```

**Atenção:** antes de buildar, garantir que a aplicação web não está rodando — o processo segura os `.dll` em `NetModel\web\bin\` e o build falha com `MSB3027`. Encerrar o processo antes de buildar.

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
