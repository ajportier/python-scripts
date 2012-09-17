#!/usr/bin/python
def testUDP(host,port):
    '''Checks a single UDP port to see if it is open'''
    import socket
    socket.setdefaulttimeout(2)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((host,int(port)))
        s.shutdown(2)
        return True
    except:
        return False

def testTCP(host,port):
    '''Checks a single TCP port to see if it is open'''
    import socket
    socket.setdefaulttimeout(2)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host,int(port)))
        s.shutdown(2)
        return True
    except:
        return False

def main():
    import sys
    host = sys.argv[1]
    tcp = [ 22, 53, 80, 443, 3306]
    udp = [ 53 ]
    for port in tcp:
        print host + " tcp " + str(port) + " : " + str(testTCP(host,port))
    for port in udp:
        print host + " udp " + str(port) + " : " + str(testUDP(host,port))

if __name__=='__main__':
    main()
