# Credut: https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data

def recvall(con,BUFFER_SIZE = 1024):
    data = b""
    while True:
        packet = con.recv(BUFFER_SIZE)
        data += packet
        if len(packet) < BUFFER_SIZE:
            break
    return data
