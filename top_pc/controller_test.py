from inputs import get_gamepad


def read_controller_inputs():
    while True:
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Key":
                print(f"Button {event.code} {'pressed' if event.state else 'released'}")
            elif event.ev_type == "Absolute":
                print(f"Axis {event.code} moved to {event.state}")


# Call the function to start reading controller inputs
read_controller_inputs()