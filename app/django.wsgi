import os
import sys

sys.path.append('/webapps/nalozi')
sys.path.append('/webapps/nalozi/nalozi')
#os.environ['PYTHON_EGG_CACHE'] = '/webapps/nalozi/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
