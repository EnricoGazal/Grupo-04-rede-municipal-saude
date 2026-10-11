# Entrega 2 — Documento de arquitetura

**Grupo 04 · Caso Saúde · Envelope D**

## 1. Resumo executivo

A solução proposta é uma plataforma de atenção à saúde multi-tenant para secretarias com redes de 10 a 200 unidades. O sistema é organizado em células de capacidade: clientes grandes ou críticos recebem célula dedicada, enquanto clientes pequenos podem compartilhar uma célula com quotas isoladas por `tenant_id`. Cada célula possui poucas unidades implantáveis alinhadas aos três times; os domínios permanecem modulares e só são extraídos como serviços quando houver necessidade comprovada de escala ou isolamento. Um plano de controle regional mantém catálogo de clientes, configuração, observabilidade e provisionamento, mas não transporta o tráfego clínico de rotina.

A escolha responde ao risco dominante do envelope: uma campanha de vacinação ou falha em uma cidade não pode consumir a capacidade das demais. A arquitetura também preserva operação offline na UPA, mantém o legado de regulação durante a transição e usa eventos assíncronos para sobreviver às janelas de indisponibilidade federal.

## 2. Contexto e forças

O caso tem 70 UBS, 5 UPAs, um hospital de 400 leitos regulados, 12 mil atendimentos por dia, rede instável nas UBS, prontuário sensível com retenção de 20 anos, estoque com lote e validade, notificações compulsórias em 24 horas e campanhas que multiplicam o acesso em vinte vezes. O envelope D acrescenta três times distribuídos, nuvem pública multirregião, clientes de portes diferentes e necessidade de escalar por cidade.

As qualidades priorizadas são isolamento de falhas, escalabilidade por tenant, disponibilidade local, segurança e auditabilidade. Consistência forte é obrigatória em reserva de leitos, dispensação e identidade do prontuário; consistência eventual é aceitável em painéis, notificações e projeções de leitura.

## 3. Princípios e fronteiras

Cada requisição carrega um `tenant_id` autenticado. Nenhum serviço aceita o tenant recebido diretamente do corpo da requisição. A autorização deriva do token e é verificada no gateway e novamente no serviço dono do dado. Os dados clínicos não atravessam o plano de controle.

O estilo celular estabelece a fronteira operacional. Módulos estabelecem fronteiras de domínio dentro das três unidades operacionais de cada célula; a extração como microsserviço é seletiva, conforme o ADR-0006. Hexagonal estabelece a fronteira de código entre domínio e infraestrutura. Eventos atravessam serviços quando a resposta não precisa ser imediata. CQRS existe apenas em consultas com pico ou agregações caras.

## 4. C4 — contexto

O diagrama [c4-contexto.md](c4-contexto.md) mostra pacientes, profissionais, gestores e sistemas externos em torno da Plataforma Saúde D. As conexões estão rotuladas pelo tipo de conector, conforme solicitado pelo enunciado.

## 5. C4 — contêineres

Cada célula é composta por gateway, módulos ou serviços de domínio, barramento de eventos, banco transacional, projeções de leitura e adaptadores externos. Clientes pequenos podem compartilhar uma célula, mas recebem quotas de CPU, memória, conexões, filas e consumidores. Clientes grandes ou críticos recebem célula dedicada. O gateway usa mapa de rotas replicado em memória; o plano de controle administra configuração e capacidade, mas é isolado do caminho clínico. O catálogo regional não guarda prontuário; guarda apenas metadados de tenant, rota e estado de provisionamento.

A ingestão offline funciona com uma fila local no dispositivo da UPA. A fila é assinada, criptografada e idempotente. Na reconexão, o sincronizador envia comandos com `command_id`; o serviço responde com confirmação ou conflito explícito. A triagem local continua aceitando atendimentos, mas reserva de leito exige confirmação do serviço de regulação quando a conectividade retorna.

## 6. C4 — componentes do serviço de regulação

