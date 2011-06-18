from django.http import HttpResponse, HttpResponseRedirect
from nalozi.items.models import Item
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.template import RequestContext
from nalozi.settings import FILES_URL
from nalozi.items.models import Item, Comment
from django.utils import simplejson
import os, re, sys
import string, random
from subprocess import Popen, PIPE, STDOUT
from thumbnail import thumbnail

class CustomException(Exception):
   def __init__(self, value):
       self.parameter = value
   def __str__(self):
       return repr(self.parameter)

def handle_uploaded_file(f, id, x):
	os.mkdir(FILES_URL + '/' + id)
	
	destination = open(FILES_URL + '/' + id + '/' + x, 'wb+')
	for chunk in f.chunks():
		destination.write(chunk)
	
	destination.close()

def random_string(x):
	chars = string.letters + string.digits
	
	newpasswd = ''
	
	for i in range(x):
		newpasswd = newpasswd + chars[random.randint(0,len(chars)-1)]
	
	return newpasswd

def str_to_url(x):
	allowed = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','r','s','t','u','v', 'z', 'x', 'q', 'w', '0', '1', '2', '3', '4', '5','6','7','8','9','.']
	
	new = ''
	
	for z in x.lower():
		if z in allowed:
			new += z
		else:
			new += '-'
	new = new.replace('--', '-')
	new = new.lstrip('-')
	new = new.rstrip('-')
	
	return new

def rate(request, code, score):
	xhr = request.GET.has_key('xhr')
	score = int(score)
	
	if score >= 0 and score <= 5:
		i = get_object_or_404(Item, code=code)
		
		try:
			i.rating.add(score=score, user=request.user, ip_address=request.META['REMOTE_ADDR'])
			i.save()
			request.user.get_profile().add_point()
		except:
			score = 0
		
		if xhr:
			i2 = get_object_or_404(Item, code=code)
			stars = i2.rating.get_real_percent()/20
	
			rating = stars*30
			return HttpResponse(rating)
	
	return HttpResponseRedirect('/')

