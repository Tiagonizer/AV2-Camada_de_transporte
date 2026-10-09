
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Localiza a pasta fsm_udp_tcp independentemente de onde
# o programa for iniciado.
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from fsm_engine import FSMEngine
from protocols.udp import UDPDatagram
from channel import Channel


class NetworkSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Redes Convergentes - UDP/TCP")
        self.root.geometry("1000x720")
        self.root.minsize(800, 600)

        self.protocol_var = tk.StringVar(value="TCP")
        self.state_var = tk.StringVar(value="-")
        self.event_var = tk.StringVar()

        self.loss_var = tk.StringVar(value="0")
        self.corruption_var = tk.StringVar(value="0")
        self.duplication_var = tk.StringVar(value="0")
        self.reordering_var = tk.StringVar(value="0")
        self.min_delay_var = tk.StringVar(value="0")
        self.max_delay_var = tk.StringVar(value="0")
        self.seed_var = tk.StringVar(value="42")

        self.engine = None
        self.channel = None

        self.create_interface()
        self.load_protocol()
        self.create_channel()

    def create_interface(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        # Cabeçalho
        ttk.Label(
            main,
            text="Simulador de Redes Convergentes",
            font=("Arial", 18, "bold")
        ).pack(anchor="w")

        ttk.Label(
            main,
            text="Máquina de estados finitos e canal de comunicação"
        ).pack(anchor="w", pady=(0, 12))

        # Seleção de protocolo e estado
        protocol_frame = ttk.LabelFrame(
            main, text="Protocolo", padding=10
        )
        protocol_frame.pack(fill="x", pady=5)

        ttk.Label(protocol_frame, text="Protocolo:").pack(
            side="left"
        )

        protocol_box = ttk.Combobox(
            protocol_frame,
            textvariable=self.protocol_var,
            values=["UDP", "TCP"],
            state="readonly",
            width=12
        )
        protocol_box.pack(side="left", padx=8)
        protocol_box.bind(
            "<<ComboboxSelected>>",
            lambda event: self.load_protocol()
        )

        ttk.Label(
            protocol_frame, text="Estado atual:"
        ).pack(side="left", padx=(20, 5))

        ttk.Label(
            protocol_frame,
            textvariable=self.state_var,
            font=("Arial", 13, "bold")
        ).pack(side="left")

        # Controles da máquina de estados
        fsm_frame = ttk.LabelFrame(
            main, text="Controle da máquina de estados", padding=10
        )
        fsm_frame.pack(fill="x", pady=5)

        ttk.Label(fsm_frame, text="Evento:").pack(side="left")

        self.event_box = ttk.Combobox(
            fsm_frame,
            textvariable=self.event_var,
            state="readonly",
            width=25
        )
        self.event_box.pack(side="left", padx=8)

        ttk.Button(
            fsm_frame,
            text="Executar evento",
            command=self.execute_event
        ).pack(side="left", padx=4)

        ttk.Button(
            fsm_frame,
            text="Reiniciar protocolo",
            command=self.load_protocol
        ).pack(side="left", padx=4)

        
        # Diagrama visual da máquina de estados
        graph_frame = ttk.LabelFrame(
            main, text="Diagrama da máquina de estados", padding=5
        )
        graph_frame.pack(fill="x", pady=5)

        self.fsm_canvas = tk.Canvas(
            graph_frame,
            height=350,
            background="white",
            highlightthickness=0
        )
        self.fsm_canvas.pack(fill="x", expand=True)

        # Configuração do canal
        channel_frame = ttk.LabelFrame(
            main, text="Configuração do canal (%)", padding=10
        )
        channel_frame.pack(fill="x", pady=5)

        fields = [
            ("Perda", self.loss_var),
            ("Corrupção", self.corruption_var),
            ("Duplicação", self.duplication_var),
            ("Reordenação", self.reordering_var),
            ("Atraso mínimo (ms)", self.min_delay_var),
            ("Atraso máximo (ms)", self.max_delay_var),
            ("Semente aleatória", self.seed_var),
        ]

        for index, (label, variable) in enumerate(fields):
            row = index // 4
            column = (index % 4) * 2

            ttk.Label(
                channel_frame, text=label + ":"
            ).grid(
                row=row, column=column,
                sticky="w", padx=4, pady=5
            )

            ttk.Entry(
                channel_frame,
                textvariable=variable,
                width=10
            ).grid(
                row=row, column=column + 1,
                sticky="w", padx=4, pady=5
            )

        ttk.Button(
            channel_frame,
            text="Aplicar configuração",
            command=self.create_channel
        ).grid(
            row=2, column=0, columnspan=2,
            sticky="w", padx=4, pady=5
        )

        ttk.Button(
            channel_frame,
            text="Descartar próximo pacote",
            command=self.drop_next
        ).grid(
            row=2, column=2, columnspan=2,
            sticky="w", padx=4, pady=5
        )

        ttk.Button(
            channel_frame,
            text="Enviar datagrama de teste",
            command=self.test_channel
        ).grid(
            row=2, column=4, columnspan=2,
            sticky="w", padx=4, pady=5
        )

        ttk.Button(
            channel_frame,
            text="Liberar retidos",
            command=self.flush_channel
        ).grid(
            row=2, column=6, columnspan=2,
            sticky="w", padx=4, pady=5
        )

        # Registo
        log_frame = ttk.LabelFrame(
            main, text="Registo de eventos", padding=8
        )
        log_frame.pack(fill="both", expand=True, pady=5)

        self.log = tk.Text(
            log_frame,
            height=15,
            wrap="word",
            state="disabled",
            font=("Consolas", 10)
        )
        self.log.pack(
            side="left", fill="both", expand=True
        )

        scrollbar = ttk.Scrollbar(
            log_frame,
            orient="vertical",
            command=self.log.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.log.configure(yscrollcommand=scrollbar.set)

        ttk.Button(
            main,
            text="Limpar registo",
            command=self.clear_log
        ).pack(anchor="e", pady=4)

    def log_message(self, message):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def load_protocol(self):
        protocol = self.protocol_var.get().lower()
        definition_path = os.path.join(
            PROJECT_DIR, "definitions", protocol + ".json"
        )

        try:
            self.engine = FSMEngine(definition_path)
            self.state_var.set(self.engine.state)
            self.update_events()
            self.draw_fsm()

            self.log_message(
                f"\n--- Protocolo {protocol.upper()} iniciado ---"
            )
            self.log_message(
                f"Estado inicial: {self.engine.state}"
            )
        except Exception as error:
            messagebox.showerror(
                "Erro ao carregar protocolo", str(error)
            )

    def update_events(self):
        states = self.engine.definition["states"]
        current_state = self.engine.state
        events = list(states.get(current_state, {}).keys())

        self.event_box["values"] = events

        if events:
            self.event_var.set(events[0])
        else:
            self.event_var.set("")

    
    
    def draw_fsm(self):
        canvas = self.fsm_canvas
        canvas.delete("all")

        if self.engine is None:
            return

        states = self.engine.definition["states"]
        current = self.engine.state
        protocol = self.protocol_var.get()

        if protocol == "UDP":
            positions = {
                "READY": (450, 125)
            }
        else:
            # Distribuição em linhas para reduzir cruzamentos.
            positions = {
                "CLOSED": (90, 60),
                "LISTEN": (270, 60),
                "SYN_SENT": (450, 60),
                "SYN_RCVD": (630, 60),
                "ESTABLISHED": (810, 60),
                "CLOSE_WAIT": (90, 170),
                "TIME_WAIT": (270, 170),
                "CLOSING": (450, 170),
                "FIN_WAIT_2": (630, 170),
                "FIN_WAIT_1": (810, 170),
                "LAST_ACK": (90, 280)
            }

        # Legenda
        canvas.create_rectangle(
            15, 310, 30, 325,
            fill="#bbf7d0",
            outline="#15803d",
            width=2
        )
        canvas.create_text(
            38, 317,
            text="Estado atual",
            anchor="w",
            font=("Arial", 9)
        )

        canvas.create_rectangle(
            160, 310, 175, 325,
            fill="#f1f5f9",
            outline="#64748b"
        )
        canvas.create_text(
            183, 317,
            text="Outros estados",
            anchor="w",
            font=("Arial", 9)
        )

        canvas.create_line(
            330, 317, 370, 317,
            arrow=tk.LAST,
            fill="#64748b",
            width=2
        )
        canvas.create_text(
            380, 317,
            text="Transição",
            anchor="w",
            font=("Arial", 9)
        )

        # Desenha as transições antes dos estados.
        for origin, events in states.items():
            if origin not in positions:
                continue

            x1, y1 = positions[origin]

            for event, transition in events.items():
                destination = transition["next_state"]

                if destination not in positions:
                    continue

                x2, y2 = positions[destination]

                # Transição que retorna ao mesmo estado.
                if origin == destination:
                    canvas.create_arc(
                        x1 - 22, y1 - 43,
                        x1 + 22, y1 - 3,
                        start=0,
                        extent=300,
                        style="arc",
                        outline="#64748b",
                        width=1.5
                    )
                    canvas.create_text(
                        x1, y1 - 47,
                        text=event,
                        font=("Arial", 8),
                        fill="#334155"
                    )
                    continue

                dx = x2 - x1
                dy = y2 - y1
                distance = max((dx * dx + dy * dy) ** 0.5, 1)

                # Ajusta o início e o fim para as setas
                # não atravessarem o interior das caixas.
                start_x = x1 + dx / distance * 55
                start_y = y1 + dy / distance * 22
                end_x = x2 - dx / distance * 55
                end_y = y2 - dy / distance * 22

                canvas.create_line(
                    start_x, start_y,
                    end_x, end_y,
                    arrow=tk.LAST,
                    fill="#94a3b8",
                    width=1.5
                )

                label_x = (start_x + end_x) / 2
                label_y = (start_y + end_y) / 2 - 9

                canvas.create_text(
                    label_x, label_y,
                    text=event,
                    font=("Arial", 7),
                    fill="#334155"
                )

        # Desenha os estados por cima das setas.
        for state, (x, y) in positions.items():
            if state not in states:
                continue

            is_current = state == current

            fill = "#bbf7d0" if is_current else "#f1f5f9"
            outline = "#15803d" if is_current else "#64748b"
            line_width = 3 if is_current else 1

            canvas.create_rectangle(
                x - 53, y - 22,
                x + 53, y + 22,
                fill=fill,
                outline=outline,
                width=line_width
            )

            canvas.create_text(
                x, y,
                text=state,
                font=("Arial", 9, "bold"),
                fill="#172033"
            )

        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

        
    def execute_event(self):
        if self.engine is None:
            return

        event = self.event_var.get()
        if not event:
            messagebox.showwarning(
                "Evento", "Selecione um evento."
            )
            return

        old_state = self.engine.state
        transitions = self.engine.definition["states"]
        transition = transitions.get(old_state, {}).get(event)

        if transition is None:
            self.engine.trigger(event)
            self.log_message(
                f"Evento inválido: {event} no estado {old_state}"
            )
            return

        action = transition["action"]
        next_state = transition["next_state"]

        success = self.engine.trigger(event)

        if success:
            self.log_message(
                f"{old_state} --{event}/{action}--> {next_state}"
            )

        self.state_var.set(self.engine.state)
        self.update_events()
        self.draw_fsm()

    def create_channel(self):
        try:
            probabilities = [
                float(self.loss_var.get()),
                float(self.corruption_var.get()),
                float(self.duplication_var.get()),
                float(self.reordering_var.get())
            ]

            if any(value < 0 or value > 100
                   for value in probabilities):
                raise ValueError(
                    "As probabilidades devem estar entre 0 e 100."
                )

            min_delay = int(self.min_delay_var.get())
            max_delay = int(self.max_delay_var.get())
            seed_text = self.seed_var.get().strip()
            seed = int(seed_text) if seed_text else None

            self.channel = Channel(
                loss_probability=probabilities[0] / 100,
                corruption_probability=probabilities[1] / 100,
                duplication_probability=probabilities[2] / 100,
                reordering_probability=probabilities[3] / 100,
                min_delay=min_delay,
                max_delay=max_delay,
                seed=seed
            )

            self.log_message(
                "\nConfiguração do canal aplicada."
            )
        except (ValueError, TypeError) as error:
            messagebox.showerror(
                "Configuração inválida", str(error)
            )

    def drop_next(self):
        if self.channel is not None:
            self.channel.drop_next_packet()
            self.log_message(
                "CANAL: próximo pacote será descartado."
            )

    def test_channel(self):
        if self.channel is None:
            return

        packet = UDPDatagram(
            1025, 80, "Mensagem de teste"
        )

        self.log_message("\nEnviando datagrama pelo canal...")
        results = self.channel.transmit(packet)

        if not results:
            self.log_message(
                "Nenhum pacote entregue nesta transmissão."
            )
            return

        for received, delay in results:
            if not received.is_valid():
                self.log_message(
                    "RECEPTOR: datagrama corrompido descartado "
                    "por checksum inválido."
                )
            else:
                self.log_message(
                    f"RECEPTOR: datagrama válido; atraso informado: "
                    f"{delay} ms."
                )

    def flush_channel(self):
        if self.channel is None:
            return

        packets = self.channel.flush()

        if not packets:
            self.log_message("Não há pacotes retidos.")
            return

        for packet, delay in packets:
            if hasattr(packet, "is_valid") and not packet.is_valid():
                self.log_message(
                    "RECEPTOR: pacote retido corrompido descartado."
                )
            else:
                self.log_message(
                    f"Pacote retido liberado; atraso: {delay} ms."
                )


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkSimulator(root)
    root.mainloop()