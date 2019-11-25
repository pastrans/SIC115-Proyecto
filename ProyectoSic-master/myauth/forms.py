from django import forms
from myauth.models import MyUser


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    username = forms.CharField(label='Usuario', required=True, )
    email = forms.EmailField(label='Email',
                             required=True, )

    class Meta:
        model = MyUser
        fields = ('username', 'email', )
