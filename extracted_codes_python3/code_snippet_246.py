'''

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models

from docfish.settings import MEDIA_ROOT

from itertools import chain
import collections
import operator
import os


#######################################################################################################
# Supporting Functions and Variables ##################################################################
#######################################################################################################


# Create a token for the user when the user is created (with oAuth2)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# Get path to where images are stored for teams
def get_image_path(instance, filename):
    team_folder = os.path.join(MEDIA_ROOT,'teams')
    if not os.path.exists(team_folder):
        os.mkdir(team_folder)
    return os.path.join('teams', filename)


TEAM_TYPES = (('invite', 'Invite only. The user must be invited by the team administrator.'),
              ('institution', 'Institution only. Any user with the same institution as the creator can join'),
              ('open','Open. Anyone can join the team without asking.'))

REQUEST_CHOICES = (("denied", 'Request has not been granted.'),
                   ("pending", 'Request is pending.'),
                   ("granted", 'Request has been granted'),)

#######################################################################################################
# Teams ###############################################################################################
#######################################################################################################

class Team(models.Model):
    '''A user team is a group of individuals that are annotating reports together. They can be reports across collections, or 
    institutions, however each user is only allowed to join one team.
    '''
    name = models.CharField(max_length=250, null=False, blank=False,verbose_name="Team Name")
    owner = models.ForeignKey(User, blank=True, verbose_name="Team owner and adminstrator.")
    created_at = models.DateTimeField('date of creation', auto_now_add=True)
    updated_at = models.DateTimeField('date of last update', auto_now=True)
    collection_ids = JSONField(default=[])
    team_image = models.ImageField(upload_to=get_image_path, blank=True, null=True)    
    metrics_updated_at = models.DateTimeField('date of last calculation of rank and annotations',blank=True,null=True)
    ranking = models.PositiveIntegerField(blank=True,null=True,
                                          verbose_name="team ranking based on total number of annotations, calculated once daily.")
    annotation_count = models.IntegerField(blank=False,null=False,
                                           verbose_name="team annotation count, calculated once daily.",
                                           default=0)
    permission = models.CharField(choices=TEAM_TYPES, 
                                  default='open',
                                  max_length=100,
                                  verbose_name="Permission level for joining the team.")
    members = models.ManyToManyField(User, 
                                     related_name="team_members",
                                     related_query_name="team_members", blank=True, 
                                     help_text="Members of the team. By default, creator is made member.")
                                     # would more ideally be implemented with User model, but this will work
                                     # we will constrain each user to joining one team on view side

    def collections(self):
        from docfish.apps.main.models import Collection
        return Collection.objects.filter(id__in=self.collection_ids)
        
    def __str__(self):
        return "%s:%s" %(self.id,self.name)

    def __unicode__(self):
        return "%s:%s" %(self.id,self.name)

    def get_absolute_url(self):
        return reverse('team_details', args=[str(self.id)])

    def contender_collections(self):
        from docfish.apps.main.models import Collection
        owner_collections = Collection.objects.filter(owner=self.owner)
        public_collections = Collection.objects.exclude(owner=self.owner,private=False)
        return list(chain(owner_collections,public_collections))
       
    def add_collection(self,cid):
        if cid not in self.collection_ids:
            self.collection_ids.append(cid)
        
    def remove_collection(self,cid):
        self.collection_ids = [x for x in self.collection_ids if x != cid]
        self.save()

    def has_collections(self):
        if len(self.collection_ids) > 0:
            return True
        return False


    def get_label(self):
        return "users"

    class Meta:
        app_label = 'users'



class MembershipInvite(models.Model):
    '''An invitation to join a team.
    '''
    code = models.CharField(max_length=200, null=False, blank=False) 
    team = models.ForeignKey(Team)

    def __str__(self):
        return "<%s:%s>" %(self.id,self.team.name)

    def __unicode__(self):
        return "<%s:%s>" %(self.id,self.team.name)

    def get_label(self):
        return "users"

    class Meta:
        app_label = 'users'
        unique_together =  (("code", "team"),)


class MembershipRequest(models.Model):
    '''A request for membership is tied to a team. 
    A user is granted access if the owner grants him/her permission.
    '''
    user = models.ForeignKey(User)
    team = models.ForeignKey(Team)
    created_at = models.DateTimeField('date of request', auto_now_add=True)
    status = models.CharField(max_length=200, null=False, 
                              verbose_name="Status of request", 
                              default="pending",choices=REQUEST_CHOICES)
    
    def __str__(self):
        return "<%s:%s>" %(self.user,self.team.name)

    def __unicode__(self):
        return "<%s:%s>" %(self.user,self.team.name)

    def get_label(self):
        return "users"

    class Meta:
        app_label = 'users'
        unique_together =  (("user", "team"),)
