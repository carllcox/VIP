import os


#basedir = os.path.abspath(os.path.dirname(__file__)) 

# Google Cloud SQL
PASSWORD ="xaLjDunHHm1FcKGC"
PUBLIC_IP_ADDRESS = "34.75.89.116"
DBNAME ="coronadatabase"
PROJECT_ID ="cttxpolicy"
INSTANCE_NAME ="coronaviruspolicy:us-east1:cttxpolicy"

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '33lkjdf#897lk'
    
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        #'sqlite:///' + os.path.join(basedir, 'app.db')

    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://root:{}@{}/{}?unix_socket=/cloudsql/{}:{}".format(PASSWORD, PUBLIC_IP_ADDRESS, DBNAME, PROJECT_ID, INSTANCE_NAME )
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['exampleAdmin@example.com']
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
