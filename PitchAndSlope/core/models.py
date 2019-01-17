from __future__ import unicode_literals

from django.db import models


class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class PortalUser(models.Model):
    userId =models.CharField(max_length=50, blank=False)
    firstName =models.CharField(max_length=100, blank=False)
    lastName =models.CharField(max_length=100, blank=False)
    password =models.CharField(max_length=50, blank=False)
    email =models.CharField(max_length=100, blank=False)
    
    class Meta: 
        ordering = ['firstName']
        
    def get_absolute_url(self):
        """Returns the url to access a particular instance of MyModelName."""
        return "/userDetails/%i/" % self.userId
    
    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return "User Id:" +self.userId + "First Name:"+self + "Last Name:" +self.lastName

class Files(models.Model):
    name = models.CharField(max_length=30)
    image = models.TextField()
    canvas_image = models.TextField()
    
    def __unicode__(self):
        return self.name