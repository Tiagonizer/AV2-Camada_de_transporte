from fsm_engine import FSMEngine
from protocols.udp import UDPDatagram
from protocols.tcp import TCP, TCPSegment
from channel import Channel


# ============================================================
# TESTE DA FSM UDP
# ============================================================

print("===== TESTE DA FSM UDP =====")

udp = FSMEngine("definitions/udp.json")

print("Estado inicial:", udp.state)

udp.trigger("send")
udp.trigger("receive")

print("Estado final:", udp.state)


# ============================================================
# TESTE DO DATAGRAMA UDP
# ============================================================

print("\n===== TESTE DO DATAGRAMA UDP =====")

datagram = UDPDatagram(
    source_port=1025,
    destination_port=80,
    data="Olá"
)

print("Porta de origem:", datagram.source_port)
print("Porta de destino:", datagram.destination_port)
print("Comprimento:", datagram.length)
print("Checksum:", datagram.checksum)
print("Checksum válido:", datagram.is_valid())


# ============================================================
# TESTE DE CORRUPÇÃO
# ============================================================

print("\n===== TESTE DE CORRUPÇÃO =====")

datagram.data = "Ola"

print("Dados alterados:", datagram.data)
print("Checksum válido:", datagram.is_valid())

if not datagram.is_valid():
    print("RECEPTOR: Datagrama descartado.")


# ============================================================
# TESTE DO CANAL
# ============================================================

print("\n===== TESTE DO CANAL =====")

channel = Channel(
    loss_probability=0.3,
    corruption_probability=0.2,
    duplication_probability=0.2,
    reordering_probability=0.2,
    min_delay=10,
    max_delay=100,
    seed=42
)

for i in range(10):
    print(f"Datagrama {i + 1}:")
    channel.transmit(f"Datagrama {i + 1}")


# ============================================================
# TESTE DA FSM TCP - CLIENTE E SERVIDOR
# ============================================================

print("\n===== TESTE DA FSM TCP =====")

servidor = TCP()
cliente = TCP()

print("\nEstado inicial:")
print("Cliente:", cliente.state)
print("Servidor:", servidor.state)

# Servidor começa a escutar
servidor.trigger("listen")

# Cliente inicia conexão
cliente.trigger("connect")

# Servidor recebe SYN
servidor.trigger("receive_SYN")

# Cliente recebe SYN-ACK
cliente.trigger("receive_SYN_ACK")

# Servidor recebe ACK
servidor.trigger("receive_ACK")

print("\nEstado final:")
print("Cliente:", cliente.state)
print("Servidor:", servidor.state)


# ============================================================
# TESTE DE PERDA DO SYN
# ============================================================

print("\n===== TESTE DE PERDA DO SYN =====")

cliente = TCP()
servidor = TCP()

servidor.trigger("listen")
cliente.trigger("connect")

print("\nSYN foi perdido pelo canal.")

print("Estado do cliente antes do timeout:", cliente.state)

cliente.timeout()

print("Estado do cliente após timeout:", cliente.state)

# Servidor recebe o SYN retransmitido
servidor.trigger("receive_SYN")

# Cliente recebe o SYN-ACK
cliente.trigger("receive_SYN_ACK")

# Servidor recebe o ACK
servidor.trigger("receive_ACK")

print("\nEstados após a retransmissão:")
print("Cliente:", cliente.state)
print("Servidor:", servidor.state)


# ============================================================
# TESTE DE PERDA DO SYN-ACK
# ============================================================

print("\n===== TESTE DE PERDA DO SYN-ACK =====")

cliente = TCP()
servidor = TCP()

servidor.trigger("listen")
cliente.trigger("connect")

# Servidor recebe o SYN
servidor.trigger("receive_SYN")

print("\nSYN-ACK foi perdido pelo canal.")

print("Cliente:", cliente.state)
print("Servidor:", servidor.state)

# Cliente percebe timeout e retransmite SYN
cliente.timeout()

# Servidor percebe timeout e retransmite SYN-ACK
servidor.timeout()

print("\nApós os timeouts:")
print("Cliente:", cliente.state)
print("Servidor:", servidor.state)


# Cliente recebe o SYN-ACK retransmitido
cliente.trigger("receive_SYN_ACK")

# Servidor recebe o ACK retransmitido pelo cliente
servidor.trigger("receive_ACK")

print("\nEstados finais:")
print("Cliente:", cliente.state)
print("Servidor:", servidor.state)


# ============================================================
# TESTE DE FECHAMENTO NORMAL
# ============================================================

print("\n===== TESTE DE FECHAMENTO NORMAL =====")

cliente = TCP()
servidor = TCP()

# Estabelece a conexão
servidor.trigger("listen")
cliente.trigger("connect")
servidor.trigger("receive_SYN")
cliente.trigger("receive_SYN_ACK")
servidor.trigger("receive_ACK")

print("\nConexão estabelecida:")
print("Cliente:", cliente.state)
print("Servidor:", servidor.state)

