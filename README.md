# EcoCharge

## Sistema Inteligente de Gestão de Energia para Eletropostos

Projeto desenvolvido para a **Sprint 3 – Prototipagem Funcional e Integração**, com o objetivo de demonstrar uma solução de gestão energética para eletropostos utilizando energia solar, armazenamento em bateria, rede elétrica e automação baseada em regras.

---

## 1. Objetivo do Projeto

O EcoCharge é um protótipo de sistema para gerenciamento inteligente de energia em eletropostos.

O sistema simula diferentes níveis de consumo de um eletroposto ao longo do dia e determina automaticamente qual fonte de energia deve ser utilizada.

A estratégia de gerenciamento segue a seguinte prioridade:

1. Energia solar;
2. Energia armazenada na bateria;
3. Energia da rede elétrica.

Durante os horários de maior demanda, o sistema também aplica uma estratégia de gerenciamento de demanda, reduzindo o consumo simulado em 20%.

---

## 2. Funcionamento do Sistema

O sistema recebe como parâmetros:

- Nível inicial da bateria;
- Capacidade total da bateria;
- Consumo do eletroposto;
- Geração de energia solar.

A partir desses dados, o EcoCharge realiza uma simulação por horário.

---

### Video no YouTube:
https://youtu.be/hnuuLNTRFgc

---

### Fluxo de decisão

```text
                 Geração Solar
                       |
                       v
                EcoCharge
                       |
                       v
             Verificar demanda
                       |
                 Horário de pico?
              +--------+--------+
              |                 |
             Sim               Não
              |                 |
              |                 |
              |                 |
              v                 |
       Reduzir demanda          |
           em 20%               |
              |                 |
              +--------+--------+
                       |
                       v
               Energia Solar
                       |
              Solar suficiente?
                 /         \
               Sim          Não
               |             |
               v             v
          Usar Solar     Usar Bateria
                              |
                     Bateria suficiente?
                         /        \
                       Sim         Não
                       |            |
                       v            v
                 Usar Bateria    Usar Rede

