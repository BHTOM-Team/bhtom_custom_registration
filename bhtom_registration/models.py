
from django.db import models
from django.contrib.auth.models import User

class LatexUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    latex_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='LaTeX name')
    latex_affiliation = models.CharField(max_length=255, null=True, blank=True, verbose_name='LaTeX affiliation')
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name='Address')
    about_me = models.TextField(null=True, blank=True, verbose_name='About me')
    orcid_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='ORCCID ID')