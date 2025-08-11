from inputs import get_gamepad
import time

class Controller:
    def __init__(self):
        self.connection = True
        print("Controller reading initialized")
        self.axis = {}
        self.button = {}
        self.active = True # controller is active by default
        self.hat = {}
        self._last_axis = {}

    def get_controller_values(self):
        try:
            events = get_gamepad()
        except OSError:
            # No events available, return immediately
            return
        for event in events:
            if event.ev_type == "Key":
                if event.code == "BTN_START" and event.state == 1:
                    self.active = not self.active
                    print("Controller active" if self.active else "Controller inactive")
            elif event.ev_type == "Absolute":
                # convert the axis values from -32767-32767 to -1 to 1
                value = event.state / 32769
                code_map = {
                    "ABS_Y": "0",
                    "ABS_X": "1",
                    "ABS_RY": "2",
                    "ABS_RX": "3"
                }
                if event.code in code_map:
                    idx = code_map[event.code]
                    # Only update if value changed
                    if self.axis.get(idx) != value:
                        self.axis[idx] = value
        # No sleep here; let caller control timing

# if __name__ == "__main__":
#     controller = Controller()
#     t = threading.Thread(target=controller.get_controller_values)
#     t.start()
# if __name__ == "__main__":
#     controller = Controller()
#     t = threading.Thread(target=controller.get_controller_values)
#     t.start()
