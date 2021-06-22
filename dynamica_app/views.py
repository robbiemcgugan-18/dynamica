from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from dynamica_app.models import Event, PartFormat, Music, Request, UserProfile
from django.core import serializers
from dynamica_app.forms import AddMusicForm, RequestForm
import json
from django.http import JsonResponse
from django.contrib import messages

def index(request):
    context_dict = {}

    return render(request, 'dynamica_app/index.html', context_dict)

def user_login(request):
    # Define the context dictionary with an empty error message
    context_dict = {'error_message': None}

    # If the method is POST (form has been submitted) the form will be processed
    if request.method == 'POST':
        # Get the username and password values from the POST request
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Attempt to authenticate the user with the provided details
        user = authenticate(username=username, password=password)

        # If a user with the given username and password exists
        if user:
            # Check that their account is still active
            # If it is then log the user in
            if user.is_active:
                login(request, user)

                # Redirect the user back to the home page
                return redirect(reverse('menu'))

            # If the account exists but is disabled, display an error message
            else:
                context_dict['error_message'] = "Account is disabled. Please contact Robbie McGugan for further details"

        # If an account with the given details does not exist, display an error message
        else:
            context_dict['error_message'] = "Username or Password is incorrect"

    # If the form has not been submitted, render the view onscreen
    return render(request, 'dynamica_app/login.html', context=context_dict)

@login_required
def menu(request):
    context_dict = {}

    if request.user.groups.filter(Q(name='Admin') | Q(name='Staff')).exists():
        context_dict['authorised'] = True
    else:
        context_dict['authorised'] = False

    return render(request, 'dynamica_app/landing.html', context=context_dict)

@login_required
def user_logout(request):
    # Log the user out
    logout(request)

    # Redirect the user back to the home page
    return redirect(reverse('index'))

@login_required
def request_music(request):
    context_dict = {}

    form = RequestForm()

    if request.method == "POST":
        form = RequestForm(request.POST)

        if form.is_valid():
            request_form = form.save(commit=False)
            request_form.user = UserProfile.objects.get(user=request.user.id)
            request_form.save()
            context_dict['success_message'] = "Successfully requested a piece of music. You can view this request in My Requests."


    if request.GET.get('action') == 'get':
        piece_name = request.GET.get('piece_name')

        if piece_name != "":
            part_format_data = Music.objects.get(name=piece_name).part_format.part_data
            part_format_list = part_format_data.split(",")

            return render(request, 'dynamica_app/part_dropdown_options.html', {'part_format_list': part_format_list})

    context_dict['form'] = form

    return render(request, 'dynamica_app/request_music.html', context=context_dict)

@login_required
def permission_denied(request):
    return render(request, 'dynamica_app/permission_denied.html')

@login_required
def calendar(request):
    context_dict = {}

    events = serializers.serialize("json", Event.objects.all())
    context_dict["events"] = events

    return render(request, 'dynamica_app/calendar.html', context=context_dict)

@login_required
@user_passes_test(lambda u: u.groups.filter(Q(name='Admin') | Q(name='Staff')).exists(), login_url='permission_denied', redirect_field_name=None)
def manage_calendar(request):
    context_dict = {}

    if request.GET.get('action') == 'get':
        event_data = json.loads(request.GET.get('event_data'))

        if request.GET.get('task') == 'add':
            if event_data["end"] == "":
                event = Event(name=event_data["name"], location=event_data["location"], start=event_data["start"], year=event_data["year"], month=event_data["month"], day=event_data["day"])
            else:
                event = Event(name=event_data["name"], location=event_data["location"], start=event_data["start"], end=event_data["end"], year=event_data["year"], month=event_data["month"], day=event_data["day"])
            event.save()

        elif request.GET.get('task') == 'delete':
            print(event_data["day"], event_data["month"], event_data["year"])
            event = Event.objects.filter(name=event_data["name"], year=event_data["year"], month=event_data["month"], day=event_data["day"])
            event.delete()

    events = serializers.serialize("json", Event.objects.all())
    context_dict["events"] = events

    return render(request, 'dynamica_app/manage_calendar.html', context=context_dict)

@login_required
@user_passes_test(lambda u: u.groups.filter(Q(name='Admin') | Q(name='Staff')).exists(), login_url='permission_denied', redirect_field_name=None)
def add_music(request):
    context_dict = {}

    form = AddMusicForm()

    if request.method == "POST":
        form = AddMusicForm(request.POST)
        if form.is_valid():
            form.save()
            context_dict['success_message'] = "Successfully created new piece of music"

    elif request.GET.get('action') == 'get':
        part_format_name = request.GET.get('format_name')
        part_format_data = PartFormat.objects.filter(name=part_format_name)[0].part_data
        return JsonResponse(part_format_data, safe=False)

    context_dict['form'] = form
    return render(request, 'dynamica_app/add_music.html', context=context_dict)

@login_required
@user_passes_test(lambda u: u.groups.filter(Q(name='Admin') | Q(name='Staff')).exists(), login_url='permission_denied', redirect_field_name=None)
def view_requests(request):
    context_dict = {}

    if request.GET.get('action') == 'get':
        request_id = request.GET.get('request_id')
        req = Request.objects.get(id=request_id)

        if req.completed == True:
            req.completed = False
            req.save()
        else:
            req.completed = True
            req.save()

        return JsonResponse({'request_id': request_id, 'complete': req.completed})

    context_dict['requests'] = Request.objects.all().order_by('-time')

    return render(request, 'dynamica_app/view_requests.html', context=context_dict)

@login_required
def my_requests(request):
    context_dict = {}

    requests = Request.objects.filter(user=request.user.id).order_by('-time')
    context_dict['requests'] = requests

    return render(request, 'dynamica_app/my_requests.html', context=context_dict)
