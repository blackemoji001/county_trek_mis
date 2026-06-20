# reports views
from django.shortcuts import render

def revenue(request):
    return render(request, 'reports/revenue.html')