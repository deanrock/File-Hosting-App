from django import template
from django.conf import settings

def setting ( context ):
	return {'DEBUG': settings.DEBUG }