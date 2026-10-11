# Entrega 5 — Versão final revisada

**Grupo 04 · Caso Saúde · Envelope D**  
Padrões e Arquitetura de Software — PUC-Campinas · 2026/2

## Integrantes

Lucas Joaquim; Lucas Ferro; Gabriel Jesus; Eduardo Borsatto; Enrico Gazal.

## Roteiro de avaliação

1. [Changelog da versão final](CHANGELOG.md): mudanças após a leitura cruzada.
2. [Matriz de estilos revisada](../entrega-1-matriz-de-estilos/): avaliação dos doze estilos e descartes.
3. [Documento de arquitetura](../entrega-2-documento-de-arquitetura/documento-arquitetura.md): decisões, restrições e respostas às perguntas do caso.
4. [Diagramas C4 e índice dos ADRs](../entrega-2-documento-de-arquitetura/): contexto, contêineres e componentes.
5. [Entrega 4B](../entrega-4-leitura-cruzada/respostas-recebidas.md): respostas às sete objeções do Grupo 09.
6. [Spike revisado](../entrega-3-spike/): código executável, cenário e saída esperada.

## ADRs vigentes e histórico

| Decisão vigente | Histórico substituído | Tema |
| --- | --- | --- |
| [ADR-0006](../entrega-2-documento-de-arquitetura/adr/0006-celulas-por-porte-e-modularidade.md) | ADR-0001 | Células por porte e três unidades operacionais |
| [ADR-0007](../entrega-2-documento-de-arquitetura/adr/0007-autoridade-e-adaptadores-por-tenant.md) | ADR-0003 | Autoridade única de reserva e adaptadores por tenant |
| [ADR-0008](../entrega-2-documento-de-arquitetura/adr/0008-operacao-e-escrita-em-campanhas.md) | ADR-0004 | Operação por célula e controle da escrita |
| [ADR-0009](../entrega-2-documento-de-arquitetura/adr/0009-roteamento-replicado-e-quota-por-tenant.md) | ADR-0005 | Roteamento replicado e quota por tenant |

O ADR-0002 permanece vigente. Os ADRs anteriores são preservados na pasta `adr/` como histórico.

## Verificação da publicação

- Material extraído do pacote `grupo-04-4b-atualizado.zip` e organizado nas cinco pastas de entregas existentes.
- Textos em `.md`, com links relativos; diagramas disponíveis em páginas Markdown com Mermaid e nos arquivos originais.
- Spike executado com sucesso; saída comparada com `saida-esperada.txt` e código compilado com `py_compile`.
- Verificação automática do spike mantida no [GitHub Actions](https://github.com/EnricoGazal/Grupo-04-rede-municipal-saude/actions/workflows/spike.yml).

O spike é uma simulação determinística; não substitui testes de carga, rede ou múltiplas réplicas em produção. O documento da Entrega 4A conserva a ressalva do pacote sobre confrontar as objeções com o repositório recebido.

[← Leitura cruzada](../entrega-4-leitura-cruzada/) · [Voltar ao início](../README.md)
