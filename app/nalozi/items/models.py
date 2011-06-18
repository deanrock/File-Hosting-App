from django.db import models
from django.contrib.auth.models import User
from djangoratings.fields import RatingField

# Create your models here.
class Album(models.Model):
	user = models.ForeignKey(User, null=True, blank=False, related_name='album_set')
	name = models.CharField(max_length=200)
	pub_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return self.name

class Tag(models.Model):
	name = models.CharField(max_length=50)
	url = models.CharField(max_length=100)
	
class Item(models.Model):
	name = models.CharField(max_length=200)
	user = models.ForeignKey(User, null=True, blank=False, related_name='item_set')
	album = models.ForeignKey(Album, null=True)
	published = models.BooleanField(default=False)
	path = models.CharField(max_length=200)
	pub_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateField(auto_now=True)
	type = models.CharField(max_length=100)
	thumbnail = models.CharField(max_length=200, null=True)
	thumbnail_medium = models.CharField(max_length=200, null=True)
	is_private = models.BooleanField(default=False)
	url = models.CharField(max_length=200)
	code = models.CharField(max_length=200)
	random_string = models.CharField(max_length=200,null=True, blank=True)
	tags = models.ManyToManyField(Tag)
	description = models.TextField(null=True, blank=True)
	converted = models.BooleanField(default=False)
	
	#rating
	rating = RatingField(range=5,weight=5,can_change_vote=False,allow_anonymous=False)
	
	def __unicode__(self):
		return self.name

class Comment(models.Model):
    belong_to  = models.ForeignKey(Item)
    author        = models.ForeignKey(User)
    comment   = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)