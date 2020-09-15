import os
import tqdm
import socket
from threading import Thread

clients = []
BUFFER_SIZE = 4096
SEPARATOR = '<SEPARATOR>'


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket, filename, filesize):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name
        if os.path.isfile(filename):
            i = 1
            name, ext = filename.split('.')
            while True:
                tmp_name = f'{name}_copy{i}.{ext}'
                i += 1
                if not os.path.isfile(tmp_name):
                    self.filename = tmp_name
                    break
        else:
            self.filename = filename
        self.filesize = filesize

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(
            range(self.filesize),
            f'Receiving {self.filename}',
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        )
        with open(self.filename, 'wb') as f:
            for _ in progress:
                # read 1024 bytes from the socket (receive)
                bytes_read = self.sock.recv(BUFFER_SIZE)
                if not bytes_read:
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
        self._close()
        return


def main():
    # receive 4096 bytes each time
    server_host = '0.0.0.0'
    server_port = 8800

    next_name = 1

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address;
    # in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind((server_host, server_port))
    sock.listen()
    print(f'[*] Listening as {server_host}:{server_port}')
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        # receive the file infos
        # receive using client socket, not server socket
        received = con.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)
        # start new thread to deal with client
        ClientListener(name, con, filename, filesize).start()


if __name__ == '__main__':
    main()
