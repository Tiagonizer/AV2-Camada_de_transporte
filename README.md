# Simulador de Redes Convergentes - FSM UDP/TCP

Trabalho da AV2 de Redes Convergentes (Camada de Transporte) - UNIFOR

## Equipe

- Tiago Pascoal - Matrícula 2320491
- Victor Menezes - Matrícula 2325183

## Sobre o projeto

Simulador em Python que modela o comportamento dos protocolos UDP e TCP da camada de transporte usando máquinas de estados finitos (FSM), com um canal de comunicação que simula problemas reais de rede. O projeto ainda está em desenvolvimento.

## O que já está implementado

- Motor de FSM genérico (fsm_engine.py) que lê a definição dos estados e transições de arquivos JSON
- FSM do UDP (estado READY, eventos send e receive)
- FSM do TCP com 11 estados: CLOSED, LISTEN, SYN_SENT, SYN_RCVD, ESTABLISHED, FIN_WAIT_1, FIN_WAIT_2, CLOSING, TIME_WAIT, CLOSE_WAIT e LAST_ACK
- Datagrama UDP com cálculo e validação de checksum
- Segmento TCP com número de sequência, número de ACK e dados
- Detecção de ACKs duplicados e Fast Retransmit no TCP
- Canal de comunicação com perda, corrupção, duplicação, reordenação, atraso e semente (seed) configuráveis
- Interface gráfica em Tkinter para controlar o simulador
- Testes automatizados de cenários

## Estrutura do projeto

~~~
fsm_udp_tcp/
├── main.py                  # roteiro de demonstração dos cenários
├── fsm_engine.py            # motor de máquina de estados
├── channel.py               # canal com perda, corrupção, duplicação e reordenação
├── definitions/
│   ├── tcp.json             # estados e transições do TCP
│   └── udp.json             # estados e transições do UDP
├── protocols/
│   ├── tcp.py               # TCP e segmento TCP
│   └── udp.py               # datagrama UDP e checksum
├── gui/
│   └── app.py               # interface gráfica (Tkinter)
└── tests/
    └── tests_scenarios.py   # testes automatizados
~~~

## Como executar

Requisito: Python 3 (o Tkinter já vem com a instalação padrão do Python).

1. Entre na pasta do código:

   cd fsm_udp_tcp
2. Rodar a demonstração no terminal (cenários de UDP, handshake, perda de SYN e SYN-ACK, fechamento normal e simultâneo, ACK duplicado, etc.):

   python main.py
3. Abrir a interface gráfica:

   python gui/app.py
4. Rodar os testes automatizados:

   python -m unittest discover -s tests -p "tests_scenarios.py"

Observação: o main.py usa caminhos relativos, então deve ser executado de dentro da pasta fsm_udp_tcp.

## Cenários demonstrados

- Estabelecimento de conexão TCP (three-way handshake)
- Perda do SYN e do SYN-ACK com retransmissão por timeout
- Fechamento normal e fechamento simultâneo da conexão
- ACKs cumulativos, ACKs duplicados e Fast Retransmit
- Datagrama UDP corrompido sendo descartado pelo checksum
- Envio de dados para uma porta TCP fechada

## Próximos passos

### Próxima etapa: preparar a transferência TCP

Trabalho no arquivo protocols/tcp.py, mantendo a interface e os testes atuais.

- [ ] Número de sequência (SEQ) e confirmação (ACK)
- [ ] Envio de segmentos de dados
- [ ] Reconhecimento cumulativo dos segmentos recebidos
- [ ] Retransmissão após timeout
- [ ] Fast Retransmit após três ACKs duplicados
- [ ] Registro das transmissões e retransmissões para visualizar na interface