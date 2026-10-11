import os

from fsm_engine import FSMEngine


class TCPSegment:
    def __init__(self, seq, ack=0, data=""):
        self.seq = seq
        self.ack = ack
        self.data = data
        self.length = len(data.encode("utf-8"))

    def __repr__(self):
        return (
            f"TCPSegment(seq={self.seq}, "
            f"ack={self.ack}, length={self.length})"
        )


class TCP:
    def __init__(self, initial_seq=1):
        definition_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "definitions",
            "tcp.json"
        )

        self.fsm = FSMEngine(definition_path)

        self.next_seq = initial_seq
        self.last_ack = 0
        self.duplicate_ack_count = 0

        self.outstanding = {}
        self.fast_retransmit = False
        self.segment_to_retransmit = None

        self.estimated_rtt = None
        self.rtt_variation = None
        self.timeout_interval = 1.0

        self.expected_seq = initial_seq
        self.log = []

    @property
    def state(self):
        return self.fsm.state

    def _log(self, message):
        self.log.append(message)
        print(message)

    def trigger(self, event):
        return self.fsm.trigger(event)

    def send_data(self, data):
        if not isinstance(data, str):
            raise TypeError("Os dados devem ser uma string.")

        if not data:
            raise ValueError("Não é possível enviar dados vazios.")

        if self.state != "ESTABLISHED":
            raise RuntimeError(
                "A conexão TCP precisa estar ESTABLISHED para enviar dados."
            )

        segment = TCPSegment(
            seq=self.next_seq,
            ack=self.last_ack,
            data=data
        )

        self.outstanding[segment.seq] = segment
        self.next_seq += segment.length

        self._log(
            f"TCP: segmento enviado SEQ={segment.seq}, "
            f"ACK={segment.ack}, tamanho={segment.length}"
        )

        return segment

    def receive_segment(self, segment):
        if not isinstance(segment, TCPSegment):
            raise TypeError(
                "O pacote recebido não é um TCPSegment."
            )

        if segment.length == 0:
            self._log("TCP: segmento sem dados recebido.")
            return self.expected_seq

        if segment.seq == self.expected_seq:
            self.expected_seq += segment.length

            self._log(
                f"TCP: dados recebidos em SEQ={segment.seq}; "
                f"próximo SEQ esperado={self.expected_seq}"
            )

        elif segment.seq > self.expected_seq:
            self._log(
                f"TCP: segmento fora de ordem; esperado SEQ "
                f"{self.expected_seq}, recebido SEQ {segment.seq}"
            )

        else:
            self._log(
                f"TCP: segmento duplicado recebido em SEQ "
                f"{segment.seq}"
            )

        ack_number = self.expected_seq

        self._log(
            f"TCP: enviando ACK cumulativo {ack_number}"
        )

        return ack_number

    def receive_ack(self, ack_number, rtt_sample=None):
        if rtt_sample is not None:
            self._update_rtt(rtt_sample)

        if ack_number < self.last_ack:
            self._log("TCP: ACK antigo ignorado.")
            return

        if ack_number == self.last_ack:
            self.duplicate_ack_count += 1

            self._log(
                f"TCP: ACK duplicado {ack_number} "
                f"({self.duplicate_ack_count}/3)"
            )

            if self.duplicate_ack_count == 3:
                if self.outstanding:
                    seq = min(self.outstanding)
                    self.segment_to_retransmit = self.outstanding[seq]
                    self.fast_retransmit = True
                    self._log(
                        f"TCP: FAST RETRANSMIT! "
                        f"Retransmitindo segmento SEQ {seq}"
                    )
                else:
                    self._log(
                        "TCP: três ACKs duplicados, "
                        "mas não há segmento pendente para retransmitir."
                    )
            return

        self.last_ack = ack_number
        self.duplicate_ack_count = 0
        self.fast_retransmit = False
        self.segment_to_retransmit = None

        acknowledged = [
            seq
            for seq, segment in self.outstanding.items()
            if seq + segment.length <= ack_number
        ]

        for seq in acknowledged:
            del self.outstanding[seq]

        self._log(
            f"TCP: ACK recebido: {ack_number}; "
            f"segmentos confirmados: {len(acknowledged)}"
        )

    def _update_rtt(self, sample):
        if sample < 0:
            return

        if self.estimated_rtt is None:
            self.estimated_rtt = sample
            self.rtt_variation = sample / 2
        else:
            variation = abs(self.estimated_rtt - sample)

            self.rtt_variation = (
                0.75 * self.rtt_variation
                + 0.25 * variation
            )

            self.estimated_rtt = (
                0.875 * self.estimated_rtt
                + 0.125 * sample
            )

        self.timeout_interval = max(
            0.2,
            self.estimated_rtt + 4 * self.rtt_variation
        )

        self._log(
            f"TCP: RTT estimado={self.estimated_rtt:.3f}s; "
            f"timeout={self.timeout_interval:.3f}s"
        )

    def timeout(self):
        success = False

        # Timeout da conexão, conforme os estados definidos na FSM.
        if self.state in ("SYN_SENT", "SYN_RCVD", "TIME_WAIT"):
            success = self.fsm.trigger("timeout")

        # Timeout de dados: prepara a retransmissão do segmento.
        if self.outstanding:
            seq = min(self.outstanding)
            self.segment_to_retransmit = self.outstanding[seq]

            self.timeout_interval = min(
                self.timeout_interval * 2,
                60.0
            )

            self._log(
                f"TCP: timeout; retransmitindo segmento SEQ {seq}"
            )

            return True

        return success

    def get_pending_segments(self):
        return list(self.outstanding.values())

    def get_retransmission(self):
        return self.segment_to_retransmit