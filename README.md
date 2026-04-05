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

Há um workspace local separado para testes e artefatos de estudo.

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

Mais tarde, isso pode virar um atalho ou fluxo direto para abrir só o servidor.

### Fluxo operacional recomendado

1. Abrir a instalação do `GeneXus Next`.
2. Entrar na pasta `bl`.
3. Executar `GeneXus.Services.Host.exe`.
4. Confirmar que o servidor respondeu no endpoint padrão.

### Atalho no desktop

Como a intenção é poder usar o servidor com ou sem a IDE, faz sentido considerar um atalho no desktop que aponte diretamente para `GeneXus.Services.Host.exe`.

Esse atalho pode servir como entrada rápida para iniciar apenas o backend local, sem passar pela interface do `GeneXus Next`.

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

Na validação realizada:

- `initialize` respondeu com sucesso
- o servidor devolveu `Mcp-Session-Id`
- `tools/list` retornou as ferramentas GeneXus expostas

Isso confirma que o servidor está funcional como MCP, e não apenas escutando a porta.

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

Se o `initialize` falhar com `406`, o problema costuma ser o `Accept` da requisição e não necessariamente o servidor desligado.

## Estado atual

- O `GeneXus MCP Server` pode responder em `http://localhost:8001/mcp`
- O host local é `GeneXus.Services.Host.exe`
- O servidor pode ser iniciado sem abrir a IDE
- O log relevante é `GXMBLServices.log`
- `settings.json` e `settings-overrides.json` fazem parte do apoio local

## Termo de trabalho

`Arquivo Textual de Objeto Genexus` significa um arquivo `.gx` que representa textualmente um objeto GeneXus e que pode servir como fonte para leitura, estudo, exportação ou importação no fluxo MCP.

## Pontos em aberto

- O formato textual exato que o GeneXus aceita para exportar e importar um `WebPanel` sem perder o conteúdo visual
- Como fazer o round-trip entre os arquivos textuais exportados e a KB de forma confiável
- Qual é a serialização oficial esperada para um `WebPanel` simples com texto visível
- Como produzir um exemplo mínimo que volte da KB com `Start` e `TextBlock` preservados
- Se a pasta `Examples` deve ficar só para exemplos já validados
- Quando vale a pena separar mais os artefatos do workspace de testes

## Próximos registros

Os próximos apontamentos desta pasta devem ampliar esta base com:

- um atalho local para iniciar apenas o `GeneXus MCP Server`
- quais comandos e fluxos de uso foram testados localmente
