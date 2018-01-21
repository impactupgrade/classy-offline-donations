from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from .forms import *
from .services import classy


def index(request):
    context = {}
    return render(request, 'core/index.html', context)


def core_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                classy.login(email, request.session)
                if request.POST.get('next') is not None:
                    return redirect(request.POST.get('next'))
                else:
                    return redirect('/core')
            else:
                messages.error(request, 'Invalid email or password')

    else:
        form = LoginForm()

    context = {'form': form}
    if request.GET.get('next') is not None:
        context['next'] = request.GET.get('next')
    return render(request, 'core/login.html', context)


def core_logout(request):
    logout(request)
    return redirect('/core')


@permission_required('core.can_enable_user', login_url="/core/login")
def enable_user(request):
    if request.method == 'POST':
        form = EnableUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if classy.has_account(email, request.session):
                user = User.objects.create_user(email, email, password)
                user.save()

                messages.success(request, 'Successfully enabled ' + email)
                return redirect('/core/enable-user')
            else:
                messages.error(request, email + ' does not exist in Classy')

    else:
        form = EnableUserForm()

    return render(request, 'core/enable-user.html', {'form': form})


@login_required(login_url="/core/login")
def donate(request):
    fundraiser_choices = classy.get_fundraisers(request.session)

    if request.method == 'POST':
        form = DonationForm(fundraiser_choices, request.POST)
        if form.is_valid():
            classy.create_donation(form, request.session)
            messages.success(request, 'Successfully created donation!')
            return redirect('/core/donate')
    else:
        # team_choices = classy.get_teams(request.session)
        form = DonationForm(fundraiser_choices)

    return render(request, 'core/donate.html', {'form': form})


@permission_required('core.can_approve_donation', login_url="/core/login")
def approve(request):
    donations = classy.get_unapproved_donations(request.session)

    # if request.method == 'POST':
    # TODO: use to approve 1..n donations with checkboxes
    # else:

    return render(request, 'core/approve.html', {'donations': donations})
