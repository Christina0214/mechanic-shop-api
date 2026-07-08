class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:password@localhost/mechanic_shop'
    DEBUG = True #Autoupdates whenever any changes happen
    
class TestingConfig:
    pass

class ProductionConfig:
    pass