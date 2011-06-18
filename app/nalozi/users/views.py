# coding=utf8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from nalozi.users.models import Friendship
from django.contrib.auth.decorators import login_required
from nalozi.items.models import Item
from django.core.validators import email_re #register
from django.contrib.auth.models import User #register, username_exists, email_exists

def is_valid_email(email):
    return True if email_re.match(email) else False
   
def username_exists(username):
	try:
		User.objects.get(username=username)
	except User.DoesNotExist:
		return False
	return True

def email_exists(email):
	try:
		User.objects.get(email=email)
	except User.DoesNotExist:
		return False
	return True

def login(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')
	
	error = ''
	url = ''
	
	if request.method == 'POST':
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			if user.is_active:
				auth_login(request, user)
				
				#Checks if user uploaded files when he wasn't logged in
				if 'uploaded_files' in request.session and not request.session['uploaded_files'] == []:
					for x in request.session['uploaded_files']:
						i = Item.objects.get(id=x)
						i.user = user
						i.save()
					request.session.modified = True
				
				if 'url' in request.POST and request.POST['url'] != '':
					return HttpResponseRedirect('/' + request.POST['url'][1:])
				else:
					return HttpResponseRedirect('/')
			else:
				error = u'Vaš uporabniški račun je bil onemogočen!'
		else:
			error = u'Uporabnik s tem uporabniškim imenom/geslom ne obstaja!'
	
	if 'next' in request.GET:
		url = request.GET['next']
		
	return render_to_response('users/login.html', {'error': error, 'url': url},
		context_instance=RequestContext(request))

def register(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')
	
	errors = []
	username = ''
	email = ''
	
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		password2 = request.POST['password2']
		email = request.POST['email']
		
		if not password == password2:
			errors.append('Gesli se ne ujemata!')
		
		if not is_valid_email(email):
			errors.append('Email naslov ni pravilen!')
		
		if username_exists(username):
			errors.append('Uporabnik z enakim uporabnikom že obstaja!')
		
		if email_exists(email):
			errors.append('Uporabnik z enakim email naslovom že obstaja!')
		
		if len(errors) == 0:
			#register the user
			user = User.objects.create_user(username, email, password)
			user.save()
			
			user2 = authenticate(username=username, password=password)
			auth_login(request, user2)
			
			#Checks if user uploaded files when he wasn't logged in
			if 'uploaded_files' in request.session and not request.session['uploaded_files'] == []:
				for x in request.session['uploaded_files']:
					i = Item.objects.get(id=x)
					i.user = user
					i.save()
				request.session.modified = True
			
			return HttpResponseRedirect('/')
	
	return render_to_response('users/register.html', {'errors': errors, 'username': username, 'email': email},
		context_instance=RequestContext(request))

def logout(request):
	auth_logout(request)
	return HttpResponseRedirect('/')

@login_required
def my_friends(request):
	friends = [Friendship.to_friend for Friendship in request.user.friend_set.all()]
	
	return render_to_response('users/my_friends.html', {'friends': friends},
		context_instance=RequestContext(request))

@login_required
def my_files(request):
	items = request.user.item_set.all()
	
	return render_to_response('users/my_files.html', {'items': items},
		context_instance=RequestContext(request))