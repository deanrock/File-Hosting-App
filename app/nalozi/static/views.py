# coding=utf8
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.core.mail import send_mail

def contact(request):
	if 'message' in request.POST:
		message = request.POST['message']
		email = request.POST['email']
		name = request.POST['name']
		subject = request.POST['subject']
		
		send_mail('Kontaktni obrazec (' + subject +')', 'Email: ' + email + '\n\nName:' + name + '\n\n' + message, email, [u'info@naloži.si'])
		
	return render_to_response('static/contact.html', {},
		context_instance=RequestContext(request))

def terms_of_use(request):
	return render_to_response('static/terms-of-use.html', {},
		context_instance=RequestContext(request))