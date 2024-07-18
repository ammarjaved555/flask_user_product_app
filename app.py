from flask import Flask
from config import Config
from models import db
from controllers import user_blueprint, product_blueprint, order_blueprint

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(user_blueprint, url_prefix='/users')
app.register_blueprint(product_blueprint, url_prefix='/products')
app.register_blueprint(order_blueprint, url_prefix='/orders')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
