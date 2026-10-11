import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from protocols.tcp import TCP
from channel import Channel


class TestTCPChannel(unittest.TestCase):

    def test_perda_e_retransmissao_de_segmento(self):
        tcp = TCP()
        tcp.trigger("connect")
        tcp.trigger("receive_SYN_ACK")

        canal = Channel(loss_probability=1.0, seed=42)

        # 1. Emissor envia um segmento.
        segmento = tcp.send_data("Ola")

        # 2. O canal perde o segmento.
        recebido = canal.transmit(segmento)
        self.assertEqual(recebido, [])

        # O segmento continua pendente.
        self.assertEqual(len(tcp.get_pending_segments()), 1)

        # 3. Simula o timeout e prepara a retransmissao.
        tcp.timeout()
        retransmissao = tcp.get_retransmission()
        self.assertIsNotNone(retransmissao)

        # 4. Desativa a perda para a nova tentativa.
        canal.loss_probability = 0.0

        recebido = canal.transmit(retransmissao)
        self.assertEqual(len(recebido), 1)

        segmento_recebido, atraso = recebido[0]

        # 5. O receptor processa o segmento e devolve um ACK.
        ack = tcp.receive_segment(segmento_recebido)
        tcp.receive_ack(ack)

        # 6. O segmento deve deixar de estar pendente.
        self.assertEqual(tcp.get_pending_segments(), [])

        print("\nTeste de integracao TCP/canal concluido.")
        print(f"ACK recebido: {ack}")
        print(f"Segmentos pendentes: {tcp.get_pending_segments()}")


if __name__ == "__main__":
    unittest.main(verbosity=2)