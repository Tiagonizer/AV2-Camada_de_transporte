# Simulador de Redes Convergentes — FSM UDP/TCP

Trabalho da AV2 de Redes Convergentes — Camada de Transporte  
Universidade de Fortaleza (UNIFOR)

## Equipe

- Tiago Pascoal
- Victor Menezes

## Sobre o projeto

Simulador desenvolvido em Python para representar aspectos dos protocolos UDP e TCP da camada de transporte utilizando máquinas de estados finitos (FSM). O projeto inclui um canal de comunicação configurável, capaz de simular condições adversas de rede, e uma interface gráfica para acompanhar os testes.

## Funcionalidades implementadas

- Motor genérico de máquinas de estados finitos, com definições carregadas de arquivos JSON.
- FSM UDP com estado `READY` e eventos de envio e recebimento.
- FSM TCP com 11 estados, cobrindo estabelecimento, transferência e encerramento de conexão.
- Datagrama UDP com cálculo e validação de checksum.
- Segmentos TCP com números de sequência, ACKs e dados.
- Reconhecimento cumulativo de dados e controle de segmentos pendentes.
- Detecção de ACKs duplicados e preparação de retransmissão rápida após três ACKs duplicados.
- Preparação de retransmissão após timeout.
- Estimativa de RTT e cálculo do intervalo de timeout.
- Canal configurável para perda, corrupção, duplicação, reordenação e atraso.
- Semente aleatória configurável para testes reproduzíveis.
- Interface gráfica em Tkinter.
- Testes automatizados para os principais cenários de UDP e TCP.

**Status dos testes:** 14 testes automatizados passaram na última execução registrada. A retransmissão rápida é verificada por teste, mas sua transmissão efetiva pelo canal após três ACKs duplicados ainda precisa de validação integrada.

## Estrutura do projeto

```text
fsm_udp_tcp/
├── main.py
├── fsm_engine.py
├── channel.py
├── definitions/
│   ├── tcp.json
│   └── udp.json
├── protocols/
│   ├── tcp.py
│   └── udp.py
├── gui/
│   └── app.py
└── tests/
    ├── tests_scenarios.py
    └── test_tcp_channel.py
```

## Requisitos

- Python 3
- Tkinter, normalmente incluído nas instalações do Python para desktop

## Como executar

Abra o terminal na pasta `fsm_udp_tcp`.

Executar a demonstração:

```bash
python main.py
```

Abrir a interface gráfica:

```bash
python gui/app.py
```

Executar os testes automatizados:

```bash
python -m unittest discover -s tests -v
```

Execute os comandos a partir da pasta `fsm_udp_tcp`, para que os caminhos relativos e os imports funcionem corretamente.

## Cenários de teste

1. Estabelecimento de conexão TCP (*three-way handshake*).
2. Perda de SYN e timeout.
3. Perda de SYN-ACK e timeout.
4. Fechamento normal de conexão TCP.
5. Fechamento simultâneo de conexão TCP.
6. Detecção de três ACKs duplicados e seleção do segmento para retransmissão rápida.
7. Envio de dados para porta TCP fechada, com geração de RST.
8. Envio de 20 datagramas UDP em canal com perda configurada.
9. Detecção de corrupção de datagrama por checksum.
10. Comparação simplificada de entrega UDP e TCP em canal com perda.

Os cenários automatizados demonstram os comportamentos implementados no simulador. Alguns mecanismos, como a retransmissão rápida integrada ao canal, ainda requerem validação adicional para confirmar o comportamento completo.

## Resultados registrados

Na última execução dos testes:

- A suíte automatizada terminou com 14 testes aprovados.
- No cenário de perda UDP, foram recebidos 12 de 20 datagramas.
- Na comparação simplificada, UDP recebeu 14 de 20 datagramas e TCP recebeu 20 de 20, com 8 tentativas adicionais.

Esses números correspondem às execuções registradas e não representam uma garantia de resultado para todas as configurações do canal.

## Limitações e melhorias futuras

- Validar a retransmissão rápida de ponta a ponta, incluindo a entrega do segmento retransmitido pelo canal.
- Integrar de forma mais completa o envio, a recepção e a retransmissão dos segmentos TCP.
- Aprofundar a simulação do controle de fluxo e congestionamento, se exigidos pelo escopo final.
- Registrar e apresentar de forma mais detalhada as transmissões, ACKs e retransmissões na interface gráfica.
- Documentar os cenários com capturas de tela e resultados experimentais.

## Repositório

Código-fonte: https://github.com/Tiagonizer/AV2-Camada_de_transporte
