# ADR-0005: Roteamento determinístico e isolamento de falhas por tenant

- **Status:** aceito
- **Contexto:** A exigência dominante diz que falha ou pico de uma cidade não pode derrubar as demais. Essa é a decisão mais arriscada porque um compartilhamento acidental de fila ou consumidor pode reintroduzir o blast radius.
- **Decisão:** O gateway resolve `tenant_id` para uma célula. Cada célula possui fila, consumidor e orçamento de concorrência próprios. O consumidor de uma célula nunca processa mensagens de outra. O spike simula um pico e uma falha em Cidade A e verifica que Cidade B continua processando sua fila.
- **Alternativas consideradas:** Fila regional compartilhada, descartada porque mensagens de um tenant poderiam ocupar toda a capacidade; particionamento apenas por chave em uma fila, descartado como isolamento operacional insuficiente; célula por unidade, descartada por custo.
- **Consequências positivas:** Falha mensurável, teste determinístico e escala independente.
- **Consequências negativas:** Mais filas e deploys, necessidade de catálogo consistente e maior custo de observabilidade.
- **Prova:** `entrega-3-spike/exemplo.py` e `entrega-3-spike/saida-esperada.txt`.

## Referências

[1]: https://puc-campinas.instructure.com/courses/97274/files/4317955 "Estilos Arquiteturais de Software: guia de consulta"
