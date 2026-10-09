import random
import copy


class Channel:
    def __init__(
        self,
        loss_probability=0.0,
        corruption_probability=0.0,
        duplication_probability=0.0,
        reordering_probability=0.0,
        min_delay=0,
        max_delay=0,
        seed=None
    ):
        self.loss_probability = loss_probability
        self.corruption_probability = corruption_probability
        self.duplication_probability = duplication_probability
        self.reordering_probability = reordering_probability
        self.min_delay = min_delay
        self.max_delay = max_delay

        self.random = random.Random(seed)
        self.buffer = []
        self.drop_next = False
        self.virtual_time = 0

        self._validate_parameters()

    def _validate_parameters(self):
        probabilities = [
            self.loss_probability,
            self.corruption_probability,
            self.duplication_probability,
            self.reordering_probability
        ]

        if any(p < 0 or p > 1 for p in probabilities):
            raise ValueError(
                "As probabilidades devem estar entre 0 e 1."
            )

        if self.min_delay < 0 or self.max_delay < self.min_delay:
            raise ValueError("Intervalo de atraso inválido.")

    def drop_next_packet(self):
        """Descarta manualmente o próximo pacote transmitido."""
        self.drop_next = True
        print("CANAL: próximo pacote será descartado.")

    def _corrupt_packet(self, packet):
        """Corrompe uma cópia do pacote, quando possível."""
        corrupted = copy.deepcopy(packet)

        if hasattr(corrupted, "data"):
            data = corrupted.data

            if isinstance(data, str):
                corrupted.data = data + "X"
            elif isinstance(data, bytes):
                corrupted.data = data + b"X"
            else:
                print("CANAL: pacote não permite corrupção automática.")
                return corrupted

            print("CANAL: pacote corrompido.")

        elif hasattr(corrupted, "checksum"):
            corrupted.checksum ^= 1
            print("CANAL: checksum corrompido.")

        else:
            print("CANAL: pacote não permite corrupção automática.")

        return corrupted

    def transmit(self, packet):
        """
        Retorna uma lista de pares (pacote, atraso_ms).
        Um pacote perdido ou retido para reordenação pode
        resultar em uma lista vazia.
        """
        if self.drop_next:
            self.drop_next = False
            print("CANAL: pacote descartado manualmente.")
            return []

        if self.random.random() < self.loss_probability:
            print("CANAL: pacote perdido.")
            return []

        transmitted_packet = copy.deepcopy(packet)

        if self.random.random() < self.corruption_probability:
            transmitted_packet = self._corrupt_packet(
                transmitted_packet
            )

        delay = self.random.randint(
            self.min_delay,
            self.max_delay
        )

        packets = [(transmitted_packet, delay)]

        if self.random.random() < self.duplication_probability:
            packets.append((copy.deepcopy(transmitted_packet), delay))
            print("CANAL: pacote duplicado.")

        if self.random.random() < self.reordering_probability:
            self.buffer.extend(packets)
            print("CANAL: pacote retido para reordenação.")
            return []

        # Um pacote retido anteriormente pode ser entregue depois
        # do pacote atual, simulando uma mudança de ordem.
        if self.buffer:
            self.random.shuffle(self.buffer)
            packets.extend(self.buffer)
            self.buffer.clear()
            print("CANAL: pacote(s) retido(s) liberado(s).")

        self.virtual_time += delay

        print(
            f"CANAL: pacote entregue com atraso de {delay} ms."
        )

        return packets

    def flush(self):
        """Libera pacotes retidos no buffer."""
        if not self.buffer:
            return []

        self.random.shuffle(self.buffer)
        packets = self.buffer.copy()
        self.buffer.clear()

        print(
            f"CANAL: liberando {len(packets)} pacote(s) retido(s)."
        )

        return packets