from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from myauth.admin import UserCreationForm
from myauth.forms import UserChangeForm
from django.contrib.auth import update_session_auth_hash, login, authenticate
from django.contrib import messages
# Create your views here.


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password1')
            )
            login(request, user)
            return redirect('/index/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def settings(request):
    if request.method == 'POST':
        form = UserChangeForm(data=request.POST, instance=request.user,  files=request.FILES )
        if form.is_valid():
            update = form.save(commit=False)
            update.user = request.user
            update.save()
            messages.success(request, 'Tu configuracion ha sido correctamente guardada! en la ultima sesion')
            return redirect('/index/')
        else:
            messages.error(request, 'Porfavor corriga los errores:')
    else:
        user = request.user
        form = UserChangeForm(instance=user)
    return render(request, 'registration/settings.html', {
        'form': form,
                 })


@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'La contrasenia ha sido cambiada!')
            return redirect('/login/')
        else:
            messages.error(request, 'Porfavor corriga los errores:')
    else:
        form = PasswordForm(request.user)
    return render(request, 'registration/password.html', {'form': form})
