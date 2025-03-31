from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from app.controllers.product_controller import product_bp
    from app.controllers.seller_controller import seller_bp
    from app.controllers.store_controller import store_bp
    
    app.register_blueprint(product_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(store_bp)
    
    return app 