from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', 'nalozi.items.views.index'),
	
	(r'^datoteka/(.*)/(.*)$', 'nalozi.items.views.show'),
	(r'^iskanje$', 'nalozi.items.views.search'),
	(r'^brskaj$', 'nalozi.items.views.browse'),
	(r'^rate/(.*)/(.*)$', 'nalozi.items.views.rate'),
	
	(r'^moji-prijatelji$', 'nalozi.users.views.my_friends'),
	(r'^moje-datoteke$', 'nalozi.users.views.my_files'),
	
	#Users
	(r'^prijava', 'nalozi.users.views.login'),
	(r'^odjava$', 'nalozi.users.views.logout'),
	(r'^registracija$', 'nalozi.users.views.register'),
	
	#Static pages
	(r'^kontakt$', 'nalozi.static.views.contact'),
	(r'^pogoji-uporabe$', 'nalozi.static.views.terms_of_use'),
	
	(r'^d/(.*)$', 'nalozi.items.views.shorturl'),
	
    # Example:
    # (r'^nalozi/', include('nalozi.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

#Static files - DEBUG
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT+'/css'}),
        (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT+'/images'}),
        (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT+'/js'}),
        (r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.FILES_URL}),
    )