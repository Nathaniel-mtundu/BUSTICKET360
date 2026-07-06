from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth import login
from .models import Customer

# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user = user, phone_number = form.cleaned_data['phone_number'])
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


# def auth_view(request):
#     mode = request.GET.get('mode', 'signup')
#     if mode == 'login':
#         form = AuthenticationForm()  # or your custom login form
#     else:
#         form = UserCreationForm()    # or your custom signup form
#     return render(request, 'registration/auth.html', {'form': form, 'mode': mode})