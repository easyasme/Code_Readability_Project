from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView as AuthPasswordChangeView,
)
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import SignupForm, ProfileForm, PasswordChangeForm


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "update! :)")
            return redirect("accounts:profile_edit")
    elif request.method == "GET":
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile_edit.html", {"form": form})


def signup(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            signed_user = form.save()
            auth.login(request, signed_user)
            messages.success(request, "Welcome. :)")
            return redirect("/")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


login = LoginView.as_view(
    template_name="accounts/login.html", redirect_authenticated_user=True
)
logout = LogoutView.as_view()


class PasswordChangeView(AuthPasswordChangeView, LoginRequiredMixin):
    success_url = reverse_lazy("core:root")
    template_name = "accounts/password_change.html"
    form_class = PasswordChangeForm

    def form_valid(self, form):
        messages.success(self.request, "Success Changed! :)")
        return super().form_valid(form)
