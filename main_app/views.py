from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Plant, CareLog
from django.utils import timezone

def home(request):
    return render(request, 'home.html')

@login_required
def plant_index(request):
    plants = Plant.objects.filter(user=request.user)
    return render(request, 'plants/index.html', {'plants': plants})

@login_required
def plant_detail(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id, user=request.user)
    care_logs = CareLog.objects.filter(plant=plant).order_by('-date_logged')
    return render(request, 'plants/detail.html', {'plant': plant, 'care_logs': care_logs})

@login_required
def plant_create(request):
    if request.method == 'POST':
        plant = Plant(
            user=request.user,
            plant_family=request.POST['plant_family'],
            nickname=request.POST.get('nickname', ''),
            variety=request.POST.get('variety', ''),
            notes=request.POST.get('notes', ''),
        )
        plant.save()
        return redirect('plant_index')
    return render(request, 'plants/form.html')

@login_required
def plant_edit(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id, user=request.user)
    if request.method == 'POST':
        plant.plant_family = request.POST['plant_family']
        plant.nickname = request.POST.get('nickname', '')
        plant.variety = request.POST.get('variety', '')
        plant.notes = request.POST.get('notes', '')
        plant.save()
        return redirect('plant_detail', plant_id=plant.id)
    return render(request, 'plants/form.html', {'plant': plant})

@login_required
def plant_delete(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id, user=request.user)
    if request.method == 'POST':
        plant.delete()
        return redirect('plant_index')
    return render(request, 'plants/confirm_delete.html', {'plant': plant})

@login_required
def care_log_add(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id, user=request.user)
    if request.method == 'POST':
        date_logged = request.POST.get('date_logged')
        CareLog.objects.create(
            plant=plant,
            care_type=request.POST['care_type'],
            notes=request.POST.get('notes', ''),
            date_logged=date_logged if date_logged else timezone.now(),
        )
    return redirect('plant_detail', plant_id=plant.id)

@login_required
def care_log_delete(request, care_log_id):
    care_log = get_object_or_404(CareLog, id=care_log_id, plant__user=request.user)
    plant_id = care_log.plant.id
    if request.method == 'POST':
        care_log.delete()
    return redirect('plant_detail', plant_id=plant_id)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('plant_index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})