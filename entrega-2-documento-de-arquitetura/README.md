# Entrega 2 — Documento de arquitetura

**Grupo 04 · Caso Saúde · Envelope D**

[← Entrega 1](../entrega-1-matriz-de-estilos/) · [Voltar ao README](../README.md) · [Entrega 3 →](../entrega-3-spike/)

## 1. Resumo executivo

A solução proposta é uma plataforma de atenção à saúde multi-tenant para secretarias com redes de 10 a 200 unidades. O sistema é organizado em células por cidade. Cada célula possui os serviços de prontuário, atendimento, regulação, farmácia, agendamento e vigilância, além de filas e armazenamento particionados por `tenant_id`. Um plano de controle regional mantém catálogo de clientes, configuração, observabilidade e provisionamento, mas não transporta o tráfego clínico de rotina.

A escolha responde ao risco dominante do envelope: uma campanha de vacinação ou falha em uma cidade não pode consumir a capacidade das demais. A arquitetura também preserva operação offline na UPA, mantém o legado de regulação durante a transição e usa eventos assíncronos para sobreviver às janelas de indisponibilidade federal.

## 2. Contexto e forças

O caso tem 70 UBS, 5 UPAs, um hospital de 400 leitos regulados, 12 mil atendimentos por dia, rede instável nas UBS, prontuário sensível com retenção de 20 anos, estoque com lote e validade, notificações compulsórias em 24 horas e campanhas que multiplicam o acesso em vinte vezes. O envelope D acrescenta três times distribuídos, nuvem pública multirregião, clientes de portes diferentes e necessidade de escalar por cidade.

As qualidades priorizadas são isolamento de falhas, escalabilidade por tenant, disponibilidade local, segurança e auditabilidade. Consistência forte é obrigatória em reserva de leitos, dispensação e identidade do prontuário; consistência eventual é aceitável em painéis, notificações e projeções de leitura.

## 3. Princípios e fronteiras

Cada requisição carrega um `tenant_id` autenticado. Nenhum serviço aceita o tenant recebido diretamente do corpo da requisição. A autorização deriva do token e é verificada no gateway e novamente no serviço dono do dado. Os dados clínicos não atravessam o plano de controle.

O estilo celular estabelece a fronteira operacional. Microsserviços estabelecem fronteiras de domínio dentro de cada célula. Hexagonal estabelece a fronteira de código entre domínio e infraestrutura. Eventos atravessam serviços quando a resposta não precisa ser imediata. CQRS existe apenas em consultas com pico ou agregações caras.

## 4. C4 — contexto

O diagrama `c4-contexto.mmd` mostra pacientes, profissionais, gestores e sistemas externos em torno da Plataforma Saúde D. As conexões estão rotuladas pelo tipo de conector, conforme solicitado pelo enunciado.

## 5. C4 — contêineres

Cada cidade recebe uma célula composta por gateway, serviços de domínio, barramento de eventos, banco transacional, projeções de leitura e adaptadores externos. O plano de controle administra configuração e capacidade, mas é isolado do caminho clínico. O catálogo regional não guarda prontuário; guarda apenas metadados de tenant e estado de provisionamento.

A ingestão offline funciona com uma fila local no dispositivo da UPA. A fila é assinada, criptografada e idempotente. Na reconexão, o sincronizador envia comandos com `command_id`; o serviço responde com confirmação ou conflito explícito. A triagem local continua aceitando atendimentos, mas reserva de leito exige confirmação do serviço de regulação quando a conectividade retorna.

## 6. C4 — componentes do serviço de regulação

O serviço de regulação é o contêiner mais importante porque o caso exige que duas unidades nunca reservem o mesmo leito, enquanto o legado permanece ativo. Seus componentes são: API de reserva, coordenador de idempotência, repositório de leitos, adaptador do legado e publicador de eventos. A reserva usa uma restrição única `(tenant_id, leito_id, intervalo_ativo)` no armazenamento do serviço. O adaptador traduz chamadas para a API antiga e executa reconciliação; ele não concede uma reserva definitiva fora do domínio novo.

## 7. Dados e consistência

O prontuário é dono dos registros clínicos e expõe referências mínimas para os demais serviços. A regulação é dona de leitos e ambulâncias. A farmácia é dona de estoque, lote e dispensação. O agendamento é dono de vagas. A vigilância consome eventos de atendimento e produz notificações. O legado é tratado como sistema externo durante a migração e não como banco compartilhado.

A consistência é forte dentro de cada agregado. Entre serviços, eventos possuem `event_id`, `aggregate_id`, `tenant_id`, versão e timestamp lógico. Consumidores persistem a chave de idempotência antes de aplicar efeitos. Falhas de publicação são tratadas por outbox transacional.

## 8. Operação e implantação

Cada célula é um conjunto de unidades implantáveis com limites de CPU, memória e filas. O plano de controle mede latência, taxa de erro, profundidade de fila, taxa de conflitos e consumo por tenant. O escalonamento é acionado por fila e latência dentro da célula, não pela média regional. O catálogo regional mantém uma rota para a célula de cada cidade.

