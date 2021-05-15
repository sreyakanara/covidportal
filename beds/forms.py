from django.forms import ModelForm
from .models import Patient, BedAllocation

class PatientForm(ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age','location', 'district', 'phone', 'aadharno', 'category']

class BedAllocationForm(ModelForm):
    class Meta:
        model = BedAllocation
        fields = ['patient', 'category']

    def __init__(self, hospital=None, **kwargs):
        super(BedAllocationForm, self).__init__(**kwargs)
        self.fields['patient'].queryset = Patient.objects.filter(district=hospital.district, status='W')
