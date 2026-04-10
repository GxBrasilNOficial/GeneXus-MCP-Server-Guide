# AGENTS.md

## Apoio local

Existe um arquivo separado de apoio, `bl-mapa-funcional.md`, na pasta do `GeneXus Next`, que pode ser útil mais adiante para entender a pasta `bl`.

Por enquanto, ele fica apenas como referência secundária. O foco principal desta pasta continua sendo o `GeneXus MCP Server` fora da IDE.

## Workspace de testes

O workspace base de testes fica em `C:\Dev\Test`.

Na fase atual, esse workspace é a base para trabalho intermediário dos agentes com `Knowledge Bases` tratadas via `GeneXus MCP Server`, sem abrir `Knowledge Bases` de produção.

Nele, deve existir uma pasta separada para cada teste de cada `Knowledge Base`.

Artefatos de teste, exportações temporárias, importações preparadas e experimentos de validação ficam nesse workspace, não nesta pasta de documentação.

## Pasta Examples

A pasta `Examples` deste repositório deve receber apenas exemplos que já tenham sido aceitos corretamente pelo `Codex`, pelo `GeneXus MCP Server` e pelo `GeneXus`.

Enquanto isso não estiver validado, ela pode permanecer vazia.

## WorkWithWeb

Quando uma `Transaction` for atendida por `WorkWithWeb`, o objeto de modelagem a tratar como fonte de verdade é o `WorkWithWeb<NomeDaTransaction>`.

Os `WebPanel`, `WebComponent` e artefatos gerados e administrados por esse `WorkWithWeb` não devem ser alterados diretamente.

Se a intenção for mudar comportamento, layout ou fluxo de objetos gerados por `WorkWithWeb`, a mudança deve ser feita no `WorkWithWeb` correspondente, para que o `GeneXus` regenere os artefatos derivados.