O serviço de regulação é o contêiner mais importante porque o caso exige que duas unidades nunca reservem o mesmo leito, enquanto o legado permanece ativo. Seus componentes são: API de reserva, coordenador de idempotência, repositório de leitos, adaptador do legado e publicador de eventos. Há uma autoridade única por tenant e fase de migração (ADR-0007). Enquanto o legado for autoridade, a máquina de estados registra `SOLICITADA → PENDENTE_LEGADO → CONFIRMADA/RECUSADA/RECONCILIAÇÃO`; a confirmação depende do legado, com idempotência e consulta de estado após timeout, sem lock local aberto durante a chamada externa. Quando o serviço novo assume a autoridade, sua restrição transacional impede reservas concorrentes, e o legado fica somente leitura para aquele fluxo. Os adaptadores são versionados por tenant (`legacy_adapter_version`).

## 7. Dados e consistência

O prontuário é dono dos registros clínicos e expõe referências mínimas para os demais serviços. A regulação é dona de leitos e ambulâncias. A farmácia é dona de estoque, lote e dispensação. O agendamento é dono de vagas. A vigilância consome eventos de atendimento e produz notificações. O legado é tratado como sistema externo durante a migração e não como banco compartilhado.

A consistência é forte dentro de cada agregado. Entre serviços, eventos possuem `event_id`, `aggregate_id`, `tenant_id`, versão e timestamp lógico. Consumidores persistem a chave de idempotência antes de aplicar efeitos. Falhas de publicação são tratadas por outbox transacional.

## 8. Operação e implantação

Cada célula é um conjunto de unidades implantáveis com limites de CPU, memória, conexões e filas. O gateway regional mantém o mapa de rotas em memória e continua atendendo tenants conhecidos quando o catálogo está indisponível. O plano de controle mede latência, taxa de erro, profundidade de fila, taxa de conflitos, saturação de escrita e consumo por tenant. O escalonamento é acionado por fila, latência e saturação dentro da célula, não pela média regional. Durante campanhas, o agendamento usa fila de entrada, quotas, vagas particionadas por unidade/data e pré-aquecimento da capacidade de escrita.

A implantação ocorre por célula, começando por um tenant de baixa criticidade. Rollback é feito por versão de serviço e esquema compatível. A observabilidade inclui logs estruturados sem conteúdo clínico, métricas com `tenant_id` controlado e traces com mascaramento. A indisponibilidade do sistema federal abre uma fila de retry com backoff; o atendimento local não fica bloqueado.

## 9. Mapa de restrições e decisões

Para facilitar a impressão, cada relação entre restrição, decisão e evidência aparece em um bloco vertical.

### 9.1 Escala e isolamento

**Restrição:** 10–200 unidades por cliente.  
**Decisão:** células de capacidade, dedicadas ou compartilhadas por porte, com catálogo regional.  
**Evidência:** ADR-0006 e C4 de contêineres.

**Restrição:** falha em uma cidade não pode afetar as demais.  
**Decisão:** filas, bancos, quotas, limites e escalonamento por célula e tenant.  
**Evidência:** ADR-0006 e ADR-0009; spike da Entrega 3.

**Restrição:** pico sazonal de campanhas.  
**Decisão:** CQRS seletivo, projeções e escalonamento orientado por fila.  
**Evidência:** ADR-0006 e ADR-0008.

**Restrição:** nuvem pública multirregião.  
**Decisão:** células replicáveis e plano de controle regional.  
**Evidência:** ADR-0008.

### 9.2 Atendimento, regulação e dados

**Restrição:** a UPA deve trabalhar sem internet.  
**Decisão:** fila local idempotente e sincronização posterior.  
**Evidência:** ADR-0002 e ADR-0009.

**Restrição:** reserva de leito sem duplicidade.  
**Decisão:** dono único, restrição transacional e reconciliação com o legado.  
**Evidência:** ADR-0002 e ADR-0007.

**Restrição:** prontuário sensível com retenção de 20 anos.  
**Decisão:** serviço dono, criptografia, autorização e auditoria minimizada.  
**Evidência:** ADR-0002.

**Restrição:** auditoria de acesso e alteração.  
**Decisão:** log append-only com referências minimizadas.  
**Evidência:** ADR-0002.

### 9.3 Integrações e continuidade

