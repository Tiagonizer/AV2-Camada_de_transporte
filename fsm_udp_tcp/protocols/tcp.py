from fsm_engine import FSMEngine


class TCPSegment:
    def __init__(self, seq, ack=0, data=""):
        self.seq = seq
        self.ack = ack
        self.data = data
        self.length = len(data)

    def __repr__(self):
        return (
            f"TCPSegment("
            f"seq={self.seq}, "
            f"ack={self.ack}, "
            f"length={self.length})"
        )


class TCP:
    def __init__(self):
        self.fsm = FSMEngine("definitions/tcp.json")

        self.next_seq = 1
        self.last_ack = 0
        self.duplicate_ack_count = 0
        self.fast_retransmit = False
        self.segment_to_retransmit = None

    @property
    def state(self):
        return self.fsm.state

    def trigger(self, event):
        return self.fsm.trigger(event)

    def timeout(self):
        return self.fsm.trigger("timeout")

    def receive_ack(self, ack_number):
        if self.fast_retransmit:
            return

        if ack_number == self.last_ack:
            self.duplicate_ack_count += 1

            print(
                f"TCP: ACK duplicado {ack_number} "
                f"({self.duplicate_ack_count}/3)"
            )

            if self.duplicate_ack_count == 3:
                self.fast_retransmit = True
                self.segment_to_retransmit = ack_number
                print("TCP: FAST RETRANSMIT!")
                print(
                    f"TCP: retransmitindo segmento com SEQ "
                    f"{self.segment_to_retransmit}"
                )
        else:
            self.last_ack = ack_number
            self.duplicate_ack_count = 0
            print(f"TCP: ACK recebido: {ack_number}")