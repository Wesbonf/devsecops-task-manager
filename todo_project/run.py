from todo_project import app
import os

if __name__ == '__main__':
    # Bind host controlled by environment to avoid hardcoded 0.0.0.0
    host = os.environ.get('APP_HOST', '127.0.0.1')
    port = int(os.environ.get('APP_PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ('1', 'true', 'yes')
    app.run(host=host, port=port, debug=debug, use_reloader=False)