**Restrição:** notificação compulsória em até 24 horas.  
**Decisão:** evento local, outbox e fila de retry federal.  
**Evidência:** ADR-0007 e ADR-0008.

**Restrição:** sistema federal com indisponibilidade.  
**Decisão:** adaptador assíncrono, timeout, retry e circuit breaker.  
**Evidência:** ADR-0007 e ADR-0008.

**Restrição:** legado ativo por até dois anos.  
**Decisão:** anti-corruption layer, leitura controlada e migração strangler.  
**Evidência:** ADR-0007.

**Restrição:** três times distribuídos.  
**Decisão:** contratos de serviço, ownership por domínio e ADRs versionados.  
**Evidência:** ADR-0006.

## 10. Respostas às cinco perguntas obrigatórias

### 10.1 Como a UPA continua triando e atendendo sem internet?

O dispositivo local mantém uma fila de comandos assinados e um cache mínimo de dados necessários à triagem. A triagem gera `command_id` e é aplicada localmente; ao retornar a conexão, o sincronizador entrega os comandos com idempotência. Regulação de leito que dependa de estado global fica pendente até confirmação, sem duplicar o atendimento local. Ver ADR-0002, ADR-0009 e [c4-componentes.md](c4-componentes.md).

### 10.2 Como duas unidades não reservam o mesmo leito?

Existe uma autoridade única por tenant e fase de migração. Enquanto o legado for autoridade, o serviço novo registra `SOLICITADA` ou `PENDENTE_LEGADO`, envia uma operação idempotente e só apresenta `CONFIRMADA` após confirmação da autoridade vigente. O serviço não mantém lock aberto durante a chamada externa. Depois da migração, o serviço novo torna-se autoridade e o legado fica somente leitura. Ver ADR-0007.

### 10.3 Como o prontuário rastreia acesso e convive com LGPD?

Todo acesso passa por autorização contextual e gera evento de auditoria com ator, finalidade, paciente referenciado, operação, timestamp e resultado. O conteúdo clínico não é replicado no log. A retenção clínica é separada da retenção de auditoria; solicitações de acesso e retificação passam por workflow, enquanto exclusão é tratada conforme base legal e política institucional, sem apagar registros cuja guarda obrigatória prevaleça. Ver ADR-0002.

### 10.4 Como a notificação chega à vigilância em 24 horas com o sistema federal indisponível?

O atendimento confirmado publica um evento local via outbox. A vigilância consome o evento e gera a notificação dentro da célula, deixando o envio federal em fila durável com retry e dead-letter. O SLA local de geração é monitorado independentemente da disponibilidade federal; quando a janela retorna, o adaptador entrega os itens ainda não confirmados. Ver ADR-0007 e ADR-0008.

### 10.5 Como o legado é substituído gradualmente?

O anti-corruption layer apresenta um contrato novo ao restante da plataforma e cada tenant possui um adaptador versionado. A migração ocorre por fluxo: leitura controlada, comparação de resultados, autoridade única no legado, piloto de escrita, troca de autoridade por tenant, aumento progressivo e desligamento por capacidade. Nenhum serviço novo acessa o banco do legado diretamente. Ver ADR-0007 e [c4-containers.md](c4-containers.md).

## 11. Riscos e trade-offs

A arquitetura paga custo de operação e duplicação por célula para obter isolamento. Consistência eventual entre alguns serviços exige reconciliação e telas que mostrem estados pendentes. O plano de controle é um componente crítico, mas não fica no caminho de transações clínicas; se ele cair, células já provisionadas continuam operando. O maior risco é a disciplina de isolamento de tenant, por isso o spike testa roteamento, fila e falha independente.

## Referências

[1]: https://puc-campinas.instructure.com/courses/97274/pages/um-problema-cinco-realidades "Enunciado Um problema, cinco realidades"
[2]: https://puc-campinas.instructure.com/courses/97274/files/4317955 "Estilos Arquiteturais de Software: guia de consulta"

[Índice da arquitetura](README.md) · [Voltar ao início](../README.md)

- [Enunciado Um problema, cinco realidades][1]
- [Estilos Arquiteturais de Software: guia de consulta][2]
