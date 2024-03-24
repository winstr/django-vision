from django import forms

from .models import WebsocketHost


class WebsocketHostForm(forms.ModelForm):
    class Meta:
        model = WebsocketHost
        fields = ('host_uri', 'alias', 'description')
