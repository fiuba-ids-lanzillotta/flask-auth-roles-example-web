import logging
import os
from flask import Flask, render_template
from flask_auth_roles_web.routes.auth import auth_bp

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.json.sort_keys = False
app.secret_key = os.getenv('SECRET_KEY', 'change-me-please-frontend')

app.register_blueprint(auth_bp)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404


if __name__ == '__main__':
    app.run(debug=True, port=5001)
