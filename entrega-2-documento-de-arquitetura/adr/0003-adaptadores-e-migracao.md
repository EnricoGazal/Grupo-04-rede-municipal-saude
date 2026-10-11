# ADR-0003: Anti-corruption layer e migração strangler

- **Status:** aceito
- **Contexto:** A regulação legada continua ativa por até dois anos e sistemas federais possuem janelas de indisponibilidade. O restante da plataforma não pode depender de formatos antigos.
- **Decisão:** Usar adaptadores hexagonais para traduzir a API legada e as APIs federais. A plataforma publica eventos por outbox; o adaptador federal usa retry, backoff e dead-letter. A migração segue leitura controlada, comparação, piloto de escrita e expansão por cidade.
- **Alternativas consideradas:** Banco compartilhado com legado, descartado por acoplamento e risco de escrita concorrente; chamada síncrona direta a sistemas federais, descartada porque bloquearia o atendimento; big bang, descartado por risco operacional.
- **Consequências positivas:** Contrato interno estável, tolerância a indisponibilidade e substituição incremental.
- **Consequências negativas:** Há estados pendentes, duplicidade potencial que exige idempotência e custo temporário de manter dois caminhos.

## Referências

[1]: https://puc-campinas.instructure.com/courses/97274/files/4317955 "Estilos Arquiteturais de Software: guia de consulta"
