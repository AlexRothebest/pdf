import os
import sys
 
sys.path.append('/home/c/cf88808/PDF/')
sys.path.append('/home/c/cf88808/env/lib/python3.4/site-packages/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'PDF.settings'
 
from django.core.handlers import wsgi
application = wsgi.WSGIHandler()