def index(request):
	latest_files = Item.objects.all()
	
	code = ''
	url = ''
	error = 'Napaka pri nalaganju!'
	
	allowed = ['bmp', 'gif', 'jpg', 'png', 'tiff', 'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'odt', 'ods', 'odp', 'wmv', 'mp4']
	
	randomString = random_string(100) #random number just for kicks (it should be as random and unique as possible)
	
	if request.method == 'POST':
		try:
			name = request.FILES['file'].name
			ext = name.split('.')[len(name.split('.'))-1].lower()
			
			if ext not in allowed:
				error = 'Ta tip datoteke ni dovoljen!'
				raise CustomException('wrong_type')
			
			url = str_to_url(request.FILES['file'].name)
			i = Item(name = request.FILES['file'].name, type = request.FILES['file'].content_type, url = url, random_string = randomString, description = '')
			
			if request.user.is_authenticated():
				if 'private' in request.POST:
					i.is_private = True
				
				i.user = request.user
			
			i.save() #save it to get id
			
			code = str(i.id) + random_string(6)
			
			i.code = code
			i.save()
			
			handle_uploaded_file(request.FILES['file'], code, url)
			
			i.path = code + '/' + url
			i.save()
			
			#if not logged in, save item id to session
			if not request.user.is_authenticated():
				if not 'uploaded_files' in request.session:
					request.session['uploaded_files'] = []
				
				tmp = request.session['uploaded_files']
				tmp.append(i.id)
				request.session['uploaded_files'] = tmp
				request.session.modified = True
			
			#everything went well, check if we can make a preview of file
			if i.type == 'application/pdf':
				try:
					os.system("convert -colorspace rgb " + FILES_URL + "/" + i.path + " " + FILES_URL + "/" + i.code + "/converted-" + i.code + ".jpg")
					i.converted = True
					
					#create thumbnail
					path = FILES_URL + "/" + i.code + "/converted-" + i.code + "-0.jpg"
					if not os.path.exists(path):
						path = FILES_URL + "/" + i.code + "/converted-" + i.code + ".jpg"
					
					t = thumbnail(path)
					m = thumbnail(path, 200)
					
					if t:
						i.thumbnail = t
					
					if m:
						i.thumbnail_medium = m
					
				except:
					#something went wrong
					i.converted = False
			
			if i.type == 'image/jpg' or i.type == 'image/jpeg' or i.type == 'image/png' or i.type == 'image/gif':
				path = FILES_URL + '/' + i.path
				try:
					t = thumbnail(path)
					m = thumbnail(path, 200)
					
					if t:
						i.thumbnail = t
					
					if m:
						i.thumbnail_medium = m
				except:
					path = ''
			
			i.published = True
			i.save()

			if request.user.is_authenticated():
				request.user.get_profile().add_point()
			
			return HttpResponseRedirect('/datoteka/' + i.path)
		except:
			#revert db/fs - delete created folder/file and remove DB entry
			
			try:
				if len(code) > 0 and len(url) > 0:
					os.remove(FILES_URL + '/' + code + '/' + url)
					os.rmdir(FILES_URL + '/' + code)
			except:
				#there might be a problem with removing folder/file
				None
			
			#try removing entry from DB
			try:
				i = Item.objects.get(random_string=randomString, published=False)
				i.delete()
			except:
				#entry not found, apparently we didn't create one therefore we don't need to remove folder/file
				None
			
			return render_to_response('items/index.html', {'latest_files_list': latest_files, 'error': error},
		context_instance=RequestContext(request))
	
	if 'uploaded_files' in request.session:
		x = request.session['uploaded_files']
	
	return render_to_response('items/index.html', {'latest_files_list': latest_files},
		context_instance=RequestContext(request))

def show(request, code, url):
	i = get_object_or_404(Item, code=code, url=url)
	
	if i.is_private and not i.user == request.user:
		return render_to_response('items/show_file_is_private.html',
			context_instance=RequestContext(request))
	
	#template variables
	show_edit_description = False
	converted_vars = {}
	
	#add comemnt
	if request.method == 'POST' and 'comment' in request.POST and request.user.is_authenticated():
		comment = request.POST['comment']
		
		if len(comment) > 2:
			c = Comment(belong_to=i,author=request.user,comment=comment)
			c.save()
			request.user.get_profile().add_point()
			return HttpResponseRedirect('/datoteka/' + i.path)
	
	#edit data
	if request.method == 'POST' and i.user == request.user and 'edit_description' in request.POST:
		show_edit_description = True
	
	if request.method == 'POST' and i.user == request.user and 'edit_description' not in request.POST:
		if 'to_private' in request.POST:
			i.is_private = True
		
		if 'to_public' in request.POST:
			i.is_private = False
		
		if 'description' in request.POST:
			i.description = request.POST['description']
		
		i.save()
		
		if 'new_tag' in request.POST and len(request.POST['new_tag']) > 0:
			t = Tag(name=request.POST['new_tag'], url=str_to_url(request.POST['new_tag']))
			t.save()
			
		#add tag to item
		"""{% if tags %}
	<b>Tagi:</b>
	{% for tag in tags %}
	<a href="/tag/{{tag.url}}">{{tag.name}}</a>
	{% endfor %}
	{% endif %}
	
	{% if item.user == user %}
	<input type="text" name="new_tag" /> <input type="submit" value="Dodaj" />
	{% endif %}"""
		
		if 'delete' in request.POST:
			os.remove(FILES_URL + '/' + i.code + '/' + i.url)
			os.rmdir(FILES_URL + '/' + i.code)
			i.delete()
			return HttpResponseRedirect('/moje-datoteke')
		
		return HttpResponseRedirect('/datoteka/' + i.path)
	
	#converted PDF
	if i.type == 'application/pdf':
		try:
			dir = os.listdir(FILES_URL + '/' + i.code)
			
			pattern = re.compile(r'^converted-' + i.code + '-([0-9]+)\.jpg$')
			
			files = []
			
			for file in dir:
				q = pattern.search(file)
				if q:
					
					files.append(int(q.groups()[0]))
			
			if len(files) > 0:
				files.sort()
				cmd = 'identify ' + FILES_URL + '/' + i.code + '/converted-' + i.code + '-' + str(files[0]) + '.jpg'
			else:
				cmd = 'identify ' + FILES_URL + '/' + i.code + '/converted-' + i.code + '.jpg'
				
			converted_vars['type'] = "pdf"
			converted_vars['files'] = files
			
			#image size
			p = Popen(cmd,shell=True,stdin=PIPE,stdout=PIPE,stderr=STDOUT, close_fds=True)
			output = p.stdout.read()
			regex = re.compile(r'([0-9]+)x([0-9]+)')
			
			s = regex.search(output)
			
			if s and len(s.groups()) >= 2:
				width = s.groups()[0]
				height = s.groups()[1]
				converted_vars['width'] = width
				converted_vars['height'] = height
			else:
				raise CustomException('cannot get image width and height')
		except:
			converted_vars = {}
		
	#converted picture
	if i.type == 'image/jpg' or i.type == 'image/jpeg' or i.type == 'image/png' or i.type == 'image/gif':
		try:
			converted_vars['type'] = "image"
			
			#image size
			cmd = 'identify ' + FILES_URL + '/' + i.code + '/' + i.url
			p = Popen(cmd,shell=True,stdin=PIPE,stdout=PIPE,stderr=STDOUT, close_fds=True)
			output = p.stdout.read()
			regex = re.compile(r'([0-9]+)x([0-9]+)')
			
			s = regex.search(output)
			
			if s and len(s.groups()) >= 2:
				width = s.groups()[0]
				height = s.groups()[1]
				converted_vars['width'] = width
				converted_vars['height'] = height
			else:
				raise CustomException('cannot get image width and height')
		except:
			converted_vars = {}
			
	#rating
	stars = i.rating.get_real_percent()/20
	
	rating = stars*30
	
	comments = Comment.objects.filter(belong_to=i).order_by('-pub_date').all()
	
	return render_to_response('items/show.html', {'item': i, 'rating': rating, 'comments': comments, 'show_edit_description': show_edit_description, 'converted_vars': converted_vars},
		context_instance=RequestContext(request))

def shorturl(request, code):
	i = get_object_or_404(Item, code=code)
	
	if i.is_private and not i.user == request.user:
		return render_to_response('items/show_file_is_private.html',
			context_instance=RequestContext(request))
	
	return HttpResponseRedirect('/datoteka/' + i.code + '/' + i.url)

def search(request):
	if 'q' in request.GET and len(request.GET['q']) > 2:
		#search code
		q = request.GET['q']
		
		return render_to_response('items/search.html', { 'search_query': q, 'results': '' },
			context_instance=RequestContext(request))
	else:
		#error
		return render_to_response('items/search_search_query_too_short.html', { 'search_query': '' }, 
			context_instance=RequestContext(request))

def browse(request):
	results = Item.objects.filter(is_private=False,published=True).order_by('-pub_date').all()[0:20]
	return render_to_response('items/browse.html', { 'results': results },
			context_instance=RequestContext(request))