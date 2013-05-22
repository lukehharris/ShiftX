#!"C:\Users\John Galt\Documents\GitHub\ShiftExchange\venv\Scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'gunicorn==0.17.4','console_scripts','gunicorn'
__requires__ = 'gunicorn==0.17.4'
import sys
from pkg_resources import load_entry_point

sys.exit(
   load_entry_point('gunicorn==0.17.4', 'console_scripts', 'gunicorn')()
)
