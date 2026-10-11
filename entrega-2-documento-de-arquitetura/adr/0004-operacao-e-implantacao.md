# ADR-0004: Escalonamento e operação por célula

- **Status:** aceito
- **Contexto:** O envelope D exige nuvem multirregião, clientes de portes diferentes e pico sazonal brutal. Escalar toda a plataforma por uma cidade seria caro e poderia causar interferência.
- **Decisão:** Cada célula terá limites, métricas e filas próprios. O escalonamento será acionado por profundidade de fila, latência e erro dentro da célula. Campanhas usam projeções de leitura e consumidores elásticos. O plano de controle provisiona células e registra capacidade, sem ficar no caminho de requisições clínicas.
- **Alternativas consideradas:** Cluster regional único, descartado por blast radius; serverless em todos os serviços, descartado por imprevisibilidade de latência e custo em transações; escala manual, descartada por não atender picos.
- **Consequências positivas:** Capacidade cresce apenas no tenant pressionado e falhas ficam contidas.
- **Consequências negativas:** Operação precisa comparar células, custos e versões; a infraestrutura é duplicada.

## Referências

[1]: https://puc-campinas.instructure.com/courses/97274/files/4317955 "Estilos Arquiteturais de Software: guia de consulta"
