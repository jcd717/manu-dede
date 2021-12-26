
from flask import session,current_app


import os, time, subprocess, re, uuid, glob
from datetime import datetime


youtube_dl_app='youtube-dl' # -P ne marche pas
youtube_dl_app='yt-dlp'



class Download:
    def __init__(self,url) -> None:
        self.urlEnCours=url
        self.log_stdout=self.log_stderr=''
        self.process=self.destination=self.lastETA=None

    def __str__(self) -> str:
        return str(self.__dict__)

'''
Lorsqu'un download est en cours les variables de session suivantes existent:
idDownload

Lorsque le download est terminé, les détruire avec del
'''


# def telecharger(url):
# # ajouter à la ligne de commande:
# # --no-playlist 
# # --no-colors
# # --newline
# # -P chemin
#     idDownload=uuid.uuid4()
#     session['idDownload']=idDownload
#     current_app.downloads[idDownload]=Download(url)

#     cmd= youtube_dl_app,'--no-playlist','--no-colors','--newline','-P '+current_app.downloadsPath,url
#     process = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
#     current_app.downloads[idDownload].process=process

#     os.set_blocking(process.stdout.fileno(), False)
#     current_app.downloads[idDownload].log_stdout=''
#     destinationRecue = etaRecue = False
#     while not destinationRecue and process.poll()==None:
#         line = process.stdout.readline()
#         if line!='':
#             current_app.downloads[idDownload].log_stdout += line
#             destination=getDestination(line)
#             if destination!=None:
#                 destinationRecue=True
#                 current_app.downloads[idDownload].destination=destination
#             else:
#                 time.sleep(0.05)
#     if not destinationRecue: # à priori url déjà téléchargée
#         rc=process.wait()
#         if rc==0:
#             os.set_blocking(process.stdout.fileno(), False)
#             print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] [à priori url déjà téléchargée]: rc={rc} url={url}')
#             reste=process.stdout.read()
#             current_app.downloads[idDownload].log_stdout += reste
#             # je ne prend pas stderr
#             video='Mystère'
#             for line in reste.splitlines():
#                 video=getRegex(r'^\[download\].+downloads/(.+) has already been downloaded$',line)
#                 break
#             return f"L'URL \"{url}\" de la vidéo \"{video}\" est déjà téléchargée"
    
#     error=refreshDownload(current_app.downloads[idDownload])
#     return error

def telecharger(url):
# ajouter à la ligne de commande:
# --no-playlist 
# --no-colors
# --newline
# -P chemin
    idDownload=uuid.uuid4()
    session['idDownload']=idDownload
    current_app.downloads[idDownload]=Download(url)

    cmd= youtube_dl_app,'--no-playlist','--no-colors','--newline','-P '+current_app.downloadsPath,url
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    current_app.downloads[idDownload].process=process

    destinationRecue = False
    while not destinationRecue and process.poll()==None:
        try:
            out,err=process.communicate(timeout=0.1)
        except subprocess.TimeoutExpired: pass
        print('OUT')
        print('---')
        print(out)
        print('--------------------------------------')
        print('ERR')
        print('---')
        print(err)
        print('--------------------------------------')
        time.sleep(0.05)
    #     if line!='':
    #         current_app.downloads[idDownload].log_stdout += line
    #         destination=getDestination(line)
    #         if destination!=None:
    #             destinationRecue=True
    #             current_app.downloads[idDownload].destination=destination
    #         else:
    #             time.sleep(0.05)
    # if not destinationRecue: # à priori url déjà téléchargée
    #     rc=process.wait()
    #     if rc==0:
    #         os.set_blocking(process.stdout.fileno(), False)
    #         print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] [à priori url déjà téléchargée]: rc={rc} url={url}')
    #         reste=process.stdout.read()
    #         current_app.downloads[idDownload].log_stdout += reste
    #         # je ne prend pas stderr
    #         video='Mystère'
    #         for line in reste.splitlines():
    #             video=getRegex(r'^\[download\].+downloads/(.+) has already been downloaded$',line)
    #             break
    #         return f"L'URL \"{url}\" de la vidéo \"{video}\" est déjà téléchargée"
    
    # error=refreshDownload(current_app.downloads[idDownload])
    # return error
    return "Arrêt programmé"

   
def refreshDownload(download:Download):
    etaRecue = False
    error=None
    while not etaRecue and download.process.poll()==None:
        line = download.process.stdout.readline()
        if line!='':
            download.log_stdout += line
            eta=getETA(line)
            if eta!=None:
                etaRecue=True
                download.lastETA=eta
            else:
                time.sleep(0.05)
    print(download.log_stdout)
    if not etaRecue: # le process est terminé
        os.set_blocking(download.process.stdout.fileno(), False)
        rc=download.process.wait()
        if rc==0:
            reste=download.process.stdout.read()
            download.log_stdout += reste
            for line in reste.splitlines():
                newDest=getMerger(line)
                if newDest!=None:
                    download.destination=newDest
                    break
            print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] [RECU]: url={download.urlEnCours}')
            print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] [RECU]: {download.destination}')
            # faire le lien symbolique
            src=download.destination
            dst=current_app.staticDownloadPath+'/'+os.path.basename(download.destination)
            os.symlink(src,dst)
        else:
            print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] [ERROR]: rc={rc} url={download.urlEnCours}')
            error=download.process.stderr.read()
            print(error)
            error=f"\"{download.urlEnCours}\" n'existe pas!"

        del download
        del session['idDownload']

        return error
        


def getDestination(line):
    '''
    retourne None si elle n'est pas présente
    sinon le chemin complet
    '''
    return getRegex(r"^\[download\] Destination: (.+)$",line)
    

def getETA(line):
    '''
    retourne None si elle n'est pas présente
    sinon ETA trouvée
    '''
    return getRegex(r"^\[download\].*ETA (\d.*)$",line)

def getMerger(line):
    return getRegex(r"^\[Merger\].*into \"(.+)\"$",line)

def getRegex(regex,line):
    dest=re.match(regex,line)
    return None if dest==None else dest.groups()[0]


def deleteFiles(fileName):
    fileName=os.path.basename(fileName)
    precedent=''
    while fileName!=precedent:
        fileName , precedent=os.path.splitext(fileName)[0] , fileName
    names=glob.glob(current_app.downloadsPath+'/'+glob.escape(fileName)+'.*')
    for f in names:
        os.remove(f)

