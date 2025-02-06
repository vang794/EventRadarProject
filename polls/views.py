from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CreateAccountForm

def create_account(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('account_created'))
        return render(request, 'polls/create_account.html', {'form': form})
    
    form = CreateAccountForm()
    return render(request, 'polls/create_account.html', {'form': form})

def account_created(request):
    return render(request, 'polls/account_created.html')
