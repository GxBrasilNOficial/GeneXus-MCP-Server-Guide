# Sugestoes De Melhoria Da Nexa

Este arquivo registra sugestoes temporarias de melhoria da skill `nexa` percebidas durante o uso nesta pasta.

Mais adiante, esse conteudo pode ser movido para um lugar metodologicamente mais apropriado.

## Sugestoes Atuais

### WorkWithWeb como fonte de verdade

A `nexa` deveria explicitar melhor que, quando uma `Transaction` e atendida por `WorkWithWeb`, o objeto de modelagem a tratar como fonte de verdade e o `WorkWithWeb<NomeDaTransaction>`.

Tambem deveria explicitar que os `WebPanel`, `WebComponent` e demais artefatos gerados e administrados por esse `WorkWithWeb` nao devem ser alterados diretamente.

### Autonumber em Domain vs Attribute

A `nexa` poderia deixar mais visivel, logo na trilha de modelagem, que `Autonumber` nao e propriedade de `Domain`.

Esse ponto pertence ao `Attribute` dentro da `Transaction`, e vale enfatizar isso para evitar tentativas de modelar identificadores auto numerados no objeto errado.
