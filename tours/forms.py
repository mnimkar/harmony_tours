from django import forms

from .models import Enquiry


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = [
            "name",
            "email",
            "mobile",
            "city",
            "adults",
            "children_5_12",
            "children_below_5",
            "travel_date",
            "message",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Name", "required": True}),
            "email": forms.EmailInput(attrs={"placeholder": "Email", "required": True}),
            "mobile": forms.TextInput(attrs={"placeholder": "Mobile", "required": True}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "adults": forms.NumberInput(attrs={"min": 1, "max": 30}),
            "children_5_12": forms.NumberInput(attrs={"min": 0, "max": 15}),
            "children_below_5": forms.NumberInput(attrs={"min": 0, "max": 15}),
            "travel_date": forms.DateInput(attrs={"type": "date"}),
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Message"}),
        }
