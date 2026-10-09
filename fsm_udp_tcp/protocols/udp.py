import socket
import struct


class UDPDatagram:
    def __init__(
        self,
        source_port,
        destination_port,
        data,
        source_ip="127.0.0.1",
        destination_ip="127.0.0.1"
    ):
        self.source_port = source_port
        self.destination_port = destination_port
        self.data = data
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.length = 8 + len(data.encode("utf-8"))
        self.checksum = self.calculate_checksum()

    def calculate_checksum(self):
        data_bytes = self.data.encode("utf-8")
        self.length = 8 + len(data_bytes)

        udp_header = struct.pack(
            "!HHHH",
            self.source_port,
            self.destination_port,
            self.length,
            0
        )

        pseudo_header = (
            socket.inet_aton(self.source_ip)
            + socket.inet_aton(self.destination_ip)
            + struct.pack(
                "!BBH", 0, socket.IPPROTO_UDP, self.length
            )
        )

        packet = pseudo_header + udp_header + data_bytes

        if len(packet) % 2:
            packet += b"\x00"

        total = sum(
            (packet[i] << 8) + packet[i + 1]
            for i in range(0, len(packet), 2)
        )

        while total >> 16:
            total = (total & 0xFFFF) + (total >> 16)

        result = (~total) & 0xFFFF
        return result if result != 0 else 0xFFFF

    def is_valid(self):
        original_checksum = self.checksum
        expected_checksum = self.calculate_checksum()
        return original_checksum == expected_checksum