import os
import time
import subprocess

#cmd = 'python3', '-c', 'import time; [(print((i+1)*123), time.sleep(1)) for i in range(5)]'

yt='youtube-dl'
yt='yt-dlp'

cmd= yt,'--no-playlist','--no-colors','--newline','-P /tmp',"https://www.youtube.com/watch?v=Hhbz5Sah3dw"
p = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
os.set_blocking(p.stdout.fileno(), False)
#start = time.time()
# while True:
#     # first iteration always produces empty byte string in non-blocking mode
#     for i in range(2):    
#         line = p.stdout.readline()
#         print(i, line)
#         time.sleep(0.5)
#     if time.time() > start + 5:
#         break
#p.terminate()

# ma version

while p.poll()==None:
  time.sleep(0.2)
  line = p.stdout.readline()
  if line=='':
    print('rien...')
  else:
    print('reçu:',line)

rc=p.wait()
print('rc=',rc)
print('stdout:',p.stdout.read())
print('stderr:',p.stderr.read())
