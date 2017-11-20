from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from .forms import EnableUserForm
from .services import classy


def index(request):
    context = {}
    return render(request, 'core/index.html', context)


def donation(request):
    context = {}
    return render(request, 'core/donation.html', context)


# @permission_required('core.can_enable_user')
def enable_user(request):
    if request.method == 'POST':
        form = EnableUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if classy.has_account(email):
                # TODO: create account
                messages.success(request, 'Successfully enabled ' + email)
                return HttpResponseRedirect('/core/enable-user')
            else:
                messages.error(request, email + ' does not exist in Classy')

    else:
        form = EnableUserForm()

    return render(request, 'core/enable-user.html', {'form': form})
