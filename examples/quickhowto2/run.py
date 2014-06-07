import sys
from app import create_app

config = 'config'
if len(sys.argv) > 1:
    config = sys.argv[1]
create_app(config).run(host='0.0.0.0', port=8080, debug=True)
