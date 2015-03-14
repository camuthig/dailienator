from django import forms

class SupportRequestForm(forms.Form):
    # Fields needed:
    #   support category
    #   issues description
    email = forms.EmailField(
        label="Email Address",
        required=False
    )
    issue_category = forms.ChoiceField(
        label="Issue Category",
        required=True,
        choices=[
            ('Login Support', 'Login Support'),
            ('User Administration', 'User Administration'),
            ('Account Administration', 'Account Administration'),
            ('Daily Generation', 'Daily Generation'),
            ('Other', 'Other')]
    )
    issue_description = forms.CharField(
        label="Issue Description",
        required=True,
        widget=forms.Textarea(attrs={'rows':4})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SupportRequestForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        # run the parent validation first
        valid = super(SupportRequestForm, self).is_valid()

        # we're done now if not valid
        if not valid:
            return valid

        # Validate that if the user is not authenticated, they provided an
        # email address
        if not self.user.is_authenticated():
            if not self.cleaned_data['email']:
                return False

        return True