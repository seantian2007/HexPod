import serial
import time
ser = serial.Serial('/dev/cu.usbserial-120', 115200, timeout=1)
time.sleep(3)
ser.reset_input_buffer()
n = ser.write(b"1570,1460,1530\n")
print("wrote", n, "bytes")
print("reply:", repr(ser.readline()))
ser.close()