
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from fsm_engine import FSMEngine
from protocols.udp import UDPDatagram
from protocols.tcp import TCP
from channel import Channel


def caminho_definicao(nome):
    return os.path.join(ROOT, "definitions", nome)


def criar_tcp():
    return TCP()


def criar_fsm_tcp():
    return FSMEngine(caminho_definicao("tcp.json"))


def criar_fsm_udp():
    return FSMEngine(caminho_definicao("udp.json"))


class TestUDPScenarios(unittest.TestCase):

    def test_fsm_udp_send_receive(self):
        fsm = criar_fsm_udp()
        self.assertEqual(fsm.state, "READY")
        self.assertTrue(fsm.trigger("send"))
        self.assertTrue(fsm.trigger("receive"))
        self.assertEqual(fsm.state, "READY")

    def test_checksum_udp_valido(self):
        pacote = UDPDatagram(1025, 80, "Ola")
        self.assertTrue(pacote.is_valid())

    def test_checksum_udp_corrompido(self):
        pacote = UDPDatagram(1025, 80, "Ola")
        pacote.data = "OlaX"
        self.assertFalse(pacote.is_valid())

    # Cenário 8: 20 datagramas UDP e perda de 30%
    def test_cenario_8_udp_com_perda(self):
        canal = Channel(
            loss_probability=0.30,
            seed=42
        )

        enviados = 20
        recebidos = 0

        for numero in range(enviados):
            pacote = UDPDatagram(1025, 80, f"Mensagem-{numero}")
            resultado = canal.transmit(pacote)
            recebidos += len(resultado)

        perdidos = enviados - recebidos

        print(
            f"\nUDP: enviados={enviados}, "
            f"recebidos={recebidos}, perdidos={perdidos}"
        )

        self.assertEqual(enviados, 20)
        self.assertLess(recebidos, enviados)
        self.assertEqual(recebidos + perdidos, enviados)

    # Cenário 9: checksum detecta corrupção
    def test_cenario_9_udp_corrompido_no_canal(self):
        canal = Channel(
            corruption_probability=1.0,
            seed=42
        )

        original = UDPDatagram(1025, 80, "Mensagem")
        resultado = canal.transmit(original)

        self.assertEqual(len(resultado), 1)

        pacote_recebido, atraso = resultado[0]

        self.assertFalse(pacote_recebido.is_valid())
        # A cópia corrompida não deve modificar o original.
        self.assertTrue(original.is_valid())


class TestTCPScenarios(unittest.TestCase):

    def test_cenario_1_handshake(self):
        cliente = criar_fsm_tcp()
        servidor = criar_fsm_tcp()

        servidor.trigger("listen")
        cliente.trigger("connect")
        servidor.trigger("receive_SYN")
        cliente.trigger("receive_SYN_ACK")
        servidor.trigger("receive_ACK")

        self.assertEqual(cliente.state, "ESTABLISHED")
        self.assertEqual(servidor.state, "ESTABLISHED")

    def test_cenario_2_perda_syn(self):
        cliente = criar_fsm_tcp()
        cliente.trigger("connect")
        self.assertTrue(cliente.trigger("timeout"))
        self.assertEqual(cliente.state, "SYN_SENT")

    def test_cenario_3_perda_syn_ack(self):
        cliente = criar_fsm_tcp()
        servidor = criar_fsm_tcp()

        servidor.trigger("listen")
        cliente.trigger("connect")
        servidor.trigger("receive_SYN")
        cliente.trigger("timeout")
        servidor.trigger("timeout")

        self.assertEqual(cliente.state, "SYN_SENT")
        self.assertEqual(servidor.state, "SYN_RCVD")

    def test_cenario_4_fechamento_normal(self):
        cliente = criar_fsm_tcp()
        servidor = criar_fsm_tcp()

        servidor.trigger("listen")
        cliente.trigger("connect")
        servidor.trigger("receive_SYN")
        cliente.trigger("receive_SYN_ACK")
        servidor.trigger("receive_ACK")

        cliente.trigger("close")
        servidor.trigger("receive_FIN")
        servidor.trigger("close")
        cliente.trigger("receive_ACK")
        cliente.trigger("receive_FIN")
        servidor.trigger("receive_ACK")

        self.assertEqual(cliente.state, "TIME_WAIT")
        self.assertEqual(servidor.state, "CLOSED")

    def test_cenario_5_fechamento_simultaneo(self):
        cliente = criar_fsm_tcp()
        servidor = criar_fsm_tcp()

        servidor.trigger("listen")
        cliente.trigger("connect")
        servidor.trigger("receive_SYN")
        cliente.trigger("receive_SYN_ACK")
        servidor.trigger("receive_ACK")

        cliente.trigger("close")
        servidor.trigger("close")
        cliente.trigger("receive_FIN")
        servidor.trigger("receive_FIN")
        cliente.trigger("receive_ACK")
        servidor.trigger("receive_ACK")

        self.assertEqual(cliente.state, "TIME_WAIT")
        self.assertEqual(servidor.state, "TIME_WAIT")

    # Cenário 6: três ACKs duplicados acionam Fast Retransmit
    
    
    def test_cenario_6_fast_retransmit(self):
        tcp = TCP()
        tcp.trigger("connect")
        tcp.trigger("receive_SYN_ACK")

        segmento = tcp.send_data("Ola")
        self.assertIsNotNone(segmento)

        # O ACK 0 é o ACK anterior; três repetições
        # devem disparar a retransmissão rápida.
        ack_anterior = 0

        tcp.receive_ack(ack_anterior)
        tcp.receive_ack(ack_anterior)
        tcp.receive_ack(ack_anterior)

        retransmissao = tcp.get_retransmission()

        self.assertIsNotNone(retransmissao)
        self.assertEqual(retransmissao.seq, segmento.seq)
        self.assertTrue(tcp.fast_retransmit)

        print("Cenário 6: retransmissão rápida validada.")



    def test_cenario_7_porta_fechada(self):
        servidor = criar_fsm_tcp()

        self.assertTrue(servidor.trigger("receive_data"))
        self.assertEqual(servidor.state, "CLOSED")


class TestComparacaoProtocolos(unittest.TestCase):

    # Cenário 10: comparação simplificada sob a mesma taxa de perda.
    # UDP não tenta recuperar pacotes; a simulação TCP tenta novamente.
    def test_cenario_10_comparacao_udp_tcp(self):
        quantidade = 20

        canal_udp = Channel(
            loss_probability=0.30,
            seed=123
        )

        udp_recebidos = 0

        for numero in range(quantidade):
            pacote = UDPDatagram(1025, 80, f"UDP-{numero}")
            udp_recebidos += len(canal_udp.transmit(pacote))

        canal_tcp = Channel(
            loss_probability=0.30,
            seed=123
        )

        tcp_recebidos = 0
        retransmissoes = 0

        for numero in range(quantidade):
            pacote = UDPDatagram(1025, 80, f"TCP-{numero}")
            tentativas = 0

            while tentativas < 100:
                resultado = canal_tcp.transmit(pacote)

                if resultado:
                    tcp_recebidos += 1
                    break

                retransmissoes += 1
                tentativas += 1

            self.assertLess(tentativas, 100)

        print(
            f"\nComparação simplificada: "
            f"UDP recebeu {udp_recebidos}/{quantidade}; "
            f"TCP recebeu {tcp_recebidos}/{quantidade}; "
            f"tentativas adicionais TCP={retransmissoes}"
        )

        self.assertLessEqual(udp_recebidos, quantidade)
        self.assertEqual(tcp_recebidos, quantidade)
        self.assertGreaterEqual(retransmissoes, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)