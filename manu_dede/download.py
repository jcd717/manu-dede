from flask import session,current_app


import subprocess, re, uuid, os
from datetime import datetime


youtube_dl_app='youtube-dl' # -P ne marche pas
youtube_dl_app='yt-dlp'



class Download:
    def __init__(self,url) -> None:
        self.urlEnCours=url
        self.stdout=self.stderr=''
        self.process=self.destination=None

    def __str__(self) -> str:
        return str(self.__dict__)

'''
Lorsqu'un download est en cours les variables de session suivantes existent:
idDownload

Lorsque le download est terminé, les détruire avec del
'''


def telecharger(url,gererSession=True):
# ajouter à la ligne de commande:
# --no-playlist 
# --no-colors
# --newline
# -P chemin
    error=None
    idDownload=uuid.uuid4()
    if gererSession:
        session['idDownload']=idDownload
    download=Download(url)
    current_app.downloads[idDownload]=download

    cmd= youtube_dl_app,'--no-playlist','--no-colors','--newline','-P '+current_app.downloadsPath,url
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)   
    current_app.downloads[idDownload].process=process

    print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] [DOWNLOAD]: url={download.urlEnCours}')

    download.stdout,download.stderr = process.communicate() # ici l'attente dépend de la taille du download
    print('-----------------------------------------------------------------------------------')
    if process.returncode==0:
        print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] [RECU]: url={download.urlEnCours}')
        print('OUTPUT')
        print('------')
        print(download.stdout)
        for line in download.stdout.splitlines():
            dst=getMerger(line)
            if dst!=None:
                download.destination=dst
                break
            else:
                dst=getDestination(line)
                if dst!=None:
                    download.destination=dst
                    # pas de break pour avoir le dernier nom affiché
        # faire le lien symbolique
        if download.destination==None: # probablement que l'URL est déjà téléchargée
            for line in download.stdout.splitlines():
                deja=getAlready(line)
                if deja!=None:
                    error=f"Il semble que l'URL \"{download.urlEnCours}\" pour le fichier \"{deja}\" soit déjà téléchargée"
                    break
            else:
                error="Il y a un problème dans le lien symbolique"
        else:
            print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] [RECU]: destination={download.destination}')
            src=download.destination
            dst=current_app.staticDownloadPath+'/'+os.path.basename(download.destination)
            os.symlink(src,dst)

    else:
        print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] [ERROR]: rc={process.returncode} url={download.urlEnCours}')
        print('STDERR')
        print('------')
        print(download.stderr)
        error="Il y a un problème"
    print('-----------------------------------------------------------------------------------')

    del current_app.downloads[idDownload]
    if gererSession:
        del session['idDownload']
    return error , None if error is not None else os.path.basename(download.destination)



def getDestination(line):
    '''
    retourne None si elle n'est pas présente
    sinon le chemin complet
    '''
    return getRegex(r"^\[download\] Destination: (.+)$",line)
    
def getMerger(line):
    return getRegex(r"^\[Merger\].*into \"(.+)\"$",line)

def getAlready(line):
    return getRegex(r"^\[download\].+downloads/(.+) has already been downloaded$",line)

def getRegex(regex,line):
    dest=re.match(regex,line)
    return None if dest==None else dest.groups()[0]


