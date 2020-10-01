import socket
import threading
import time


class Tello:
    def __init__(self, local_ip, local_port):
        """
        Initiates the Tello class.
        The needed Sockets and Threads are created and/or started here.

        Args:
            local_ip (string): local ip address of the host.
            local_port (integer): local port of the host
        """

        self.local_ip = local_ip
        self.local_port = local_port
        self.local_video_port = 11111

        self.tello_address = ("192.168.10.1", 8889)


        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.local_ip, self.local_port))

        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.local_ip,self.local_video_port))

        self.socket.sendto(b"command",self.tello_address)
        self.socket.sendto(b"streamon",self.tello_address)

        self.response_thread = threading.Thread(target=self._response_thread)
        self.response_thread.daemon = True
        self.response_thread.start()

        self.battery_thread = threading.Thread(target=self._battery_thread)
        self.battery_thread.daemon = True
        self.battery_thread.start()

        self.response = None 

        self.TIME_OUT = .5
        self.MIN_BATTERY_LEVEL = 10

        self.abort_flag = False
        self.battery_low_flag = False


    def _response_thread(self):
        """
        Waits for response from the socket and assignes the response to a variable.
        """
        while True:
            try:
                self.response, _ = self.socket.recvfrom(3000)
            except socket.error as e:
                print(f"Error: {e}")

    def _battery_thread(self):
        """
        Checks the battery level.
        If the battery level gets low the drone will be forced to land.
        """
        while True:
            if self.get_battery_status() < self.MIN_BATTERY_LEVEL:
                self.land()
            time.sleep(20)


    def send_command(self, command):
        """
        Sends a command to the Tello API.

        Args:
            command (string): command to be send to the API.

        Returns:
            string: Response from Tello Drone: OK, ERROR or a specific value.
        """

        print(f"Sending command: {command}")

        self.abort_flag = False
        self.socket.sendto(command.encode("utf-8"), self.tello_address)

        timer = threading.Timer(self.TIME_OUT, self.set_abort_flag)
        
        timer.start()
        while self.response is None:
            if self.abort_flag:
                break

        timer.cancel()

        if self.response is None:
            response = "none"
        else:
            response = self.response.decode("utf-8")

        self.response = None
            
        return response

    
    def set_abort_flag(self):
        """
        Sets the abort flag used to determine if a command has timed out.
        """
        self.abort_flag = True



    def takeoff(self): 
        """
        Drone will takeoff

        Returns:
            string: Response from Tello Drone: OK or ERROR
        """

        return self.send_command("takeoff")

    def land(self):
        """
        Drone will slowly land

        Returns:
            string: Response from Tello Drone: OK or ERROR
        """

        return self.send_command("land")
    
    def emergency_stop(self):
        """
        Drones motor will imediately turned off

        Returns:
             string: Response from Tello Drone: OK or ERROR
        """

        return self.send_command("emergency")

    def up(self,distance):
        """
        Move the drone in upward direction for x centimeters.
        The range of [distance] can be between 20 and 500.

        Args:
            distance (integer): distance in centimeters
        Returns:
            string: Response from Tello Drone: OK or ERROR
        """

        return self.send_command(f"up {distance}")

    def down(self,distance):
        """
        Move the drone in downward direction for x centimeters.
        The range of [distance] can be between 20 and 500.

        Args:
            distance (integer): distance in centimeters

        Returns:
           string: Response from Tello Drone: OK or ERROR
        """

        return self.send_command(f"down {distance}")
    
    def left(self,distance):
        """
        Move the drone left for x centimeters.
        The range of [distance] can be between 20 and 500.

        Args:
            distance (integer): distance in centimeters

        Returns:
           string: Response from Tello Drone: OK or ERROR
        """

        return self.send_command(f"left {distance}")

    def right(self,distance):
        """
        Move the drone right for x centimeters.
        The range of [distance] can be between 20 and 500.

        Args:
            distance (integer): distance in centimeters

        Returns:
            string: Response from Tello Drone: OK or ERROR
        """

        return self.send_command(f"right {distance}")
    
    def forward(self,distance):
        """
        Move the drone forwards for x centimeters.
        The range of [distance] can be between 20 and 500.

        Args:
            distance (integer): distance in centimeters

        Returns:
            string: Response from Tello Drone: OK or ERROR
        """

        return self.send_command(f"forward {distance}")

    def back(self,distance):
        """
        Move the dron back for x centimeters.
        The range of [distance] can be between 20 and 500.

        Args:
            distance (integer): distance in centimeters

        Returns:
            string: Response from Tello Drone: OK or ERROR
        """
        return self.send_command(f"back {distance}")

    def cw(self,degrees):
        """
        Rotate the drone clock-wise for x degrees.
        The range of [degrees] can be between 1 and 360.

        Args:
            degree (integer): angle in degrees

        Returns:
            [type]: [description]
        """
        return self.send_command(f"cw {degrees}")

    def ccw(self,degrees):
        """
        Rotate the drone counter-clock-wise for x degrees.
        The range of [degrees] can be between 1 and 360.

        Args:
            degrees (integer): angles in degrees
        Returns:
            string: Response from Tello Drone: OK or ERROR
        """
        return self.send_command(f"ccw {degrees}")

    def stop(self):
        """
        Drone stops and hovers mid air.
        Can be called at any time.
        """

        return self.send_command("stop")

    def set_speed(self, velocity):
        """
        Sets velocity of the drone to x centimeters per second.
        Velocity can range between 10 and 100.

        Args:
            velocity (integer): velocity in centimeters per second

        Returns:
            string: Response from Tello Drone: OK or ERROR
        """

        return self.send_command(f"speed {velocity}")

    def get_battery_status(self):
        """
        Get the drones current battery level in percent.

        Returns:
            integer: battery level in percent
        """
        battery_life = self.send_command("battery?")

        return int(battery_life)
    
    def get_sdk_version(self):
        """
        Get the drones current sdk version.

        Returns:
            string: sdk version
        """
        sdk_version = self.send_command("sdk?")

        return sdk_version

        