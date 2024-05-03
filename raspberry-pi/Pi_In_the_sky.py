# type: ignore
import board
import busio
#import adafruit_mpu6050
import digitalio
import time
import adafruit_mpl3115a2  # Import the MPL3115A2 library
import storage
import os

## Initialize I2C communication with the MPU6050 sensor
#sda_pinmpu = board.GP4  # Replace with your SDA pin
#scl_pinmpu = board.GP5  # Replace with your SCL pin
#i2cmpu = busio.I2C(scl_pinmpu, sda_pinmpu)
#mpu = adafruit_mpu6050.MPU6050(i2cmpu)  # Replace with your MPU6050 address
# Initialize I2C communication with the MPL3115A2 sensor
sda_pinmpl = board.GP14  # Replace with your SDA pin
scl_pinmpl = board.GP15  # Replace with your SCL pin
i2cmpl = busio.I2C(scl_pinmpl, sda_pinmpl)
# Initialize the MPL3115A2 altimeter
mpl3115a2 = adafruit_mpl3115a2.MPL3115A2(i2cmpl)

# Initialize the button for recording
databutton_pin = board.GP11  # Replace with the actual GPIO pin you are using
databutton = digitalio.DigitalInOut(databutton_pin)
databutton.direction = digitalio.Direction.INPUT
databutton.pull = digitalio.Pull.UP

# Initialize the Onboard Led and Led connected to GP16
led_pin = board.LED  # LED PIN = ONBOARD
led = digitalio.DigitalInOut(led_pin)
led.direction = digitalio.Direction.OUTPUT

led_2_pin = board.GP16  # LED PIN = GP16
led_2 = digitalio.DigitalInOut(led_2_pin)
led_2.direction = digitalio.Direction.OUTPUT

# Initialize the motor
motor_pin = board.GP13 # MOTOR PIN = GP13
motor = digitalio.DigitalInOut(motor_pin)
motor.direction = digitalio.Direction.OUTPUT

led.value = True
time.sleep(0.1)
led.value = False
time.sleep(0.1)
time.sleep(1.5) #Delay to help initialize values

# Store the initial altitude and time
initial_altitude = mpl3115a2.altitude
start_time = time.monotonic()
print(start_time)
# Flag to indicate recording status
recording = False
# Create or open the data.csv file in append mode
motor_start_time = None  # Variable to store the time when the motor starts

# Previous time for speed calculation
previous_time = time.monotonic()
# find which file number we're on
files = os.listdir("FlightData")
file_num = 0
for file in files:
    if file.startswith("flightdata-"):
        file_num += 1

with open(f"FlightData/flightdata-{file_num}.csv", "a") as datalog:
    # Main loop
    while True:
        ## Read acceleration values
        #acceleration = mpu.acceleration
        #x_acceleration, y_acceleration, z_acceleration = acceleration
        
        # Read altitude from MPL3115A2 altimeter in meters
        current_altitude_meters = mpl3115a2.altitude
        # Convert altitude to feet
        current_altitude = current_altitude_meters * 3.28084

        # Calculate time of flight
        current_time = time.monotonic()
        delta_time = current_time - previous_time  # Time difference between readings
        print(current_time)
        time_of_flight = current_time - start_time
        # Update previous time
        previous_time = current_time
        # Check if the button is pressed to start/stop recording
        if databutton.value == True and not recording:
            # Button pressed, start recording
            recording = True
            datalog.write("Time(s), Altitude(m)\n")
            motor.value = True
            motor_start_time = time.monotonic()  # Record the time when the motor starts
        elif not databutton.value == True and recording:
            # Button released, stop recording
            recording = False
            motor.value = False

        # Turn off the motor after 10 seconds
        if motor_start_time is not None and time.monotonic() - motor_start_time >= 1.5:
            motor.value = False
            motor_start_time = None  # Reset the motor start time

        # Record data if in recording mode
        if recording:
            data_string = f"{current_time:.3f}, {current_altitude:.3f}\n"
            datalog.write(data_string)
        # Flush the file to ensure data is saved
        datalog.flush()
        # Add a delay to control the loop frequency
        time.sleep(0.1)
