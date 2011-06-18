from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Friendship(models.Model):
	from_friend = models.ForeignKey(
		User, related_name='friend_set'
	)
	
	to_friend = models.ForeignKey(
		User, related_name='to_friend_set'
	)

def __unicode__(self):
	return u'%s, %s' % (
	self.from_friend.username,
	self.to_friend.username
)

class Meta:
	unique_together = (('to_friend', 'from_friend'), )

class UserProfile(models.Model):
	user = models.ForeignKey(User)
	
	#points
	points = models.BigIntegerField(default=0)
	week_points = models.BigIntegerField(default=0)
	
	def add_point(self):
		self.points = self.points + 1
		self.week_points = self.week_points + 1
		self.save()
	
	def __str__(self):  
		return "%s's profile" % self.user  
	
	def create_user_profile(sender, instance, created, **kwargs):  
		if created:
			profile, created = UserProfile.objects.get_or_create(user=instance)  
		
	post_save.connect(create_user_profile, sender=User)