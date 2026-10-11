# Entrega 4B — Respostas às objeções recebidas

**Grupo respondente:** Grupo 04 — Saúde, Envelope D  
**Grupo revisor:** Grupo 09 — Saúde, Envelope C  
**Objeto da revisão:** arquitetura do Grupo 04 para uma plataforma multi-cidade de saúde

## 1. Síntese da revisão

Agradecemos as sete objeções recebidas. Elas identificaram principalmente lacunas de operacionalização, não uma rejeição da composição geral. A proposta continua utilizando arquitetura celular, serviços por domínio, eventos e CQRS seletivo, mas foi refinada em quatro pontos: roteamento fora do caminho do plano de controle, células com capacidade por porte, autoridade única durante a migração do legado e escalabilidade de escrita no agendamento.

Também reconhecemos que a primeira versão do spike era insuficiente para provar o isolamento: ela simulava duas filas separadas, mas não uma infraestrutura compartilhada sob pressão nem uma tentativa real de tenant incorreto. Por isso, a Entrega 4B atualiza a decisão e a prova técnica associada.

## Objeção 1 — Não está definido quem escolhe a célula de cada requisição

### Resumo da objeção

O documento dizia que o catálogo regional mantém a rota da cidade, mas também dizia que o plano de controle não participa do tráfego clínico. Sem explicar onde o roteamento ocorre, o catálogo poderia virar dependência crítica e ponto único de falha.

### Resposta do Grupo 04

**Aceitamos a objeção.** A versão anterior deixava implícita uma dependência entre o gateway e o catálogo regional. Isso não era suficiente para sustentar a afirmação de que a queda do plano de controle não interrompe o atendimento.

### Decisão revisada

O roteamento passa a ter três camadas. O endereço da cidade é resolvido por DNS ou subdomínio estável. Um gateway regional replicado mantém em memória o mapa `tenant_id → cell_id`, carregado de forma assíncrona a partir do catálogo. A célula mantém sua própria configuração de tenant e não consulta o plano de controle durante uma requisição clínica.

Uma alteração de rota ou o cadastro de uma nova cidade depende do plano de controle. O atendimento de tenants já provisionados continua usando o mapa de rotas local mesmo que o catálogo esteja indisponível. O gateway possui réplicas e health checks; a perda de uma réplica não interrompe o tráfego.

### Alterações realizadas

- O ADR-0009 passa a registrar o roteador replicado e o mapa de rotas em memória.
- O documento de arquitetura passa a distinguir **plano de controle**, **gateway de roteamento** e **células de dados**.
- O spike passa a testar erro de tenant e falha de catálogo sem interromper tenants já conhecidos.

## Objeção 2 — O spike não tem como falhar

### Resumo da objeção

O spike anterior modelava cada célula como um objeto isolado. A falha de Cidade A era apenas um atributo Python, e o cenário não exercitava um recurso compartilhado, cota por tenant ou token com tenant incorreto.

### Resposta do Grupo 04

**Aceitamos integralmente.** A crítica é correta. O spike antigo demonstrava apenas que duas filas independentes podem continuar processando, mas não provava que o desenho resistiria a um erro de roteamento ou a um pico que tentasse consumir capacidade compartilhada.

### Decisão revisada

A prova deve simular um gateway replicado, um catálogo que pode ficar indisponível, limites de concorrência por tenant e uma requisição cujo tenant do corpo não coincide com o tenant autenticado. A falha de Cidade A deve interromper apenas o consumidor e a fila de A, enquanto Cidade B continua processando dentro da sua cota.

### Alterações realizadas

- O spike foi reescrito para medir a vazão de B antes e durante a falha de A.
- O código rejeita explicitamente o tenant do corpo diferente do tenant do token.
- O código simula indisponibilidade do catálogo depois que o mapa de rotas foi carregado.
- A verificação compara invariantes de isolamento, em vez de depender apenas de uma contagem fixa.

## Objeção 3 — Uma célula por cidade não combina com clientes de 10 a 200 unidades

### Resumo da objeção

Uma célula completa por cidade poderia impor o mesmo custo fixo a clientes pequenos e grandes. A própria definição de cell-based permite que uma célula contenha um subconjunto de clientes, e não necessariamente exatamente uma cidade.

