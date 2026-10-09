import json


class FSMEngine:

    def __init__(self, definition_file):
        with open(definition_file, "r", encoding="utf-8") as file:
            self.definition = json.load(file)

        self.state = self.definition["initial_state"]

    def trigger(self, event):
        states = self.definition["states"]

        if event not in states[self.state]:
            print(
                f"Evento '{event}' inválido "
                f"para o estado '{self.state}'"
            )
            return False

        transition = states[self.state][event]

        old_state = self.state
        action = transition["action"]
        self.state = transition["next_state"]

        print(
            f"{old_state} --{event}/{action}--> {self.state}"
        )

        return True