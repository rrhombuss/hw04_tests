from django import forms

from .models import Group, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text']


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'slug', 'description']
