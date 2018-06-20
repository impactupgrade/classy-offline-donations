import os

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import *
from .services import classy


# TODO: Pull the common context variables (organization_name, etc.) to a helper...


def index(request):
    return render(request, 'core/index.html', __add_context(request))


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
                    return redirect('/')
            else:
                messages.error(request, 'Invalid email or password')

    else:
        form = LoginForm()

    context = __add_context(request, {'form': form})
    if request.GET.get('next') is not None:
        context['next'] = request.GET.get('next')
    return render(request, 'core/login.html', context)


def core_logout(request):
    logout(request)
    return redirect('/')


@staff_member_required(login_url="/login")
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
                return redirect('/enable-user')
            else:
                messages.error(request, email + ' does not exist in Classy')

    else:
        form = EnableUserForm()

    return render(request, 'core/enable-user.html', __add_context(request, {'form': form}))


@login_required(login_url="/login")
def donate(request):
    fundraiser_choices = classy.get_fundraisers(request.session)

    if request.method == 'POST':
        form = DonationForm(fundraiser_choices, request.POST)
        if form.is_valid():
            classy.create_donation(form, request.session)
            messages.success(request, 'Successfully created donation!')
            return redirect('/donate')
    else:
        # team_choices = classy.get_teams(request.session)
        form = DonationForm(fundraiser_choices)

    return render(request, 'core/donate.html', __add_context(request, {'form': form}))


@staff_member_required(login_url="/login")
def approve(request):
    donations = classy.get_unapproved_donations(request.session)

    if request.method == 'POST':
        form = ApproveDonationForm(donations, request.POST)
        if form.is_valid():
            for donation_id in form.cleaned_data['donation_ids']:
                classy.approve_donation(donation_id, request.session)
            messages.success(request, 'Successfully approved donations!')
            return redirect('/approve')
    else:
        form = ApproveDonationForm(donations)

    return render(request, 'core/approve.html', __add_context(request, {'donations': donations, 'form': form}))


@staff_member_required(login_url="/login")
def delete(request, donation_id):
    classy.delete_donation(donation_id, request.session)
    messages.success(request, 'Successfully deleted the donation!')
    return redirect('/approve')


def __add_context(request, context={}):
    context['organization_name'] = os.environ['ORG_NAME']
    context['is_classy_member'] = 'CLASSY_MEMBER_ID' in request.session\
                                  and request.session['CLASSY_MEMBER_ID'] is not None
    return context
