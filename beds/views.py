from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Hospital, Patient, BedAllocation
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import PatientForm, BedAllocationForm
from django.shortcuts import redirect
# Create your views here.

def index(request):
    normal_beds = Hospital.objects.aggregate(total=Sum('normal_beds'))
    covid_beds = Hospital.objects.aggregate(total=Sum('covid_beds'))
    icu = Hospital.objects.aggregate(total=Sum('icu_beds'))
    ventilator = Hospital.objects.aggregate(total=Sum('ventilator'))

    page = request.GET.get('page', 1)
    hospital_list = Hospital.objects.all()
    paginator = Paginator(hospital_list, 5)
    try:
        hospitals = paginator.page(page)
    except PageNotAnInteger:
        hospitals = paginator.page(1)
    except EmptyPage:
        hospitals = paginator.page(paginator.num_pages)

    context = {
        'normal_beds': normal_beds,
        'covid_beds': covid_beds,
        'icu': icu,
        'ventilator': ventilator,
        'hospitals': hospitals
    }
    return render(request, 'beds/summary.html', context)

@login_required
def dashboard(request):
    user = request.user
    hospital = Hospital.objects.get(user=user)
    bedallocations = BedAllocation.objects.filter(hospital=hospital)
    context = {
        'bedallocations': bedallocations,
        'hospital': hospital
    }
    return render(request, 'beds/dashboard.html', context)

@login_required
def bedallocate(request):
    user = request.user
    hospital = Hospital.objects.get(user=user)
    form = BedAllocationForm(data=request.POST or None, hospital=hospital or None)
    context = {
        'form': form,
    }
    if form.is_valid():
        obj=form.save(commit=False)
        obj.hospital = hospital
        patient = Patient.objects.get(pk=obj.patient.id)
        patient.status = 'A'
        patient.save()
        if obj.category == 'C':
            hospital.covid_beds = hospital.covid_beds - 1
        elif obj.category == 'N':
            hospital.normal_beds = hospital.normal_beds - 1
        elif obj.category == 'I':
             hospital.icu_beds = hospital.icu_beds - 1
        else:
            hospital.ventilator = hospital.ventilator - 1
        hospital.save()
        obj.save()
        return redirect('dashboard')
    return render(request, 'beds/bedallocate.html', context)

@login_required
def discharge(request, id):
    bed = BedAllocation.objects.get(pk=id)
    hospital = Hospital.objects.get(pk=bed.hospital.id)
    patient = Patient.objects.get(pk=bed.patient.id)
    patient.status = 'D'
    patient.save()
    if bed.category == 'C':
        hospital.covid_beds = hospital.covid_beds + 1
    elif bed.category == 'N':
        hospital.normal_beds = hospital.normal_beds + 1
    elif bed.category == 'I':
         hospital.icu_beds = hospital.icu_beds + 1
    else:
        hospital.ventilator = hospital.ventilator + 1
    hospital.save()
    bed.delete()
    return redirect('dashboard')

def patient_reg(request):
    form = PatientForm(request.POST or None)
    context= {
    'form':form
    }
    if form.is_valid():
        form.save()
        return redirect('index')
    return render(request, 'beds/patient_registration.html', context)
