import os

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, \
    PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import *
from .services import classy


def index(request):
    return render(request, 'core/index.html', __add_context(request))


# TODO: Is it instead possible to get to the request from urls.py?
def login(request):
    return LoginView.as_view(
        template_name='core/login.html',
        authentication_form=BootstrapAuthenticationForm,
        extra_context=__add_context(request)
    )(request)


# TODO: Is it instead possible to get to the request from urls.py?
def password_change(request):
    return PasswordChangeView.as_view(
        template_name='core/password_change_form.html',
        form_class=BootstrapPasswordChangeForm,
        extra_context=__add_context(request)
    )(request)


# TODO: Is it instead possible to get to the request from urls.py?
def password_change_done(request):
    return PasswordChangeDoneView.as_view(
        template_name='core/password_change_done.html',
        extra_context=__add_context(request)
    )(request)


# TODO: Is it instead possible to get to the request from urls.py?
def password_reset(request):
    return PasswordResetView.as_view(
        template_name='core/password_reset_form.html',
        email_template_name='core/password_reset_email.html',
        subject_template_name='core/password_reset_subject.txt',
        form_class=BootstrapPasswordResetForm,
        extra_context=__add_context(request)
    )(request)


# TODO: Is it instead possible to get to the request from urls.py?
def password_reset_done(request):
    return PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html',
        extra_context=__add_context(request)
    )(request)


# TODO: Is it instead possible to get to the request from urls.py?
def password_reset_confirm(request, uidb64, token):
    return PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html',
        form_class=BootstrapSetPasswordForm,
        extra_context=__add_context(request)
    )(request, uidb64=uidb64, token=token)


# TODO: Is it instead possible to get to the request from urls.py?
def password_reset_complete(request):
    return PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html',
        extra_context=__add_context(request)
    )(request)


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
            if classy.create_donation(form, request.session, request.user.username):
                messages.success(request, 'Successfully created donation!')
            else:
                messages.error(request, 'Failed to create donation.')
            return redirect('/donate')
    else:
        # team_choices = classy.get_teams(request.session)
        form = DonationForm(fundraiser_choices)

    return render(request, 'core/donate.html', __add_context(request, {'form': form}))


@staff_member_required(login_url="/login")
def approve(request):
    donations = classy.get_under_review_donations(request.session)

    if request.method == 'POST':
        form = ApproveDonationForm(donations, request.POST)
        if form.is_valid():
            success_count = 0
            error_count = 0
            for donation_id in form.cleaned_data['donation_ids']:
                if classy.approve_donation(donation_id, request.session, request.user.username):
                    success_count += 1
                else:
                    error_count += 1

            if error_count == 0:
                messages.success(request, 'Successfully approved donations!')
            elif success_count > 0 and error_count > 0:
                messages.warning(request, 'Successfully approved some donations, but some failed.')
            return redirect('/approve')
    else:
        form = ApproveDonationForm(donations)

    return render(request, 'core/approve.html', __add_context(request, {'donations': donations, 'form': form}))


@staff_member_required(login_url="/login")
def unapprove(request, donation_id):
    if classy.unapprove_donation(donation_id, request.session, request.user.username):
        messages.success(request, 'Successfully unapproved the donation.')
    else:
        messages.error(request, 'Failed to unapprove donation.')
    return redirect('/approve')


def __add_context(request, context={}):
    context['organization_name'] = os.environ['ORG_NAME']
    context['is_classy_member'] = 'CLASSY_MEMBER_ID' in request.session\
                                  and request.session['CLASSY_MEMBER_ID'] is not None
    return context
