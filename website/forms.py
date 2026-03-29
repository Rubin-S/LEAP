
from django import forms
from django.contrib.auth.models import User
from .models import Profile, Course

class SocialSignupForm(forms.Form):
    full_name = forms.CharField(max_length=100, label="Full Name")
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label="Course")
    
    def save(self, user):
      
        profile, created = Profile.objects.get_or_create(user=user)
        profile.name = self.cleaned_data['full_name']
        profile.course = self.cleaned_data['course']
        profile.save()
        return profile
