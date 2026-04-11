# GeneXus MCP Server Guide

Este repositório reúne o conhecimento sobre o uso do `GeneXus MCP Server`, com foco no que já foi confirmado e no que ainda falta validar.

## Fonte inicial

- [GeneXus for Agents - Installation guide](https://docs.genexus.com/en/wiki?61635,GeneXus+for+Agents+-+Installation+guide)

## Escopo desta documentação

Este material parte do cenário `Windows Native`, foco do guia oficial de instalação.

## Objetivo

- Registrar a definição do servidor
- Registrar a localização exata na máquina
- Concentrar observações, validações e descobertas futuras em um único lugar
- Entender como usar o MCP com ou sem a IDE aberta

## Organização acordada

Este repositório fica como base de conhecimento sobre o `GeneXus MCP Server`.

Há um workspace local separado para testes e artefatos de estudo, em `C:\Dev\Test`.

Este documento registra o estado atual do que já entendemos e o que ainda falta confirmar.

Regra prática:

- aqui ficam as anotações, decisões e explicações em `.md`
- o que vier da KB, o que for exportado e o que for preparado para importação fica no workspace de testes local
- artefatos de estudo não devem ficar misturados com a documentação permanente

## Definição inicial

O `GeneXus MCP Server` é o backend local do `GeneXus Next` para integração com ferramentas e agentes. Na instalação validada, ele é atendido pelo executável `GeneXus.Services.Host.exe`.

`Model Context Protocol (MCP)` é o protocolo que permite a agentes se conectar a servidores que expõem operações controladas.

O guia oficial confirma que o servidor:

- já vem incluído no `GeneXus Next`
- fica disponível quando a IDE está em execução
- também pode ser executado diretamente a partir da pasta `bl`
- está disponível desde `GeneXus Next 2026.01` e `GeneXus 18 Upgrade 15`
- permite, entre outras ações, criar e abrir `Knowledge Bases`, criar ou modificar objetos, definir `rules`, configurar propriedades e importar ou exportar objetos em texto

## Localização no drive

O servidor fica na pasta `bl` da instalação do `GeneXus Next`.

O executável confirmado é `GeneXus.Services.Host.exe`.

Na instalação validada nesta máquina, o caminho absoluto do host é:

`C:\Users\ANTONIOJOSE\AppData\Local\Programs\GeneXus\GeneXus Next\bl\GeneXus.Services.Host.exe`

## Arquivos de apoio

Com base no guia oficial, os arquivos locais mais relevantes para acompanhamento são:

- `GXMBLServices.log`, para monitorar a execução e interação do backend
- `settings.json`, criado por padrão em `bl`
- `settings-overrides.json`, para sobrescrever configurações sem alterar o arquivo padrão

## Conexão com a CLI

O guia oficial mostra que o servidor expõe o endpoint `http://localhost:8001/mcp` e pode ser conectado à CLI compatível com MCP.

## Como iniciar o servidor

O foco principal aqui é conseguir usar o `GeneXus MCP Server` sem depender da IDE aberta, sem excluir o uso misto quando ele fizer sentido.

Pelo guia oficial, existem dois modos úteis:

- iniciar a IDE, o que sobe o servidor automaticamente junto com ela
- iniciar apenas o backend local, executando `GeneXus.Services.Host.exe` a partir da pasta `bl`

### Fluxo operacional recomendado

1. Abrir a instalação do `GeneXus Next`.
2. Entrar na pasta `bl`.
3. Executar `GeneXus.Services.Host.exe`.
4. Confirmar que o servidor respondeu no endpoint padrão.

### Atalhos locais validados

Nesta máquina já existem atalhos no menu Iniciar para subir apenas o host:

- `GENEXUS MCP`, para abrir o host normalmente
- `GENEXUS MCP MIN`, para abrir o host minimizado

Esses atalhos aparecem na busca do Windows e apontam para `GeneXus.Services.Host.exe`.

### Comportamento esperado ao iniciar

Ao abrir o host por atalho ou executando o `.exe` diretamente, é esperado que apareça uma janela de terminal.

Os sinais relevantes de inicialização correta são:

- `GeneXus Services Host started. port:8001`
- `Now listening on: http://localhost:8001`
- `Application started. Press Ctrl+C to shut down.`

Também é normal que a janela mostre logs de carregamento de pacotes e mensagens `404` em endpoints auxiliares de OAuth discovery.

A janela precisa permanecer aberta enquanto o servidor estiver em uso.

## Como validar se está ativo

A forma prática de validação é confirmar que o endpoint MCP responde em:

`http://localhost:8001/mcp`

Também faz sentido observar o `GXMBLServices.log`, porque ele registra a execução e a interação do backend.

### Critérios práticos de validação

- o processo do host está em execução
- o endpoint `http://localhost:8001/mcp` responde
- o `GXMBLServices.log` mostra inicialização sem erro de carregamento
- a CLI consegue se conectar ao servidor MCP

### Validação MCP real

O endpoint não responde a um `GET` simples. Ele espera um cliente MCP com `Accept: application/json, text/event-stream`.
Ao usar scripts, cuidado: a resposta pode chegar em SSE com prefixos `event:` e `data:`. Extraia as linhas `data:` e parseie o JSON contido nelas.

Na validação realizada:

- `initialize` respondeu com sucesso
- o servidor devolveu `Mcp-Session-Id`
- `tools/list` retornou as ferramentas GeneXus expostas

Isso confirma que o servidor está funcional como MCP, e não apenas escutando a porta.

Ao trabalhar com `Knowledge Bases`, é importante considerar que a KB aberta fica associada à sessão MCP que executou o `open_knowledge_base`.

Na prática, isso significa que abrir a KB em uma sessão não garante que outra sessão MCP já enxergue o mesmo estado aberto.

## Como registrar no Codex Windows

O Codex local suporta MCP servers externos no arquivo de configuração do usuário. O registro deste servidor usa o alias `gxnext`.

```powershell
codex mcp add gxnext --url http://localhost:8001/mcp
```

## Uso diário

Fluxo mínimo para trabalhar com o `GeneXus MCP Server`:

1. Iniciar o host `GeneXus.Services.Host.exe`.
2. Confirmar que a porta `8001` está aberta.
3. Confirmar o handshake MCP com `initialize`.
4. Usar o servidor no Codex como `gxnext`.

> Dica de ambiente: em scripts locais no Windows, use `python3` sempre que disponível. O comando `python` pode apontar para Python 2 e causar erros de sintaxe ou encoding.

Se o `initialize` falhar com `406`, o problema costuma ser o `Accept` da requisição e não necessariamente o servidor desligado.

Em operações de listagem, `export_kb_to_text` com `listOnly:true` pode concluir com sucesso sem devolver a lista de objetos no payload MCP.

Quando for necessário obter a listagem real de objetos, pode ser necessário exportar da KB para o filesystem de trabalho e ler os artefatos gerados.

## Estado atual

- O `GeneXus MCP Server` pode responder em `http://localhost:8001/mcp`
- O host local é `GeneXus.Services.Host.exe`
- o caminho absoluto validado do host nesta máquina é `C:\Users\ANTONIOJOSE\AppData\Local\Programs\GeneXus\GeneXus Next\bl\GeneXus.Services.Host.exe`
- O servidor pode ser iniciado sem abrir a IDE
- há atalhos locais para abertura normal e minimizada do host
- O log relevante é `GXMBLServices.log`
- `settings.json` e `settings-overrides.json` fazem parte do apoio local

## Termo de trabalho

`Arquivo Textual de Objeto Genexus` significa um arquivo `.gx` que representa textualmente um objeto GeneXus e que pode servir como fonte para leitura, estudo, exportação ou importação no fluxo MCP.

## Workspace de testes

O workspace local para artefatos gerados e exportados é `C:\Dev\Test\NextTest1`. Essa é a pasta oficial de `currentDirectory` para todas as operações MCP com a KB `NextTest1`.

Estrutura interna:

| Subpasta | Uso |
|---|---|
| `ExportadosPeloGenexusMCP\` | Exports feitos via MCP — `Textual` (src/src.ns) e estrutura física |
| `ProntosParaImportacao\` | Objetos validados prontos para `import_text_to_kb` |
| `RascunhosGerados\` | Rascunhos ainda não validados |
| `Exemplos\` | Exemplos de referência |
| `Verify-*\` | Pastas de verificação por objeto |

## Fluxo de build validado

O fluxo completo validado para uma KB com `Transaction` nova é:

1. `open_knowledge_base` com `currentDirectory` apontando para o workspace de testes
2. `import_text_to_kb` com os arquivos `.gx` prontos
3. `build_all` — requer `prefer-offline=true` e `audit=false` no `~/.npmrc`
4. Verificar se o banco de aplicação já existe no LocalDB antes de qualquer operação de banco
5. `create_or_impact_database` com `isCreate: false` se banco existir com dados, `isCreate: true` se não existir
6. Subir a aplicação via `dotnet GxNetCoreStartup.dll` na pasta `NetModel\web\bin`

## `npm install` travando o build

O `build_all` chama `npm install` para os UserControls do GeneXusUnanimo. Sem configuração adequada, esse processo trava indefinidamente.

Solução validada: adicionar ao `~/.npmrc`:

```
prefer-offline=true
```

> **Em avaliação:** `audit=false` também resolve, mas desativa verificações de segurança globalmente. Ainda não confirmado se `prefer-offline=true` sozinho é suficiente — validar no próximo build.

## Pontos em aberto

- A ferramenta `run` do MCP não está funcional nesta versão — declarada no schema mas não implementada. Ver `mcp-tools.md` para detalhes e alternativa.
- Confirmar se `prefer-offline=true` sozinho no `~/.npmrc` é suficiente para evitar o hang do `npm install` no `build_all` (em observação no próximo build)
- `Procedure` nova via MCP — `PrcSaudacao` foi importada com sucesso e está na KB, mas não gerou `.dll` durante o `build_all`. Possível timing issue (build rodou antes da spec processar o novo objeto) ou bug real. Requer novo `build_all` para validar se compila na próxima execução.

## Validações concluídas

- Round-trip de `WebPanel` via MCP: export → edição do `.layout.xml` → import → build → resultado visível no browser ✅
- `textblock` no layout requer `controlName` além de `name` — sem ele o import falha ✅
- Encerrar o web app antes de buildar — processo segura `.dll` em `NetModel\web\bin\` ✅
- `Folder` é tipo de objeto GeneXus criável via `import_text_to_kb` com arquivo de corpo vazio ✅
- Mover objetos entre pastas via MCP não funciona — nem via `Folder` em `#Properties`, nem via subdiretório; exclusivo da IDE ✅
- MCP não tem `delete_object` — objetos importados não podem ser removidos via MCP ✅
- `WorkWith` e `WorkWithDevices` — exportáveis via MCP, mas **não reimportáveis**: o validador rejeita tabs no YAML mesmo em arquivos gerados pelo próprio GeneXus; criação e edição exclusivas da IDE ✅
- `BusinessComponent = true` em `#Properties` exige minúsculo (TOML) — `True` maiúsculo causa erro de parsing ✅
- `&bc.Load(Key)` requer o PK como parâmetro — `Load()` sem parâmetro não é aceito pelo validador ✅
- Round-trip de objetos gerados pelo WorkWithWeb (`WWxxx`, `ViewXxx`, `XxxGeneral`) — são `WebPanel`/`WebComponent` comuns e suportam o fluxo padrão: export → edição do `.layout.xml` → validate → import → build → visível no browser ✅
- Round-trip de código `.main.gx` (não só layout) — editar eventos/rules em WebPanel funciona: `Form.Caption` alterado no Event Start, importado, compilado, mudança refletida no browser ✅
- `execute.xml` pode ficar bloqueado após `build_all`: o GeneXus reporta falha geral, mas o passo `dotnet publish` já ocorreu e os DLLs em `bin\` estão atualizados — a aplicação serve as mudanças corretamente ✅
- Daemons GeneXus (`SpecifierDaemon`, `GeneratorDaemon`, `ResidentBuilderDaemon`) ficam órfãos após fechar a IDE e travam builds via MCP; solução: listar com `Get-WmiObject Win32_Process` e matar os PIDs com `Stop-Process -Force` antes do próximo build ✅
- `WebPanel` novo criado do zero via MCP — arquivo `.webpanel.main.gx` com mínimo de eventos/variables compila e gera DLL funcional ✅
- `build_one` e `compile_object` — **não funcionam** nesta versão do GeneXus; ambas retornam "Erro interno" sem detalhes; use `build_all` como alternativa ❌
