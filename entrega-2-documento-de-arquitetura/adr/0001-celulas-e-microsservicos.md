# ADR-0001: Células por cidade com microsserviços por domínio

- **Status:** aceito
- **Contexto:** O produto atende secretarias com 10 a 200 unidades. Uma campanha ou falha de uma cidade não pode afetar outra, e três times precisam evoluir o produto.
- **Decisão:** Implantar uma célula replicável por cidade. Dentro dela, separar atendimento/prontuário, regulação, farmácia, agendamento e vigilância em serviços de domínio. O plano de controle regional gerencia catálogo e capacidade, mas fica fora do tráfego clínico.
- **Alternativas consideradas:** Monolito multi-tenant, descartado por raio de falha e escala acoplada; microsserviços sem células, descartados porque isolam processo mas deixam banco, filas e limites compartilhados; uma célula por unidade, descartada por custo operacional excessivo.
- **Consequências positivas:** Escala por tenant, blast radius limitado, ownership claro e implantação progressiva.
- **Consequências negativas:** Duplicação de infraestrutura, mais observabilidade, necessidade de contratos e reconciliação distribuída.
- **Fronteira de estilos:** A célula define a unidade de implantação e falha; microsserviços definem a unidade de domínio; hexagonal define a fronteira interna de cada serviço.

## Referências

[1]: https://puc-campinas.instructure.com/courses/97274/files/4317955 "Estilos Arquiteturais de Software: guia de consulta"
