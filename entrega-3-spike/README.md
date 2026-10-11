# Spike — Roteamento e isolamento por tenant

Este spike prova a decisão do **ADR-0009** após a revisão do Grupo 09. O cenário usa duas cidades pequenas na mesma célula de capacidade. A célula compartilha infraestrutura, mas possui quotas de processamento separadas por tenant.

O programa testa quatro pontos:

1. O gateway carrega o mapa de rotas antes de o catálogo ficar indisponível.
2. Cidade A recebe um pico e sofre falha; Cidade B continua processando dentro da própria quota.
3. A indisponibilidade do catálogo não impede o roteamento de tenants já conhecidos.
4. Uma requisição com tenant do corpo diferente do tenant autenticado é rejeitada.

A prova não depende apenas de contagens fixas: ela verifica que B processa eventos antes e depois da falha de A, que A mantém mensagens pendentes e que a requisição adulterada não entra em nenhuma fila.

## Como executar

```bash
python3 exemplo.py
python3 exemplo.py > /tmp/saida-spike.txt
diff -u saida-esperada.txt /tmp/saida-spike.txt
```

O programa usa somente a biblioteca padrão do Python. A saída é determinística.

## Relação com a objeção recebida

O Grupo 09 observou que a versão anterior criava duas filas isoladas e não exercitava um recurso compartilhado. Esta versão simula uma célula compartilhada por clientes pequenos, quotas por tenant, falha de um cliente, catálogo fora e tenant adulterado. A arquitetura de produção ainda exigiria teste de carga, múltiplas réplicas do gateway, falhas de rede e validação de configuração.

A saída preserva o rótulo histórico `ADR-0005` do pacote; a decisão vigente é o ADR-0009. O programa simula um gateway e não testa alta disponibilidade de múltiplas réplicas.

## Referências

[1]: ../entrega-2-documento-de-arquitetura/adr/0009-roteamento-replicado-e-quota-por-tenant.md "ADR-0009"
[2]: ../entrega-4-leitura-cruzada/respostas-recebidas.md "Respostas da Entrega 4B"
[3]: https://puc-campinas.instructure.com/courses/97274/files/4317955 "Estilos Arquiteturais de Software: guia de consulta"

- [ADR-0009][1]
- [Respostas da Entrega 4B][2]
- [Estilos Arquiteturais de Software: guia de consulta][3]
