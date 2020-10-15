import socket
import threading
import cv2
import time
# for tello access
tello_ip = '192.168.10.1'
tello_port = 8889
tello_address = (tello_ip, tello_port)
# for receiving from tello
VS_UDP_IP = '0.0.0.0'
VS_UDP_PORT = 11111
# Prepare objects for VideoCapture
cap = None
# Prepare objects for receiving data
response = None
# Create a socket for communication
# * Address family: AF_INET (IPv4), Socket type: SOCK_DGRAM (UDP)
socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
# Set to listen
socket.bind (('', tello_port))
# Data receiving function
def run_udp_receiver ():
    while True:
        try:
            response, _ = socket.recvfrom (1024)
            print(response)
        except Exception as e:
            print (e)
            break
thread = threading.Thread (target = run_udp_receiver, args = ())
thread.daemon = False
thread.start ()
# Throw 'command' text to use command mode
socket.sendto ('command'.encode (' utf-8 '), tello_address)
time.sleep(2)
# Start video streaming
socket.sendto ('streamon'.encode (' utf-8 '), tello_address)
time.sleep(2)
socket.sendto ('temp?'.encode (' utf-8 '), tello_address)

udp_video_address = 'udp: // @' + VS_UDP_IP + ':' + str (VS_UDP_PORT)

if cap is None:
    cap = cv2.VideoCapture ('udp://@:11111')
if not cap.isOpened ():
    cap.open ('udp://@:11111')
while True:
    ret, frame = cap.read ()
    cv2.imshow ('frame', frame)
    if cv2.waitKey (1)&0xFF == ord ('q'):
        break
cap.release ()
cv2.destroyAllWindows ()
# Stop video streaming
socket.sendto ('streamoff'.encode (' utf-8 '), tello_address)
