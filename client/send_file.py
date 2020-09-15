import socket
import tqdm
import sys
import os


def send(
    s,
    filename,
    separator='<SEPARATOR>',
    buffer_size=4096,
):
    # get the file size
    filesize = os.path.getsize(filename)

    # send the filename and filesize
    s.send(f'{filename}{separator}{filesize}'.encode())

    # start sending the file
    progress = tqdm.tqdm(
        range(filesize),
        f'Sending {filename}',
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    )

    with open(filename, 'rb') as f:
        for _ in progress:
            # read the bytes from the file
            bytes_read = f.read(buffer_size)
            if not bytes_read:
                # file transmitting is done
                print('Finished')
                break
            # we use sendall to assure transimission in
            # busy networks
            s.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))


def main(argv):
    if len(sys.argv) != 4:
        print(f'Usage: {argv[0]} filename ip port')
        exit(1)

    filename, ip, port = argv[1:4]
    port = int(port)

    # create the client socket
    s = socket.socket()

    print(f'[+] Connecting to {ip}:{port}')
    s.connect((ip, port))
    print('[+] Connected.')

    send(s, filename)

    # close the socket
    s.close()


if __name__ == '__main__':
    main(sys.argv)
