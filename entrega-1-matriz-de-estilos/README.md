# Entrega 1 — Matriz de estilos aplicada

**Grupo 04 · Caso Saúde · Envelope D**

[Voltar ao README](../README.md) · [Entrega 2 →](../entrega-2-documento-de-arquitetura/)

## Contexto de avaliação

O produto é vendido a secretarias de saúde com redes de 10 a 200 unidades. O caso exige continuidade da triagem da UPA sem internet, reserva de leitos sem duplicidade, prontuário sensível com rastreabilidade por 20 anos, notificação em até 24 horas e substituição gradual do legado de regulação. O envelope D acrescenta multitenancy, pico sazonal brutal e isolamento de falhas por cidade.

As referências às seções são do livro da disciplina [2]. [URL 🔗](https://puc-campinas.instructure.com/courses/97274/files/4317955)

> Este arquivo não usa tabelas. Cada estilo está organizado com campos empilhados para impressão em folha retrato.

### Índice

1. [Monolito em camadas](#estilo-1--monolito-em-camadas) — 🟡 Em parte
2. [Monolito modular](#estilo-2--monolito-modular) — 🟡 Em parte
3. [Hexagonal / Ports and Adapters](#estilo-3--hexagonal--ports-and-adapters) — 🟢 Sim
4. [Microkernel](#estilo-4--microkernel) — 🟡 Em parte
5. [Microsserviços](#estilo-5--microsserviços) — 🟢 Sim
6. [SOA e barramento de serviços (ESB)](#estilo-6--soa-e-barramento-de-serviços-esb) — 🟡 Em parte
7. [Arquitetura orientada a eventos](#estilo-7--arquitetura-orientada-a-eventos) — 🟢 Sim
8. [Serverless](#estilo-8--serverless) — 🟡 Em parte
9. [Arquitetura celular](#estilo-9--arquitetura-celular-cell-based) — 🟢 Sim, dominante
10. [CQRS](#estilo-10--cqrs) — 🟢 Sim, seletivo
11. [Event Sourcing](#estilo-11--event-sourcing) — 🔴 Não como padrão
12. [Pipes and Filters](#estilo-12--pipes-and-filters) — 🟡 Em parte

---

## Estilo 1 — Monolito em camadas

**Serve para o caso e envelope:** Em parte.

**Subdomínio:** MVP administrativo de baixa criticidade, não como núcleo multi-cidade.

**Por quê:** A separação em camadas da seção 5.1 simplifica o início, mas uma unidade de implantação compartilhada aumenta o raio de falha e impede escalar uma cidade isoladamente.

**Qualidade:** Melhora simplicidade; piora isolamento e escalabilidade independente.

## Estilo 2 — Monolito modular

**Serve para o caso e envelope:** Em parte.

**Subdomínio:** Backoffice inicial e módulos de cadastro.

**Por quê:** As fronteiras explícitas da seção 6.1 reduzem acoplamento sem exigir muitos serviços. Ainda assim, o processo e o banco compartilhados não isolam completamente um tenant em pico ou falha.

**Qualidade:** Melhora manutenibilidade; piora isolamento operacional.

## Estilo 3 — Hexagonal / Ports and Adapters

**Serve para o caso e envelope:** Sim.

**Subdomínio:** Prontuário, regulação, farmácia e adaptadores de legado/federais.

**Por quê:** A seção 7.1 separa regras de negócio dos mecanismos externos. Isso permite trocar API legada, fila e armazenamento sem levar indisponibilidade externa para o domínio.

**Qualidade:** Melhora testabilidade e portabilidade; piora custo de abstração.

## Estilo 4 — Microkernel

**Serve para o caso e envelope:** Em parte.

**Subdomínio:** Regras configuráveis de protocolos e integrações por cidade.

**Por quê:** Plugins são úteis quando cada cidade possui variações de integração. O estilo não deve governar o núcleo clínico, pois plugins demais dificultam previsibilidade e certificação.

**Qualidade:** Melhora extensibilidade; piora governança e previsibilidade.

## Estilo 5 — Microsserviços

**Serve para o caso e envelope:** Sim.

**Subdomínio:** Serviços de prontuário, leitos, farmácia, agendamento e notificações.

**Por quê:** A seção 9.1 favorece implantação e escala por serviço. Usaremos serviços por domínio, mas com células por cidade para que a independência seja real e não apenas lógica.

**Qualidade:** Melhora isolamento, implantação e escala; piora complexidade distribuída.

## Estilo 6 — SOA e barramento de serviços (ESB)

**Serve para o caso e envelope:** Em parte.

**Subdomínio:** Faixa de integração com legado e sistemas federais.

**Por quê:** A seção 10.1 ajuda a centralizar transformação e contratos quando há muitos sistemas externos. Evitamos tornar o ESB o caminho de toda regra de negócio, pois ele criaria gargalo e ponto central de falha.

**Qualidade:** Melhora interoperabilidade; piora latência e risco de gargalo.

## Estilo 7 — Arquitetura orientada a eventos

**Serve para o caso e envelope:** Sim.

**Subdomínio:** Vigilância, notificações, sincronização offline e integrações.

**Por quê:** A seção 11.1 desacopla produtores e consumidores, permitindo que a vigilância processe notificações mesmo com o sistema federal indisponível. Eventos exigem idempotência, ordenação por agregado e observabilidade.

**Qualidade:** Melhora resiliência e elasticidade; piora consistência imediata e rastreabilidade operacional.

## Estilo 8 — Serverless

**Serve para o caso e envelope:** Em parte.

**Subdomínio:** Processamento de notificações, campanhas e relatórios assíncronos.

**Por quê:** A seção 12.1 combina com picos variáveis e tarefas curtas. Não será usada em reserva de leito ou prontuário transacional, onde latência, estado e operação previsível pesam mais.

**Qualidade:** Melhora elasticidade e custo fora do pico; piora cold start e previsibilidade de custo.

## Estilo 9 — Arquitetura celular (cell-based)

**Serve para o caso e envelope:** Sim, dominante.

**Subdomínio:** Uma célula isolada por cidade ou cliente.

**Por quê:** A seção 13.1 responde diretamente ao envelope: cada célula contém serviços, filas e dados da cidade. Um pico ou falha fica contido, e a capacidade pode crescer só para o tenant pressionado.

**Qualidade:** Melhora blast radius, isolamento e escala; piora duplicação e operação.

## Estilo 10 — CQRS

**Serve para o caso e envelope:** Sim, seletivo.

**Subdomínio:** Consultas de prontuário, painéis de campanha e vigilância.

**Por quê:** A seção 14.1 separa escrita transacional de leitura. Aplicamos projeções por tenant e não usamos CQRS para toda operação, evitando consistência eventual desnecessária em leitos e dispensação.

**Qualidade:** Melhora leitura e escalabilidade; piora complexidade e atraso de projeção.

## Estilo 11 — Event Sourcing

**Serve para o caso e envelope:** Não como padrão; considerado e descartado.

**Subdomínio:** Apenas uma eventual trilha de eventos clínicos se requisito futuro exigir reconstrução total.

**Por quê:** A seção 15.1 oferece histórico de eventos, mas manter vinte anos de dados sensíveis e atender apagamento legal seria mais complexo. Um log de auditoria com referências minimizadas atende melhor o caso atual.

**Qualidade:** Poderia melhorar reconstrução; piora custo, privacidade e complexidade de apagamento.

## Estilo 12 — Pipes and Filters

**Serve para o caso e envelope:** Em parte.

**Subdomínio:** Pipeline de notificações e exportações analíticas.

**Por quê:** A seção 16.1 encaixa em etapas independentes de validação, anonimização e entrega. Não serve para reserva de leito, que precisa de transação e decisão imediata.

**Qualidade:** Melhora composição e throughput; piora diagnóstico ponta a ponta.

---

## Estilos considerados e descartados

### Event Sourcing como arquitetura de dados geral

Foi descartado porque o caso exige simultaneamente retenção clínica e direitos do paciente. Guardar cada evento clínico para sempre aumentaria a superfície de dados pessoais e tornaria o apagamento seletivo mais arriscado. A decisão é manter estado operacional, trilha de auditoria minimizada e eventos de domínio com política de retenção separada.

### ESB como núcleo de toda a aplicação

Foi descartado porque concentraria tráfego, transformação e regras em um componente que poderia derrubar todas as cidades. O ESB fica limitado ao anti-corruption layer da integração legada e federal; eventos internos usam brokers por célula.

## Síntese

A composição escolhida é arquitetura celular para isolamento, microsserviços para fronteiras de domínio e escala, hexagonal dentro de cada serviço, eventos para desacoplamento e CQRS seletivo para leituras sazonais. Os ADRs da Entrega 2 delimitam explicitamente onde cada estilo termina e quais custos são aceitos.

## Referências

1. Enunciado *Um problema, cinco realidades*
2. *Estilos Arquiteturais de Software: guia de consulta*