### Resposta do Grupo 04

**Aceitamos parcialmente.** O princípio de isolamento por cidade continua adequado para clientes grandes ou críticos, mas a decisão “uma célula por cidade” era rígida demais para o intervalo de 10 a 200 unidades.

### Decisão revisada

A unidade de isolamento passa a ser uma **célula de capacidade**, com duas modalidades:

- Clientes grandes, críticos ou com requisito de isolamento dedicado recebem uma célula própria.
- Clientes pequenos podem compartilhar uma célula com outros tenants, desde que possuam filas, quotas de CPU, memória, conexões, armazenamento e consumidores separados por tenant.

A promoção de um tenant para célula dedicada ocorre quando ele ultrapassa limites de carga, risco ou crescimento definidos no catálogo. A migração é feita por cópia, replay de eventos e troca de rota, sem alterar o contrato funcional.

### Alterações realizadas

- O ADR-0006 deixa de tratar “uma cidade = uma célula” como regra universal.
- O mapa de restrições passa a registrar células dedicadas e células agrupadas por porte.
- A exigência de isolamento de falha permanece: um tenant não pode consumir a quota reservada a outro.

## Objeção 4 — Seis serviços por célula multiplicam a operação para três times

### Resumo da objeção

Com muitos clientes, seis serviços em cada célula poderiam produzir implantações e responsabilidades demais para três times. A escolha não estava alinhada ao custo operacional do envelope D.

### Resposta do Grupo 04

**Aceitamos parcialmente.** As fronteiras de domínio continuam necessárias, mas não é obrigatório que cada domínio seja um serviço independente desde o primeiro dia.

### Decisão revisada

A célula terá poucas unidades implantáveis alinhadas aos três times:

1. **Núcleo clínico modular:** atendimento, prontuário e farmácia, com fronteiras de módulo e ownership explícito.
2. **Regulação e integração:** regulação de leitos, adaptadores de legado e integrações de consistência forte.
3. **Engajamento e campanha:** agendamento, vacinação, projeções e vigilância, com possibilidade de escala independente durante campanhas.

Os módulos continuam proibidos de acessar diretamente o banco de outro módulo. Um módulo só será extraído como serviço quando houver necessidade comprovada de escala, isolamento de falha ou ciclo de implantação diferente.

### Alterações realizadas

- O ADR-0006 passa a definir módulos como padrão e extração seletiva como exceção.
- O documento de arquitetura passa a apresentar três unidades operacionais principais dentro da célula.
- A matriz de estilos mantém microsserviços como aplicação parcial, não como decomposição obrigatória de todos os domínios.

## Objeção 5 — A reserva de leito tem dois donos enquanto o legado estiver ativo

### Resumo da objeção

O sistema novo dizia ser dono da reserva, mas o legado continuaria aceitando operações durante dois anos. A restrição única no banco novo não impediria uma reserva concorrente feita diretamente no legado.

### Resposta do Grupo 04

**Aceitamos integralmente.** Reconciliar depois de uma dupla reserva não é uma garantia de exclusividade. Também reconhecemos que segurar um lock do banco novo durante uma chamada HTTP externa criaria risco de bloqueio e divergência.

### Decisão revisada

A migração terá uma autoridade de reserva por tenant e por fase. Enquanto o legado for a autoridade, o serviço novo registra a solicitação com estado `PENDENTE_LEGADO` e encaminha uma operação idempotente ao adaptador. O usuário só recebe `CONFIRMADA` depois da confirmação da autoridade vigente.

Durante o timeout, o sistema não repete cegamente a solicitação. Ele consulta o estado pelo identificador idempotente. Se o legado não suportar consulta idempotente, a operação fica pendente para reconciliação manual ou por consulta de estado antes de nova tentativa.

Depois da migração de um tenant, a autoridade passa para o serviço novo. O legado fica em modo somente leitura para aquele fluxo. Nunca haverá dois escritores ativos para o mesmo conjunto de leitos.

### Alterações realizadas

- O ADR-0007 passa a explicitar autoridade única por fase de migração.
- O documento inclui a máquina de estados `SOLICITADA → PENDENTE_LEGADO → CONFIRMADA/RECUSADA/RECONCILIAÇÃO`.
- O lock local não fica aberto durante a chamada ao legado.
- Cada transição é auditada com chave de idempotência.

