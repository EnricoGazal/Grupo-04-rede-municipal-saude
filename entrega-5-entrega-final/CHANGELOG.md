# CHANGELOG — Entrega 5 — Versão final

**Grupo 04 — Caso Saúde — Envelope D**

## Integrantes

Lucas Joaquim; Lucas Ferro; Gabriel Jesus; Eduardo Borsatto; Enrico Gazal.

## Versão 1.0.0 — Entrega final

Esta versão consolida o repositório depois da leitura cruzada e responde às objeções recebidas do Grupo 09. O conteúdo foi revisado para manter coerência entre matriz, documento de arquitetura, diagramas C4, ADRs, spike e Entrega 4B.

### Mudanças arquiteturais

A decisão de uma célula obrigatoriamente dedicada por cidade foi refinada. O projeto agora usa células de capacidade: clientes grandes ou críticos podem receber uma célula própria, enquanto clientes pequenos compartilham uma célula com quotas de CPU, memória, conexões, filas e consumidores por tenant. A extração de cada domínio como microsserviço deixou de ser obrigatória; o padrão inicial é uma célula com três unidades operacionais alinhadas aos três times: núcleo clínico, regulação e integração, e engajamento e campanhas.

O roteamento foi explicitado. O gateway regional é replicado e mantém em memória o mapa `tenant_id → cell_id`, carregado assincronamente a partir do catálogo. O catálogo não participa de cada requisição clínica. Tenants já provisionados continuam sendo atendidos durante a indisponibilidade do catálogo; mudanças de configuração ficam pendentes.

A reserva de leitos passou a ter autoridade única por tenant e fase de migração. Enquanto o legado for a autoridade, o serviço novo usa estados `SOLICITADA` e `PENDENTE_LEGADO`, chave de idempotência e consulta de estado após timeout. O novo serviço não mantém lock aberto durante chamada HTTP externa. Após a migração, o legado fica somente leitura para aquele fluxo.

As integrações legadas passaram a ser descritas como adaptadores versionados por tenant, com contrato interno estável e testes de contrato. O agendamento passou a controlar também o pico de escrita, usando fila de entrada, quotas, particionamento de vagas por unidade/data, idempotência e pré-aquecimento da capacidade do banco.

### Mudanças na leitura cruzada

A Entrega 4B foi completada em `4-leitura-cruzada/respostas-recebidas.md`, com resposta às sete objeções recebidas. Foram aceitas integralmente as críticas sobre o spike, autoridade dupla de reserva e pico de escrita; foram aceitas parcialmente as críticas sobre células por porte e quantidade de serviços; e foi aceita a necessidade de explicitar roteamento, adaptadores por cliente e catálogo fora do caminho clínico.

### Substituição formal de ADRs

Os ADRs aceitos originais não foram editados. As alterações que contradizem decisões anteriores foram registradas por novos ADRs com status explícito de substituição:

- **ADR-0006** substitui o ADR-0001: células por porte e modularidade operacional.
- **ADR-0007** substitui o ADR-0003: autoridade única de reserva e adaptadores versionados por tenant.
- **ADR-0008** substitui o ADR-0004: operação por célula e controle de escrita em campanhas.
- **ADR-0009** substitui o ADR-0005: roteamento replicado e quota por tenant.

Os ADRs 0001, 0003, 0004 e 0005 foram preservados como histórico das decisões originais.

### Mudanças no spike

O spike em `3-spike/exemplo.py` foi reescrito para simular uma célula compartilhada por duas cidades pequenas. Ele testa catálogo indisponível depois do carregamento da rota, quota individual, pico da Cidade A, falha da Cidade A, continuidade da Cidade B e rejeição de uma requisição com tenant do corpo diferente do tenant autenticado. A saída foi executada e registrada em `saida-esperada.txt`.

### Verificação final

Foram executadas as seguintes verificações:

- Execução do spike sem dependências externas;
- Comparação da saída executada com `saida-esperada.txt`;
- Compilação do código com `python3 -m py_compile`;
- Conferência dos nomes dos cinco integrantes;
- Conferência das referências aos ADRs substitutos;
- Atualização dos diagramas C4 para células por porte, roteamento replicado e autoridade única de reserva;
- Empacotamento do repositório completo para envio.

## Estrutura para envio

O professor deve receber o link do repositório revisado. O arquivo `grupo-04-4b-atualizado.zip` é apenas uma cópia de segurança local; o conteúdo que precisa estar no Git é a pasta inteira `grupo-04`, incluindo todos os diretórios de `1-matriz` a `5-final`.
