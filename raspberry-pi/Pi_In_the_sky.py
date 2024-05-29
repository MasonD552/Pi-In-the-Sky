#type: ignore
# Import necessary libraries
import board
import busio
import digitalio
import time
import mpl3115a2_highspeed as adafruit_mpl3115a2
import storage
import os
import adafruit_logging as logging

# Set up logging
logger = logging.getLogger('flight')
logger.setLevel(logging.INFO)

# Define FlightDataRecorder class
class FlightDataRecorder:
    def __init__(self):
        # Initialize pins and sensors
        self.databutton_pin = board.GP11
        self.databutton = self.setup_digital_io_button(self.databutton_pin)
        self.led_pin = board.LED
        self.led = self.setup_digital_io_output(self.led_pin)
        self.motor_pin = board.GP13
        self.motor = self.setup_digital_io_output(self.motor_pin)
        self.i2cmpl = self.setup_i2c(board.GP14, board.GP15)
        self.mpl3115a2 = adafruit_mpl3115a2.MPL3115A2(self.i2cmpl)
        self.initial_altitude = self.mpl3115a2.altitude
        self.start_time = time.monotonic()
        self.previous_time = time.monotonic()
        self.recording = False
        self.motor_start_time = None
        self.file_num = self.get_file_num()
        self.launch_altitude = None
    # Function to set up a digital input pin
    def setup_digital_io_button(self, pin):
        io = digitalio.DigitalInOut(pin)
        io.direction = digitalio.Direction.INPUT
        io.pull = digitalio.Pull.UP
        io.switch_to_input(pull=digitalio.Pull.UP)
        return io
    
    def button_pressed(self, pin):
        self.launch_altitude = self.mpl3115a2.altitude
        self.recording = True

    # Function to set up a digital output pin
    def setup_digital_io_output(self, pin):
        io = digitalio.DigitalInOut(pin)
        io.direction = digitalio.Direction.OUTPUT
        return io

    # Function to set up I2C
    def setup_i2c(self, sda_pin, scl_pin):
        return busio.I2C(scl_pin, sda_pin)

    # Function to get the file number for the data log
    def get_file_num(self):
        files = os.listdir("FlightData")
        file_num = sum(file.startswith("flightdata-") for file in files)
        return file_num

  # Function to record flight data
    def record_flight_data(self):
        with open(f"FlightData/flightdata-{self.file_num}.csv", "a") as datalog:
            while True:
                current_time = time.monotonic()
                delta_time = current_time - self.previous_time
                time_of_flight = current_time - self.start_time
                self.previous_time = current_time

                # Check if the button is pressed to start/stop recording
                if self.databutton.value and not self.recording:
                    self.recording = True
                    # Set the launch altitude
                    self.launch_altitude = self.mpl3115a2.altitude
                    # Check if the file is empty before writing the header
                    if datalog.tell() == 0:
                        datalog.write("Time(s), Altitude(ft)\n")
                    self.motor.value = True
                    self.motor_start_time = time.monotonic()
                elif not self.databutton.value and self.recording:
                    self.recording = False
                    self.motor.value = False

                # Check if the motor should be turned off
                if self.motor_start_time and time.monotonic() - self.motor_start_time >= 1.5:
                    self.motor.value = False
                    self.motor_start_time = None

                # Record data if in recording mode
                if self.recording:
                    # Calculate the altitude relative to the launch altitude
                    relative_altitude = self.mpl3115a2.altitude - self.launch_altitude
                    data_string = f"{current_time:.3f}, {relative_altitude:.3f}\n"
                    datalog.write(data_string)

                # Flush the data log and sleep for a short time
                datalog.flush()
                time.sleep(0.1)

# Main program
if __name__ == "__main__":
    recorder = FlightDataRecorder()
    recorder.record_flight_data()
