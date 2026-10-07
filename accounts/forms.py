from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label="Full name")
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "Your name",
            "username": "Pick a unique username",
            "email": "you@example.com",
            "password1": "Create a password",
            "password2": "Repeat the password",
        }
        for name, field in self.fields.items():
            field.widget.attrs["placeholder"] = placeholders.get(name, "")


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["password"].widget.attrs["placeholder"] = "Password"


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False, label="First name")
    last_name = forms.CharField(max_length=50, required=False, label="Last name")

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "bio", "location", "website", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3, "placeholder": "Tell people a little about yourself…", "maxlength": 300}),
            "location": forms.TextInput(attrs={"placeholder": "City, Country"}),
            "website": forms.URLInput(attrs={"placeholder": "https://"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
            profile.save()
        return profile
