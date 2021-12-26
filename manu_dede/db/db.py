import os
import requests
import sqlite3,csv
import click

from flask import current_app
#from flask import cli (inutile ?)
from flask.cli import with_appcontext

'''
Mode BOURRIN
Je fais une connection globale pour l'application, contrairement au tuto qui fait une connexion dans g (donc si j'ai bien compris par request)
donc problèmes potentiels de concurrence -> lenteur et/ou écritures concurrentes
'''


def get_db():
    #current_app.logger.debug("Début d'appel à get_db()")
    if current_app.config.get('db') is None:
        current_app.config['db'] = sqlite3.connect(
            current_app.DB_FILE,
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False # pour éviter l'erreur "sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread" mais mystère sur la concurrence
        )
        current_app.config['db'].row_factory = sqlite3.Row
    return current_app.config['db']


# def close_db(e=None):
#     db = current_app.config.get('db')
#     if db is not None:
#         db.close()
#     current_app.logger.debug("Fin d'appel à close_db()")


def init_db():
    # suppression des fichiers
    try:
        os.remove(current_app.DB_FILE)
    except: pass
    try:
        for dir in [current_app.staticDownloadPath,current_app.downloadsPath]:
            files=os.listdir(dir)
            for f in files:
                os.remove(dir+'/'+f)
    except: pass

    db = get_db()
    with current_app.open_resource('db/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def insertDB(url,fileName,save=True):
    db=get_db()
    db.execute(
         "insert into downloads(url,fileName) "
         "values(?,?) ",(url,fileName)
    )
    db.commit()
    if save:
        saveDB()


def deleteDB(fileName,save=True):
    db=get_db()
    db.execute(
         "delete from downloads "
         "where fileName=? ",(fileName,)
    )
    db.commit()
    if save:
        saveDB()

colonnesSauvegardees=['url','fileName']
urlSauvegardeHook='/save-downloads.php'

def saveDB():
    db=get_db()
    lignes = db.execute(
        'SELECT * '
        'FROM downloads '
        'ORDER BY id'
    ).fetchall()
    txt=''
    for colonne in colonnesSauvegardees:
        if colonne!=colonnesSauvegardees[0]:
            txt+=','
        txt+= f'"{colonne}"'
    txt+='\n'
    for ligne in lignes:
        for colonne in colonnesSauvegardees:
            if colonne!=colonnesSauvegardees[0]:
                txt+=','
            txt+= f'"{ligne[colonne]}"'
        txt+='\n'
    fileSaveDownloads=current_app.instance_path+'/'+current_app.fileSaveDownloads
    with open(fileSaveDownloads,'w') as f:
        f.write(txt)
    # sauvegarde externe du fichier fileSaveDownloads
    url=current_app.urlSaveDownloads+urlSauvegardeHook
    content=bytes(txt,'utf8')
    datas={'file':current_app.fileSaveDownloads,'content':content}
    p=requests.post(url,datas)
    

def getFileDownlodsExternal():
    url=current_app.urlSaveDownloads+'/'+current_app.fileSaveDownloads
    res=requests.get(url).content.decode('utf8')
    return res
    


def getCsvFileSaveDownloads(txt=None):
    if txt is None: # sauvegarde texte (txt) dans instance
        try:
            with open(current_app.instance_path+'/'+current_app.fileSaveDownloads) as f:
                return list(csv.DictReader(f))
        except:
            return None
    else: # lire le txt issu normalement de la sauvegarde externe
        return list(csv.DictReader(txt.splitlines()))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Supprime la base et les fichiers, puis crée la structure de la base"""
    init_db()
    click.echo('Remise à zéro des fichiers et de la base.')


# "register" des fonctions
def init_app(app):
    # app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(showDB)
    app.cli.add_command(reloadDownloads)
    


def getTableContentString(resultSet,colonnes):
    widths = []
    tavnit = '|'
    separator = '+' 
    for entete in colonnes:
        widths.append(len(entete))
    for ligne in resultSet:
        index=0
        for colonne in colonnes:
            widths[index]=max(widths[index],len(str(ligne[colonne])))
            index+=1
    for w in widths:
        tavnit += " %-"+"%ss |" % (w,)
        separator += '-'*w + '--+'
    res=separator+'\n'
    res+= tavnit % tuple(colonnes)+'\n'
    res+= separator+'\n'
    for ligne in resultSet:
        tab=[]
        for colonne in colonnes:
            tab.append(ligne[colonne])
        res+= tavnit % tuple(tab)+'\n'
    res+= separator+'\n'
    res+= f"{len(resultSet)} ligne{'' if len(resultSet)<=1 else 's'}"
    return res


@click.command('show-db')
@with_appcontext
def showDB():
    """Affiche le contenu de la base"""
    db=get_db()
    tout = db.execute(
        'SELECT * '
        'FROM downloads'
    ).fetchall()
    colonnes=['url','fileName']
    click.echo(getTableContentString(tout,colonnes))


from ..download import telecharger
@click.command('reload-downloads')
@with_appcontext
def reloadDownloads():
    '''
    Vérifie la cohérence des fichiers dans les "downloads", de la base
    et recharge ceux qui manquent en fonction de la sauvegarde externe
    '''
    filesStatic=os.listdir(current_app.staticDownloadPath)
    filesInstance=os.listdir(current_app.downloadsPath)
    sauvegardeExterne=getCsvFileSaveDownloads(getFileDownlodsExternal())
    db=get_db()
    # lire static et supprimer les liens cassés
    for f in filesStatic:
        if f not in filesInstance:
            current_app.logger.info(f'Supression de "{f}" dans static')
            os.remove(current_app.staticDownloadPath+'/'+f)
    # lire instance et supprimer les fichiers qui ne sont pas dans static
    for f in filesInstance:
        if f not in filesStatic:
            current_app.logger.info(f'Supression de "{f}" dans instance')
            os.remove(current_app.downloadsPath+'/'+f)
    # remettre la base en état
    filesInstance=os.listdir(current_app.downloadsPath)
    tout = db.execute(
            'SELECT * '
            'FROM downloads '
            ).fetchall()
    for ligne in tout:
        if ligne['fileName'] not in filesStatic:
            deleteDB(ligne['fileName'],save=False)
    # lire la sauvegarde externe et recharger ce qui manque
    for f in sauvegardeExterne:
        cherche = db.execute(
            'SELECT * '
            'FROM downloads '
            'WHERE fileName=?',(f['fileName'],)
        ).fetchall()
        if len(cherche)!=1:
            url=f['fileName']
            current_app.logger.info(f'Téléchargement de {url}')
            error,fileName= telecharger(f['url'],gererSession=False)
            if error is None:
                insertDB(f['url'],f['fileName'])
 
 
