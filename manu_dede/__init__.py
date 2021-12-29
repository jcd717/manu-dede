import os,logging

from flask import Flask, request, send_from_directory, url_for

from flask_wtf.csrf import CSRFProtect

from flask_session import Session
from werkzeug.utils import redirect

def create_app(test_config=None):

    ### TUYAUTERIE ###

    # create and configure the app
    # c'est la doc qui dit qu'il vaut mieux utiliser la forme split
    app = Flask(__name__.split('.')[0], instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        TOOLBAR=os.environ.get('TOOLBAR'),
        TITRE='Manu & Dédé téléchargent',
        DEBUG_TB_TEMPLATE_EDITOR_ENABLED=True,
        #EXPLAIN_TEMPLATE_LOADING=True
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # contient essentiellement la "SECRET_KEY"
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # si la variable d'environnement "SECRET_KEY" existe alors c'est la bonne (bonne pratique docker)
    if os.environ.get('SECRET_KEY'):
        app.config.from_mapping(SECRET_KEY=os.environ['SECRET_KEY'],)

    # autoescape sur .j2
    from jinja2 import select_autoescape

    app.jinja_env.autoescape = select_autoescape(
        default_for_string=True,
        disabled_extensions=('txt',),
        default=True
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # la toolbar
    if app.config['TOOLBAR']:
        from flask_debugtoolbar import DebugToolbarExtension
        #toolbar = DebugToolbarExtension(app)
        DebugToolbarExtension(app)
        if app.debug:  # lorsqu'il y a la toolbar, le logger n'envoie plus les debug
            app.logger.propagate = True


    @app.route('/robots.txt')
    @app.route('/humans.txt')
    #@app.route('/favicon.ico')
    @app.route('/sitemap.xml')
    def static_from_root():
        return send_from_directory(app.static_folder, request.path[1:])

    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('static', filename='img/death-guitar.png'))

    
    # session côté serveur
    redis = os.environ.get('REDIS') if os.environ.get('REDIS') else False
    app.config.update(
        SESSION_TYPE='redis' if redis else 'filesystem',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        #SESSION_COOKIE_SECURE=True,  # impose HTTPS
        SESSION_USE_SIGNER=True,
        SESSION_FILE_DIR=os.path.join(app.instance_path,'flask_session'),
        PERMANENT_SESSION_LIFETIME = 2 * 24 * 3600 + 3600 # 49 heures
    )
    if redis:
        from redis import Redis
        hp=redis.split(':')
        h=hp[0]
        p = 6379 if len(hp)==1 else int(hp[1])
        app.config['SESSION_REDIS']=Redis(host=h,port=p)
    Session(app)

    # Markdown
    # from flaskext.markdown import Markdown
    # Markdown(app)

    # sécuriser les FORM HTML
    # from flask_wtf.csrf import CSRFProtect
    # CSRFProtect(app)

    
    ### Mon appli ###

    from manu_dede import manu_dede
    app.register_blueprint(manu_dede.bp)
    app.add_url_rule('/', endpoint='homepage')

    app.downloadsPath=app.instance_path+'/downloads'
    try:
        os.makedirs(app.downloadsPath)
    except OSError:
        pass

    app.staticDownloadPath=app.static_folder+'/downloads'
    try:
        os.makedirs(app.staticDownloadPath)
    except OSError:
        pass
    
    # stockage global des downloads en cours
    app.downloads=dict()

    # pour faire marcher app.logger.info() dans Docker (mais peut-être aussi quand on est en mode Production)
    app.logger.setLevel(logging.DEBUG)

    from werkzeug.exceptions import HTTPException
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        app.logger.error(f'{e.code} - {request.remote_addr} - {request.url} - {request.user_agent}')
        return e.get_response()


    # CLI init-db et autres
    app.DB_FILE=app.instance_path+'/downloads.sqlite3'
    from .db import db
    db.init_app(app)

    # Variables d'environnement pour la base
    app.urlSaveDownloads=os.environ.get('URL_SAVE_DOWNLOADS','https://granddub.fr/manu-dede-save-downloads')
    app.fileSaveDownloads=os.environ.get('FILE_SAVE_DOWNLOADS','downloads.txt')

    # CSRF
    csrf = CSRFProtect(app)
    app.config['WTF_CSRF_TIME_LIMIT']=None # 3600 par défaut, avec None => le temps de la session

    return app

