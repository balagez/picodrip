import sys
sys.path.insert(1, '../')

from app.ddns import disable_ddns

disable_ddns()

import app.web_server