# Cliente inicia o fechamento
cliente.trigger("close")

# Servidor recebe FIN
servidor.trigger("receive_FIN")

# Servidor fecha sua parte
servidor.trigger("close")

# Cliente recebe ACK do FIN
cliente.trigger("receive_ACK")

# Cliente recebe FIN do servidor
cliente.trigger("receive_FIN")

# Servidor recebe o ACK final
servidor.trigger("receive_ACK")

print("\nEstados finais:")
print("Cliente:", cliente.state)
print("Servidor:", servidor.state)



# ============================================================
# TESTE DE FECHAMENTO SIMULTÂNEO
# ============================================================

print("\n===== TESTE DE FECHAMENTO SIMULTÂNEO =====")

cliente = TCP()
servidor = TCP()

# Estabelece a conexão
servidor.trigger("listen")
cliente.trigger("connect")
servidor.trigger("receive_SYN")
cliente.trigger("receive_SYN_ACK")
servidor.trigger("receive_ACK")

print("\nConexão estabelecida:")
print("Cliente:", cliente.state)
print("Servidor:", servidor.state)

# Os dois lados fecham ao mesmo tempo
cliente.trigger("close")
servidor.trigger("close")

print("\nApós os dois FIN:")
print("Cliente:", cliente.state)
print("Servidor:", servidor.state)

# Cada lado recebe o FIN do outro
cliente.trigger("receive_FIN")
servidor.trigger("receive_FIN")

print("\nApós receber os FIN:")
print("Cliente:", cliente.state)
print("Servidor:", servidor.state)

# Cada lado recebe o ACK
cliente.trigger("receive_ACK")
servidor.trigger("receive_ACK")

print("\nEstados finais:")
print("Cliente:", cliente.state)
print("Servidor:", servidor.state)



print("\n===== TESTE DE SEGMENTO TCP =====")

segmento = TCPSegment(
    seq=100,
    ack=0,
    data="ABCDE"
)

print("Sequence Number:", segmento.seq)
print("Acknowledgment Number:", segmento.ack)
print("Dados:", segmento.data)
print("Comprimento:", segmento.length)



print("\n===== TESTE DE ACK DUPLICADO =====")

tcp_teste = TCP()

tcp_teste.receive_ack(1)
tcp_teste.receive_ack(1)
tcp_teste.receive_ack(1)
tcp_teste.receive_ack(1)

print("Contador de ACKs duplicados:", tcp_teste.duplicate_ack_count)
print("Fast Retransmit:", tcp_teste.fast_retransmit)


print("\n===== TESTE DE 10 SEGMENTOS TCP =====")

segmentos = []

for i in range(1, 11):
    segmento = TCPSegment(
        seq=i,
        ack=0,
        data=f"Dados-{i}"
    )

    segmentos.append(segmento)

    print(
        f"Segmento {i}: "
        f"SEQ={segmento.seq}, "
        f"ACK={segmento.ack}, "
        f"Dados={segmento.data}"
    )



print("\n===== SIMULAÇÃO DE PERDA =====")

segmento_perdido = 5

for segmento in segmentos:
    if segmento.seq == segmento_perdido:
        print(
            f"Segmento {segmento.seq}: PERDIDO NO CANAL"
        )
    else:
        print(
            f"Segmento {segmento.seq}: entregue ao receptor"
        )



print("\n===== ACKS CUMULATIVOS =====")

tcp_receptor = TCP()

for segmento in segmentos:
    if segmento.seq < segmento_perdido:
        ack = segmento.seq + 1
        print(
            f"Receptor: segmento {segmento.seq} recebido "
            f"-> ACK {ack}"
        )
        tcp_receptor.receive_ack(ack)

    elif segmento.seq > segmento_perdido:
        ack = segmento_perdido
        print(
            f"Receptor: segmento {segmento.seq} chegou fora de ordem "
            f"-> ACK duplicado {ack}"
        )
        tcp_receptor.receive_ack(ack)


print("\n===== RETRANSMISSÃO DO SEGMENTO PERDIDO =====")

if tcp_receptor.fast_retransmit:
    segmento_retransmitido = next(
        segmento
        for segmento in segmentos
        if segmento.seq == segmento_perdido
    )

    print(
        f"Segmento {segmento_retransmitido.seq}: "
        f"retransmitido pelo remetente"
    )

    print(
        f"Receptor: segmento {segmento_retransmitido.seq} "
        f"recebido corretamente"
    )

    novo_ack = segmento_retransmitido.seq + 1

    print(
        f"Receptor: enviando ACK {novo_ack}"
    )

    tcp_receptor.receive_ack(novo_ack)



print("\n===== TESTE DE PORTA TCP FECHADA =====")

servidor_fechado = TCP()

print("Estado do servidor:", servidor_fechado.state)

print("Cliente envia dados para a porta fechada.")
servidor_fechado.trigger("receive_data")