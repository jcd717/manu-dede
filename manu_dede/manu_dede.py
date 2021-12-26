from flask import g,render_template, Blueprint, request, session, flash, redirect, current_app, url_for

import os

from .download import telecharger
from .db.db import insertDB,deleteDB


bp = Blueprint('manu_dede', __name__)


@bp.route('/delete/<string:nom>',methods=['GET'])
def delete(nom):
    files=getListFiles()
    if files==None or nom not in files:
        current_app.logger.error(f'{request.remote_addr} - ECHEC SUPPRESSION - {nom} - {request.user_agent}')
    else:
        current_app.logger.info(f'{request.remote_addr} - SUPPRESSION - {nom} - {request.user_agent}')
        file=current_app.staticDownloadPath+'/'+nom
        os.remove(file)
        file=current_app.downloadsPath+'/'+nom
        os.remove(file)
        deleteDB(nom)
    return redirect(url_for('homepage'))


@bp.route('/',methods = ['GET'])
def index():
    current_app.logger.debug(f'{request.remote_addr} - {request.url} - {request.user_agent}')
    url=request.args.get('url')
    if url != None and session.get('idDownload')==None:
        error,fileName=telecharger(url) # remplit session['idDownload'] et la supprime à la fin
        if error!=None:
            # afficher le flash error
            flash(error)
            if session.get('idDownload')!=None:
                del session['idDownload']
        else:
            insertDB(url,fileName)
        return redirect(request.path) # pour supprimer le paramètre dans l'URL
    elif session.get('idDownload')!=None:
        flash(f"PATIENCE, il y a une récupération en cours !!! -> {current_app.downloads[session['idDownload']].urlEnCours}")

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


def getListFiles():
    '''
    Retoune la liste des fichiers dans static/downloads 
    ou None si vide
    '''
    files=os.listdir(current_app.staticDownloadPath)
    if len(files)==0:
        return None
    res=[]
    for f in files:
        res.append(f)
    return res
    


