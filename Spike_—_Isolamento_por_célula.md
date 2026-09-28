# Spike — Isolamento por célula

Este programa prova a decisão do ADR-0005. Ele cria duas células, `cidade-a` e `cidade-b`, com filas e consumidores independentes. A Cidade A recebe um pico de eventos, processa parte da carga e falha. A Cidade B continua processando os eventos que já tinha e novos eventos, sem consumir a fila da Cidade A.

O mecanismo externo é simulado por filas em memória. O roteamento exige que o `tenant_id` do evento corresponda à célula. O resultado é determinístico e deve ser idêntico ao arquivo `saida-esperada.txt`.

## Como executar

```bash
python3 exemplo.py
```

O programa usa somente a biblioteca padrão do Python 3.12. Asserções interrompem a execução caso o isolamento não seja comprovado.

## O que aconteceria se a decisão estivesse errada?

Se as filas fossem compartilhadas, a falha da Cidade A poderia bloquear o consumidor da Cidade B ou consumir sua capacidade. Se o roteamento aceitasse um tenant incorreto, haveria risco de vazamento e processamento na célula errada. Em produção, o mesmo teste seria complementado por testes de carga, falha de infraestrutura e verificação de autorização.

## Referências

1. ADR-0005
2. *Estilos Arquiteturais de Software: guia de consulta*
