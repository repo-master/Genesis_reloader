import os

basedir = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

config_db = {
    'MYSQL_HOST': '134.209.158.162',
    #'MYSQL_HOST': 'localhost',
    'MYSQL_USER': 'GenesisServerApp',
    'MYSQL_PASSWORD': 'GenesisServerApp@321',
    'MYSQL_DB': 'genesisdb',
}
config_conn = dict(
    host=config_db['MYSQL_HOST'],
    user=config_db['MYSQL_USER'],
    password=config_db['MYSQL_PASSWORD'],
    database=config_db['MYSQL_DB'],
)

config_log = {
    'log_path': os.path.join(basedir, 'wm_server.log'),
}

class Config:
    APP_NAME = 'warehouse_monitor'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bluelemonmicrotiger'
    TOKEN_EXPIRY = False
    TOKEN_EXPIRE_SECONDS = 10
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


# class ProductionConfig(Config):
    # @classmethod
    # def init_app(cls, app):
        # Config.init_app(app)
        
        # # email errors to the administrators
        # import logging
        # from logging.handlers import SMTPHandler
        # credentials = None
        # secure = None
        # if getattr(cls, 'MAIL_USERNAME', None) is not None:
            # credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            # if getattr(cls, 'MAIL_USE_TLS', None):
                # secure = ()
        # mail_handler = SMTPHandler(
            # mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            # fromaddr=cls.FLASKY_MAIL_SENDER,
            # toaddrs=[cls.FLASKY_ADMIN],
            # subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            # credentials=credentials,
            # secure=secure)
        # mail_handler.setLevel(logging.ERROR)
        # app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    # 'production': ProductionConfig,
    
    'default': DevelopmentConfig,
}
