from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app
)

import os
from datetime import datetime


from manu_dede.download import telecharger,refreshDownload, deleteFiles

bp = Blueprint('manu_dede', __name__)


@bp.route('/',methods = ['GET'])
def index():
    def remplirG():
        g.download=current_app.downloads[session['idDownload']]
        g.nomFichier=os.path.basename(g.download.destination)
    
    url=request.args.get('url')
    if url != None and session.get('idDownload')==None:
        ok=telecharger(url) # remplit session['idDownload'] et la supprime si erreur
        if ok==None:
            remplirG()
        else:
            # afficher le flash error
            flash(ok)
            if session.get('idDownload')!=None:
                del session['idDownload']
        return redirect(request.path) # pour supprimer le paramètre dans l'URL

    if session.get('idDownload')!=None:
        refreshDownload(current_app.downloads[session['idDownload']])
        if session.get('idDownload')!=None:
            if request.args.get('cancel')==None:
                remplirG()
            else: # annulation, le lien symbolique n'est pas fait
                print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] [ANNULATION]: url={current_app.downloads[session["idDownload"]].urlEnCours}')
                print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] [ANNULATION]: {current_app.downloads[session["idDownload"]].destination}')
                current_app.downloads[session["idDownload"]].process.kill()
                current_app.downloads[session["idDownload"]].process.communicate() # pour lire rc sinon zombie
                deleteFiles(current_app.downloads[session["idDownload"]].destination)
                del current_app.downloads[session["idDownload"]]
                del session['idDownload']
                return redirect(request.path) # pour supprimer le paramètre dans l'URL
    
    g.urls=getListDownloads()
    return render_template('manu-dede.j2')


def getListDownloads():
    '''
    Retoune la liste des fichiers dans static/downloads triés antéchronologique selon st_ctime
    ou None si vide
    '''
    files=os.listdir(current_app.staticDownloadPath)
    if len(files)==0:
        return None
    res=[]
    for f in files:
        res.append({'stat': os.stat(current_app.staticDownloadPath+'/'+f),
                    'nom': f,
                    'url': url_for('static',filename='downloads/'+f)
        })
    res=sorted(res,reverse=True, key=lambda k: k['stat'].st_ctime  )
    return res
    


