from inputs import get_gamepad
import time

class Controller:
    def __init__(self):

        self.connection = True
        
        # # check if controller is connected
        # while self.connection:
        #     try:
        #         get_gamepad()
        #     except:
        #         self.connection = False
        #         print("Controller not connected")
        #         time.sleep(5)
        print("Controller reading initialized")
                

        self.axis = {}
        self.button = {}
        self.active = False
        self.hat = {}

    def get_controller_values(self):
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Key":
                if event.code == "BTN_BASE4" and event.state == 1:
                    self.active = not self.active
                    print("Controller active" if self.active else "Controller inactive")
            elif event.ev_type == "Absolute":
                # convert the axis values from 0-255 to -1 to 1
                value = (event.state - 127.5) / 127.5
                if event.code == "ABS_X":
                    self.axis["0"] = value
                elif event.code == "ABS_Y":
                    self.axis["1"] = value
                elif event.code == "ABS_Z":
                    self.axis["2"] = value
                elif event.code == "ABS_RZ":
                    self.axis["3"] = value

# if __name__ == "__main__":
#     controller = Controller()
#     t = threading.Thread(target=controller.get_controller_values)
#     t.start()