## Objeção 6 — Um adaptador só para o legado, mas cada cliente tem o seu

### Resumo da objeção

O envelope D é multi-cidade e não garante que todos os clientes utilizem o mesmo sistema legado, versão ou API. Um adaptador único poderia transformar uma mudança de um cliente em risco para os demais.

### Resposta do Grupo 04

**Aceitamos.** O termo “o adaptador” no documento descrevia a porta conceitual, mas não deixava claro que a implementação deveria ser por cliente.

### Decisão revisada

A plataforma terá uma porta estável de regulação e adaptadores versionados por tenant. Cada célula carrega apenas o adaptador configurado para seus clientes. O contrato interno define comandos, respostas, idempotência, timeout, reconciliação e estados de erro.

A variação por cliente é tratada como extensão controlada, semelhante a um microkernel restrito ao perímetro de integração. O núcleo de regulação não recebe regras específicas do legado. Cada adaptador passa por testes de contrato antes da implantação.

### Alterações realizadas

- O ADR-0007 passa a mencionar registro de adaptadores por tenant e versão.
- O mapa de integração inclui capability `legacy_adapter_version`.
- Uma alteração em um adaptador não altera os demais tenants.

## Objeção 7 — O pico da campanha é de escrita, e o CQRS só resolve a leitura

### Resumo da objeção

Projeções de leitura não resolvem a disputa concorrente por vagas de vacinação. O pico concentra escritas no banco transacional, e replicar o serviço sem controlar a entrada pode apenas aumentar conflitos.

### Resposta do Grupo 04

**Aceitamos integralmente.** A arquitetura anterior dava mais destaque ao escalonamento das consultas e não descrevia suficientemente o caminho de escrita.

### Decisão revisada

Durante campanhas, o agendamento usa uma fila de entrada com limite por tenant, unidade e campanha. As vagas são particionadas por unidade, data e faixa de horário para evitar que todos os usuários disputem uma única linha ou agregado. Cada solicitação recebe chave idempotente.

A capacidade da célula é pré-aquecida antes da janela conhecida da campanha. O banco transacional recebe conexões e capacidade reservadas, enquanto projeções atendem consultas de disponibilidade. Quando a capacidade de escrita é atingida, o sistema responde com estado controlado de espera ou indisponibilidade de vaga, sem repetir a tentativa de forma ilimitada.

### Alterações realizadas

- O ADR-0008 passa a incluir escalabilidade de escrita, não apenas leitura.
- O documento passa a diferenciar fila de entrada, projeção de leitura e confirmação transacional da vaga.
- O plano de campanha inclui teste de carga e aumento antecipado da célula afetada.

## 2. Balanço final das mudanças

As objeções do Grupo 09 foram consideradas tecnicamente pertinentes. Nenhuma exige abandonar a arquitetura celular, mas elas exigem refinamento de escopo e operação.

A versão atualizada adota quatro correções principais: roteamento replicado sem dependência síncrona do plano de controle; células dedicadas ou agrupadas por porte; três unidades operacionais com módulos internos; e autoridade única de reserva durante a migração do legado. O spike também foi atualizado para provar uma decisão mais próxima do risco real do envelope D.

## 3. Itens que permanecem como trade-offs

O agrupamento de clientes pequenos reduz custo, mas exige quotas, monitoramento e migração controlada para célula dedicada. A modularidade interna reduz o número de deploys, mas exige disciplina de dependências e ownership. A fila de agendamento protege o banco, mas introduz estado de espera visível ao usuário. A autoridade única por fase simplifica a exclusividade, mas exige um plano de migração por tenant.

## Referências

[1]: https://github.com/NPLaura22/Grupo02_PADROES_E_ARQUITETURA_DE_SOFTWARE "Exemplo público de repositório de arquitetura"
[2]: https://puc-campinas.instructure.com/courses/97274/files/4317955 "Estilos Arquiteturais de Software: guia de consulta"

- [Exemplo público de repositório de arquitetura][1]
- [Estilos Arquiteturais de Software: guia de consulta][2]
