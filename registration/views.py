from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    remember_me_duration = 14 * 24 * 60 * 60  # 14 days

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.POST.get("remember_me"):
            self.request.session.set_expiry(self.remember_me_duration)
        else:
            self.request.session.set_expiry(0)
        return response


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("password_change_done")


def signup_view(request):

    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("homePage")

    return render(request, "registration/signup.html", {
        "form": form
    })
