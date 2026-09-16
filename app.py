from application import create_app
from application.models import db

app = create_app("DevelopmentConfig")

with app.app_context():
    #db.drop_all()
    db.create_all()
    
app.run()
    