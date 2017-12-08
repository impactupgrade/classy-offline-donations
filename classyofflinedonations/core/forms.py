from django import forms
from localflavor.us.forms import USStateField, USStateSelect


class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class LoginForm(BootstrapForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")


class EnableUserForm(BootstrapForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    email = forms.EmailField(label="Classy account's email")
    password = forms.CharField(widget=forms.PasswordInput(), label="This account's password (separate from Classy's)")


class DonationForm(BootstrapForm):
    def __init__(self, fundraiser_choices=(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fundraiser'].choices = fundraiser_choices
        # self.team = forms.ChoiceField(choices=team_choices, label="Team")

    # individual
    first_name = forms.CharField(required=False, label="First Name")
    last_name = forms.CharField(required=False, label="Last Name")
    email = forms.EmailField(required=False, label="Email")

    # company
    company_name = forms.CharField(required=False, label="Company / Organization Name")

    address = forms.CharField(required=False, label="Address")
    city = forms.CharField(required=False, label="City")
    state = USStateField(widget=USStateSelect, required=False, label="State")
    zip = forms.CharField(required=False, label="Zip")

    ANONYMOUS_CHOICES = (('SHOW_NAME', 'Show donor name in public activity feed'), ('ANONYMOUS', 'Keep donor anonymous'))
    anonymous = forms.ChoiceField(choices=ANONYMOUS_CHOICES, label="Public Activity Feed: Anonymous?")
    comment = forms.CharField(widget=forms.Textarea(), required=False, label="Public Activity Feed: Donor Comment")
    amount = forms.DecimalField(label="Donation Amount ($ USD)")
    TYPE_CHOICES = (('check', 'Check'), ('cash', 'Cash'))
    type = forms.ChoiceField(choices=TYPE_CHOICES, label="Payment Type")

    # TODO: Required for now, but will need to make optional once Team is supported.  But *one* of them is required!
    fundraiser = forms.ChoiceField(choices=(), label="Fundraiser")