A implantação ocorre por célula, começando por um tenant de baixa criticidade. Rollback é feito por versão de serviço e esquema compatível. A observabilidade inclui logs estruturados sem conteúdo clínico, métricas com `tenant_id` controlado e traces com mascaramento. A indisponibilidade do sistema federal abre uma fila de retry com backoff; o atendimento local não fica bloqueado.

## 9. Mapa de restrições e decisões

### 9.1 Escala e isolamento

| Restrição | Decisão | Evidência |
|---|---|---|
| 10–200 unidades por cliente. | Células por cidade e catálogo regional. | ADR-0001 e C4 de contêineres. |
| Falha em uma cidade não pode afetar as demais. | Filas, bancos, limites e escalonamento por célula. | ADR-0001 e ADR-0005; spike da Entrega 3. |
| Pico sazonal de campanhas. | CQRS seletivo, projeções e escalonamento orientado por fila. | ADR-0001 e ADR-0004. |
| Nuvem pública multirregião. | Células replicáveis e plano de controle regional. | ADR-0004. |

### 9.2 Atendimento, regulação e dados

| Restrição | Decisão | Evidência |
|---|---|---|
| A UPA deve trabalhar sem internet. | Fila local idempotente e sincronização posterior. | ADR-0002 e ADR-0005. |
| Reserva de leito sem duplicidade. | Dono único, restrição transacional e reconciliação com o legado. | ADR-0002 e ADR-0003. |
| Prontuário sensível com retenção de 20 anos. | Serviço dono, criptografia, autorização e auditoria minimizada. | ADR-0002. |
| Auditoria de acesso e alteração. | Log append-only com referências minimizadas. | ADR-0002. |

### 9.3 Integrações e continuidade

| Restrição | Decisão | Evidência |
|---|---|---|
| Notificação compulsória em até 24 horas. | Evento local, outbox e fila de retry federal. | ADR-0003 e ADR-0004. |
| Sistema federal com indisponibilidade. | Adaptador assíncrono, timeout, retry e circuit breaker. | ADR-0003 e ADR-0004. |
| Legado ativo por até dois anos. | Anti-corruption layer, leitura controlada e migração strangler. | ADR-0003. |
| Três times distribuídos. | Contratos de serviço, ownership por domínio e ADRs versionados. | ADR-0001. |

## 10. Respostas às cinco perguntas obrigatórias

### 10.1 Como a UPA continua triando e atendendo sem internet?

O dispositivo local mantém uma fila de comandos assinados e um cache mínimo de dados necessários à triagem. A triagem gera `command_id` e é aplicada localmente; ao retornar a conexão, o sincronizador entrega os comandos com idempotência. Regulação de leito que dependa de estado global fica pendente até confirmação, sem duplicar o atendimento local. Ver ADR-002, ADR-005 e `c4-componentes.mmd`.

### 10.2 Como duas unidades não reservam o mesmo leito?

O serviço de regulação é o único dono da reserva. Uma transação verifica a versão do leito e grava a reserva com restrição única; a segunda tentativa recebe conflito determinístico. O legado é consultado e reconciliado pelo adaptador, mas não grava diretamente no banco novo. Ver ADR-002 e ADR-003.

### 10.3 Como o prontuário rastreia acesso e convive com LGPD?

Todo acesso passa por autorização contextual e gera evento de auditoria com ator, finalidade, paciente referenciado, operação, timestamp e resultado. O conteúdo clínico não é replicado no log. A retenção clínica é separada da retenção de auditoria; solicitações de acesso e retificação passam por workflow, enquanto exclusão é tratada conforme base legal e política institucional, sem apagar registros cuja guarda obrigatória prevaleça. Ver ADR-002.

### 10.4 Como a notificação chega à vigilância em 24 horas com o sistema federal indisponível?

O atendimento confirmado publica um evento local via outbox. A vigilância consome o evento e gera a notificação dentro da célula, deixando o envio federal em fila durável com retry e dead-letter. O SLA local de geração é monitorado independentemente da disponibilidade federal; quando a janela retorna, o adaptador entrega os itens ainda não confirmados. Ver ADR-003 e ADR-004.

### 10.5 Como o legado é substituído gradualmente?

O anti-corruption layer apresenta um contrato novo ao restante da plataforma e traduz a API antiga. A migração ocorre por fluxo: leitura controlada, comparação de resultados, escrita do novo domínio para uma unidade piloto, aumento progressivo e desligamento por capacidade. Nenhum serviço novo acessa o banco do legado diretamente. Ver ADR-003 e `c4-containers.mmd`.

## 11. Riscos e trade-offs

A arquitetura paga custo de operação e duplicação por célula para obter isolamento. Consistência eventual entre alguns serviços exige reconciliação e telas que mostrem estados pendentes. O plano de controle é um componente crítico, mas não fica no caminho de transações clínicas; se ele cair, células já provisionadas continuam operando. O maior risco é a disciplina de isolamento de tenant, por isso o spike testa roteamento, fila e falha independente.

## Referências

1. Enunciado *Um problema, cinco realidades*
2. *Estilos Arquiteturais de Software: guia de consulta*
