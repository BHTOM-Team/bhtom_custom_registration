from bhtom_base.bhtom_common.forms import CustomUserCreationForm


class OpenRegistrationForm(CustomUserCreationForm):
    """
    Form for handling open registration requests. Does not render any groups, as the user cannot choose their own
    groups.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('groups')
