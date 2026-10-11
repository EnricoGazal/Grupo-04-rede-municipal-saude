# Fronteiras de estilos

Este arquivo não usa tabelas para permanecer adequado à impressão em folha retrato.

## Unidade de falha

**Estilo:** Arquitetura celular (cell-based).

**Onde termina:** Na célula de capacidade, dedicada a um cliente grande ou compartilhada por clientes pequenos com quotas por tenant. O plano de controle não executa transações clínicas.

## Unidade de domínio

**Estilo:** Módulos com extração seletiva em microsserviços.

**Onde termina:** Em cada módulo ou serviço de negócio, organizado nas três unidades operacionais da célula. Nenhum módulo acessa diretamente os dados de outro.

## Código e infraestrutura

**Estilo:** Hexagonal.

**Onde termina:** Nas portas dos adaptadores de banco, legado, filas e APIs federais.

## Comunicação desacoplada

**Estilo:** Orientado a eventos.

**Onde termina:** Em notificações, sincronização, projeções e integrações que toleram atraso.

## Consultas de alto volume

**Estilo:** CQRS.

**Onde termina:** Nas projeções de campanha, vigilância e painéis. Não é usado na reserva de leito.

A composição é intencional. O ADR-0006 substitui o ADR-0001 na estrutura geral. O ADR-0002 limita CQRS e define consistência. O ADR-0007 substitui o ADR-0003 na integração e autoridade de reserva. O ADR-0008 substitui o ADR-0004 na operação e escrita de campanhas. O ADR-0009 substitui o ADR-0005 no roteamento e isolamento por tenant. Os ADRs anteriores permanecem como histórico.

## Referências

[1]: https://puc-campinas.instructure.com/courses/97274/files/4317955 "Estilos Arquiteturais de Software: guia de consulta"

- [Estilos Arquiteturais de Software: guia de consulta][1]
