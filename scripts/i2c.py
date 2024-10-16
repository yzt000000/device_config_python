import time

for i in range(1000):
    print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhh:%d" %i)
    read_i2c_disp(0x00)
    time.sleep(0.1)