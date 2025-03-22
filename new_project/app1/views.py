from django.shortcuts import render
# from django.http import HttpResponse
from .models import IntrusionEvent

def display(req):
    return render(req,'login.html')


def dashboard(request):
    intrusion_events = IntrusionEvent.objects.values('id', 'timestamp', 'video', 'image')
    return render(request, "dash.html", {"intrusion_events": intrusion_events})
