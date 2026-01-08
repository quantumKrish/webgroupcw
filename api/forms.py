from django import forms
from django.conf import settings

from .models import Item, Bid


class ItemAdminForm(forms.ModelForm):
    # Force an HTML5 datetime-local picker and accept the matching format.
    ends_at = forms.DateTimeField(
        input_formats=getattr(settings, "DATETIME_INPUT_FORMATS", []) + ["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "step": 60},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    starting_price = forms.DecimalField(
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01"}),
    )

    class Meta:
        model = Item
        fields = "__all__"


class BidAdminForm(forms.ModelForm):
    amount = forms.DecimalField(
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01"}),
    )

    class Meta:
        model = Bid
        fields = "__all__"
