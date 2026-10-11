# ADR-0009: Roteamento replicado e quota por tenant

- **Status:** substitui o ADR-0005
- **Contexto:** O roteador e o catálogo são componentes compartilhados, e a leitura cruzada apontou que o spike anterior não provava falha, catálogo indisponível ou tenant adulterado.
- **Decisão:** DNS ou subdomínio identifica o tenant; gateway regional replicado resolve o tenant por mapa de rotas em memória. O mapa é carregado assincronamente do catálogo, portanto tenants conhecidos continuam operando se o catálogo cair. Células compartilhadas possuem quota por tenant, e o consumidor rejeita mensagem cujo tenant não corresponde ao tenant autenticado. O spike prova pico, falha de A, continuidade de B, catálogo fora e tenant adulterado.
- **Alternativas consideradas:** Catálogo síncrono em cada requisição, descartado por colocar o plano de controle no caminho clínico; fila regional única, descartada por risco de starvation; particionamento apenas por chave, descartado como isolamento operacional insuficiente.
- **Consequências positivas:** Falha mensurável, roteamento resiliente, escala independente e proteção contra mistura de tenants.
- **Consequências negativas:** O gateway exige alta disponibilidade, consistência de configuração, observabilidade e testes de promoção entre células.
