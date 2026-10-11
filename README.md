# Grupo 04 — Saúde D

[![Spike](https://github.com/EnricoGazal/Grupo-04-rede-municipal-saude/actions/workflows/spike.yml/badge.svg)](https://github.com/EnricoGazal/Grupo-04-rede-municipal-saude/actions/workflows/spike.yml)

## Caso e envelope

**Caso:** rede municipal de atenção à saúde. **Envelope D:** empresa que vende o sistema para várias cidades, com 25 desenvolvedores em três times distribuídos. A arquitetura deve atender secretarias com redes de 10 a 200 unidades, suportar picos de campanhas, manter o isolamento entre clientes e escalar apenas o tenant que precisa.

## Integrantes

- Lucas Joaquim
- Lucas Ferro
- Gabriel Jesus
- Eduardo Borsatto
- Enrico Gazal

## Decisão arquitetural em uma frase

Adotamos uma arquitetura híbrida composta por células de capacidade, módulos ou microsserviços orientados a domínio, arquitetura hexagonal, eventos assíncronos e CQRS seletivo. Clientes grandes podem ter célula dedicada; clientes pequenos compartilham células com quotas isoladas por `tenant_id`.

## Entregas — guia para o professor

Comece pela [Entrega 5 — versão final](entrega-5-entrega-final/), que reúne o changelog, a relação de ADRs substitutos e os links para as evidências.

| Entrega | Conteúdo | Acesso |
| --- | --- | --- |
| 1 | Matriz dos doze estilos e descartes | [Matriz revisada](entrega-1-matriz-de-estilos/) |
| 2 | Arquitetura, mapa de restrições, C4 e nove ADRs | [Documento e diagramas](entrega-2-documento-de-arquitetura/) |
| 3 | Spike de roteamento, quota e isolamento por tenant | [Código e execução](entrega-3-spike/) |
| 4 | Objeções ao Grupo 02 e respostas ao Grupo 09 | [Leitura cruzada](entrega-4-leitura-cruzada/) |
| 5 | Consolidação final e histórico das mudanças | [Entrega final](entrega-5-entrega-final/) |

Os textos estão em Markdown (`.md`). Os diagramas também têm páginas Markdown com blocos Mermaid, fontes `.mmd` e imagens `.png`. O spike mantém seu formato executável `.py` e a saída de referência `.txt`.

## Execução do spike

```bash
cd 3-spike
python3 exemplo.py
python3 exemplo.py > saida-obtida.txt
diff -u saida-esperada.txt saida-obtida.txt
```

O spike usa somente a biblioteca padrão do Python. Ele simula catálogo indisponível, célula compartilhada, quota por tenant, falha de uma cidade e rejeição de tenant adulterado.

## Premissas e limites

Os números de dimensionamento são premissas da atividade e não dados oficiais. A solução é uma arquitetura de referência para avaliação acadêmica; antes de uma implantação real seriam necessários threat modeling, testes de carga, validação clínica, análise de custos e revisão jurídica.

## Referências

[1]: https://puc-campinas.instructure.com/courses/97274/pages/um-problema-cinco-realidades "Enunciado Um problema, cinco realidades"
[2]: https://puc-campinas.instructure.com/courses/97274/files/4317955 "Estilos Arquiteturais de Software: guia de consulta"

- [Enunciado Um problema, cinco realidades][1]
- [Estilos Arquiteturais de Software: guia de consulta][2]
