from django import forms
from .models import ViewerMessage

class ViewerMessageForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for f in self.fields:
            self.fields[f].widget.attrs.update({
                'class':"form-control form-control-lg"
            })
    class Meta:
        model = ViewerMessage
        fields = '__all__'