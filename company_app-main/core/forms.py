from django import forms
from django.db.models import Sum
from .models import AgentiComerciali, Contracte, Factura, FacturaItem, Plata, ContBancar, EcoCode, BudgetLine


class AgentiComercialiForm(forms.ModelForm):
    class Meta:
        model = AgentiComerciali
        fields = "__all__"


class SupplierForm(forms.ModelForm):
    class Meta:
        model = AgentiComerciali
        fields = [
            "cod", "denumirea", "forma_juridica", "cod_fiscal",
            "denumirea_completa", "conducator", "adresa_juridica",
            "adresa_postala", "telefoane", "rezident", "tara",
            "cod_tva", "cont_bancar_iban", "contract_baza", "email"
        ]
        widgets = {
            "cod": forms.TextInput(attrs={"class": "form-control"}),
            "denumirea": forms.TextInput(attrs={"class": "form-control"}),
            "forma_juridica": forms.TextInput(attrs={"class": "form-control"}),
            "cod_fiscal": forms.TextInput(attrs={"class": "form-control"}),
            "denumirea_completa": forms.TextInput(attrs={"class": "form-control"}),
            "conducator": forms.TextInput(attrs={"class": "form-control"}),
            "adresa_juridica": forms.TextInput(attrs={"class": "form-control"}),
            "adresa_postala": forms.TextInput(attrs={"class": "form-control"}),
            "telefoane": forms.TextInput(attrs={"class": "form-control"}),
            "tara": forms.TextInput(attrs={"class": "form-control"}),
            "cod_tva": forms.TextInput(attrs={"class": "form-control"}),
            "cont_bancar_iban": forms.TextInput(attrs={"class": "form-control"}),
            "contract_baza": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class ContracteForm(forms.ModelForm):
    eco = forms.ModelChoiceField(
        queryset=EcoCode.objects.all().order_by("cod"),
        required=False,
        label="ECO",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    linie_bugetara = forms.ModelChoiceField(
        queryset=BudgetLine.objects.all().order_by("cod_bugetar"),
        required=False,
        label="Linie bugetară",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Contracte
        fields = "__all__"
        widgets = {
            "data_contractului": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "termen_valabilitate": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "data_indeplinirii_obligatiilor": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Обработка ECO-кода, если введён вручную
        eco_value = self.data.get("eco_select")

        if eco_value:
            eco_value = eco_value.strip()
            eco_obj, created = EcoCode.objects.get_or_create(
                cod=eco_value,
                defaults={"descriere": "Cod adăugat automat"}
            )
            cleaned_data["eco"] = eco_obj
        else:
            cleaned_data["eco"] = None

        return cleaned_data


class FacturaForm(forms.ModelForm):
    warnings = []

    # ДОБАВЛЕНО: Явное определение поля ECO как выпадающего списка
    eco = forms.ModelChoiceField(
        queryset=EcoCode.objects.all().order_by("cod"),
        required=False,
        label="Cod ECO",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Factura
        fields = [
            'numar',
            'data_facturii',
            'suma_facturii',
            'contract',
            'comentariu',
            'budget_line',
            'contract_is_planned',
            'eco',  # ДОБАВЛЕНО: Поле ECO в Meta.fields
        ]
        widgets = {
            "data_facturii": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        contract = cleaned_data.get("contract")
        eco = cleaned_data.get("eco")
        is_planned = cleaned_data.get("contract_is_planned")
        suma = cleaned_data.get("suma_facturii")
        budget_line = cleaned_data.get("budget_line")
        self.warnings = []

        # Новая логика валидации: требуется либо контракт, либо ECO
        if is_planned and not contract:
            raise forms.ValidationError("Если контракт запланирован, необходимо выбрать контракт.")
        if not is_planned and not eco:
            raise forms.ValidationError("Если контракт не запланирован, необходимо выбрать Cod ECO.")
        if is_planned and eco:
            # Предотвращаем сохранение ECO, если выбран контракт (на случай обхода JS)
            cleaned_data['eco'] = None
        if not is_planned and contract:
            # Предотвращаем сохранение контракта, если ECO выбран (на случай обхода JS)
            cleaned_data['contract'] = None

        if contract and suma:
            # ... (Ваша логика проверки суммы контракта) ...
            pass

        if budget_line and suma:
            # ... (Ваша логика проверки суммы бюджета) ...
            pass

        return cleaned_data


class FacturaItemForm(forms.ModelForm):
    class Meta:
        model = FacturaItem
        fields = "__all__"


class PlataForm(forms.ModelForm):
    class Meta:
        model = Plata
        fields = "__all__"
        widgets = {
            "data_platii": forms.DateInput(attrs={"type": "date"}),
        }


class ContBancarForm(forms.ModelForm):
    class Meta:
        model = ContBancar
        exclude = ['agent']
        fields = [
            "denumirea",
            "iban",
            "tip_cont",
            "prin_trezoreria",
            "decontari_directe",
            "valuta",
            "denumirea_trezoreriei",
            "cod_fiscal_trezorerie",
            "numar_cont_trezorerie",
            "banca_organizatiei",
            "banca_corespondent",
            "data_deschiderii",
            "data_inchiderii",
        ]
        widgets = {
            "data_deschiderii": forms.DateInput(attrs={"type": "date"}),
            "data_inchiderii": forms.DateInput(attrs={"type": "date"}),
        }


class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Importă fișier Excel")