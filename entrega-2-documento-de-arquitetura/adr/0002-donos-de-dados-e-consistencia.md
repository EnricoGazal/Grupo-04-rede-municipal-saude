# ADR-0002: Dono por agregado e consistência seletiva

- **Status:** aceito
- **Contexto:** Leitos não podem ser reservados duas vezes. Farmácia exige receita e lote. Prontuário é sensível, deve ser rastreável e tem retenção de 20 anos.
- **Decisão:** Cada serviço é dono de seus agregados e banco. Reserva de leito, dispensação e escrita clínica usam transação forte local. Leituras de campanha e vigilância usam projeções CQRS. Eventos carregam `tenant_id`, `event_id` e versão. Auditoria guarda ator, finalidade e referência mínima, sem copiar o prontuário.
- **Alternativas consideradas:** Banco compartilhado, descartado por acoplamento e vazamento entre tenants; Event Sourcing geral, descartado pelo custo de apagar dados pessoais; consistência eventual em leitos, descartada por risco de dupla reserva.
- **Consequências positivas:** Isolamento de dados, regras explícitas, apagamento e retenção tratados por política distinta.
- **Consequências negativas:** Projeções atrasam, consultas cross-domain exigem eventos e reconciliação, e cada serviço precisa de controles próprios.

## Referências

[1]: https://puc-campinas.instructure.com/courses/97274/files/4317955 "Estilos Arquiteturais de Software: guia de consulta"
