# type: ignore
import board
import busio
import adafruit_mpu6050
import digitalio
import time
import adafruit_mpl3115a2
from analogio import AnalogIn
import storage

# Initialize I2C communication with the MPU6050 sensor
sda_pin = board.GP14  # Replace with your SDA pin
scl_pin = board.GP15  # Replace with your SCL pin
i2c = busio.I2C(scl_pin, sda_pin)
mpu = adafruit_mpu6050.MPU6050(i2c)  # Replace with your MPU6050 address

# Initialize the MPL3115A2 altimeter
mpl3115a2 = adafruit_mpl3115a2.MPL3115A2(i2c)

# Initialize the button for recording
button_pin = board.GP12  # Replace with the actual GPIO pin you are using
button = digitalio.DigitalInOut(button_pin)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP


# Store the initial altitude and time
initial_altitude = mpl3115a2.altitude
start_time = time.monotonic()

# Flag to indicate recording status
recording = False
# Create or open the data.csv file in append mode
with open("/flightdata.csv", "a") as datalog:
    # Main loop
    while True:
        # Read acceleration values
        acceleration = mpu.acceleration
        x_acceleration, y_acceleration, z_acceleration = acceleration

        # Read altitude from MPL3115A2 altimeter
        current_altitude = mpl3115a2.altitude

        # Calculate time of flight
        current_time = time.monotonic()
        time_of_flight = current_time - start_time

        # Check if the button is pressed to start/stop recording
        if button.value and not recording:
            # Button pressed, start recording
            recording = True
            datalog.write("Time(s), Altitude(m), X_Acceleration(m/s^2), Y_Acceleration(m/s^2), Z_Acceleration(m/s^2)\n")
        elif not button.value and recording:
            # Button released, stop recording
            recording = False

        # Record data if in recording mode
        if recording:
            data_string = f"{time_of_flight:.3f}, {current_altitude:.3f}, {x_acceleration:.3f}, {y_acceleration:.3f}, {z_acceleration:.3f}\n"
            datalog.write(data_string)
            
        # Flush the file to ensure data is saved
        datalog.flush()
        # Add a delay to control the loop frequency
        time.sleep(0.1)
