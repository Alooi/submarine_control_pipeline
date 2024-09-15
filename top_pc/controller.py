import pygame
import threading
import time

class Controller:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        self.connection = False

        def check_joystick():
            if pygame.joystick.get_count() == 0:
                print("No joystick found")
            else:
                self.connection = True
    
        while not self.connection:
            time.sleep(5)
            check_joystick()

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print("Joystick Name:", self.joystick.get_name())
        print("Number of Axes:", self.joystick.get_numaxes())
        print("Number of Buttons:", self.joystick.get_numbuttons())
        print("Number of Hats:", self.joystick.get_numhats())
        
        self.axis = {}
        self.button = {}
        self.button[9] = False
        self.hat = {}
        
    def get_controller_values(self):
        pygame.event.pump()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self.axis[event.axis] = event.value
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.button[event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    self.button[event.button] = False
                elif event.type == pygame.JOYHATMOTION:
                    self.hat[event.hat] = event.value

if __name__ == "__main__":
    controller = Controller()
    t = threading.Thread(target=controller.get_controller_values)
    t.start()