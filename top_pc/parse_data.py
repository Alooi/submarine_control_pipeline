class SensorDataParser:
    def __call__(self, data):
        return self.parse_sensor_data(data)

    def parse_sensor_data(self, data):
        # Split the data into lines
        lines = data.split("\n")[1:]  # Skip the first line

        # Initialize an empty dictionary
        sensor_data = {}

        # Loop through each line and split by colon
        for line in lines:
            if line:  # Check if the line is not empty
                key, value = line.split(": ")
                # Convert value to float or int if possible
                if value.isdigit():
                    sensor_data[key] = int(value)
                else:
                    try:
                        sensor_data[key] = float(value)
                    except ValueError:
                        sensor_data[key] = value  # Keep as string if conversion fails

        return sensor_data

# Usage
parser = SensorDataParser()
data = """header
temperature: 23.5
humidity: 45
status: OK"""
parsed_data = parser(data)
print(parsed_data)
