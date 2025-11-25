# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum

class AgentiComerciali(models.Model):
    cod = models.CharField(max_length=50, unique=True)
    denumirea = models.CharField(max_length=255)
    cod_fiscal = models.CharField(max_length=50)
    denumirea_completa = models.CharField(max_length=255, blank=True, null=True)
    conducator = models.CharField(max_length=255, blank=True, null=True)
    forma_juridica = models.CharField(max_length=100, blank=True, null=True)
    adresa_juridica = models.CharField(max_length=255, blank=True, null=True)
    adresa_postala = models.CharField(max_length=255, blank=True, null=True)
    telefoane = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    rezident = models.BooleanField(default=False)
    tara = models.CharField(max_length=100, blank=True, null=True)
    cod_tva = models.CharField(max_length=50, blank=True, null=True)
    cont_bancar_iban = models.CharField(max_length=34, blank=True, null=True)
    contract_baza = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "agenti_comerciali"

    def __str__(self):
        return f"{self.denumirea} ({self.cod_fiscal})"


class EcoCode(models.Model):
    cod = models.CharField(max_length=50, unique=True)
    descriere = models.CharField(max_length=255)

    class Meta:
        db_table = "eco_coduri"

    def __str__(self):
        return f"{self.cod} — {self.descriere}"


class BudgetLine(models.Model):
    cod_bugetar = models.CharField(max_length=50, unique=True)
    denumirea = models.CharField(max_length=255)
    suma_alocata = models.DecimalField(max_digits=18, decimal_places=2)
    anul = models.IntegerField(default=2025)
    file_name = models.CharField(max_length=255, blank=True, null=True)  # Добавляем
    created_at = models.DateTimeField(auto_now_add=True)  # Добавляем

    def __str__(self):
        return f"{self.cod_bugetar} - {self.denumirea}"

    class Meta:
        db_table = "linii_bugetare"

    @property
    def suma_cheltuita(self):
        return self.items.aggregate(total=Sum('suma'))['total'] or 0

    @property
    def suma_ramasa(self):
        return self.suma_alocata - self.suma_cheltuita

    @property
    def procent_cheltuit(self):
        if self.suma_alocata > 0:
            return round((self.suma_cheltuita / self.suma_alocata) * 100, 2)
        return 0


class Contracte(models.Model):
    cod = models.CharField(max_length=50, unique=True)
    denumirea = models.CharField(max_length=255)
    institutia = models.CharField(max_length=255, blank=True, null=True)
    programul = models.CharField(max_length=255, blank=True, null=True)
    componente_de_sursa = models.CharField(max_length=255, blank=True, null=True)
    originea_sursei = models.CharField(max_length=255, blank=True, null=True)
    iban = models.CharField(max_length=34, blank=True, null=True)

    agent = models.ForeignKey(AgentiComerciali, on_delete=models.CASCADE, related_name="contracte")
    contul_de_decontare = models.CharField(max_length=255, blank=True, null=True)

    nr_contractului = models.CharField(max_length=100)
    data_contractului = models.DateField()
    conditii_plata = models.CharField(max_length=255, blank=True, null=True)
    termen_valabilitate = models.DateField(blank=True, null=True)
    suma_contractului = models.DecimalField(max_digits=18, decimal_places=2)
    cota_avans = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    suma_in_valuta = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    cod_obiectului = models.CharField(max_length=100, blank=True, null=True)
    cod_valutei = models.CharField(max_length=10, blank=True, null=True)
    continut_prescurtat = models.TextField(blank=True, null=True)
    data_indeplinirii_obligatiilor = models.DateField(blank=True, null=True)
    masura = models.CharField(max_length=255, blank=True, null=True)

    contractul_nu_este_inregistrat_la_trezorerie = models.BooleanField(default=False)
    prin_achizitii_publice = models.BooleanField(default=False)
    contract_produse_alimentare = models.BooleanField(default=False)
    eco = models.ForeignKey("EcoCode", on_delete=models.SET_NULL, null=True, blank=True)

    linie_bugetara = models.ForeignKey(
        "BudgetLine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracte"
    )


    class Meta:
        db_table = "contracte"
    def suma_ramasa(self):
        return (self.suma_contractului or 0) - (self.cota_avans or 0)
    
    def __str__(self):
        return f"{self.nr_contractului} - {self.denumirea}"





class Factura(models.Model):
    contract = models.ForeignKey(Contracte, on_delete=models.CASCADE, related_name="facturi")
    numar = models.CharField(max_length=100)
    data_facturii = models.DateField()
    suma_facturii = models.DecimalField(max_digits=18, decimal_places=2)
    valuta = models.CharField(max_length=10, blank=True, null=True)
    comentariu = models.TextField(blank=True, null=True)

    contract_is_planned = models.BooleanField(
        default=True,
        verbose_name="Contractul este planificat?"  # "Контракт запланирован?"
    )

    budget_line = models.ForeignKey(
        BudgetLine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facturi"
    )

    def clean(self):
        # Сохраняем общую сумму по контракту (без текущей фактуры)
        self._contract_total = \
        Factura.objects.filter(contract=self.contract).exclude(pk=self.pk).aggregate(Sum('suma_facturii'))[
            'suma_facturii__sum'] or 0

        # Сохраняем общую сумму по строке бюджета (если есть)
        self._budget_total = None
        if self.budget_line:
            self._budget_total = \
            Factura.objects.filter(budget_line=self.budget_line).exclude(pk=self.pk).aggregate(Sum('suma_facturii'))[
                'suma_facturii__sum'] or 0

    def save(self, *args, **kwargs):
        self.full_clean()  # вызовет clean() перед сохранением
        super().save(*args, **kwargs)
    class Meta:
        db_table = "facturi"

    def __str__(self):
        return f"Factura {self.numar} ({self.contract.denumirea})"





class FacturaItem(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="items")
    denumirea = models.CharField(max_length=255)
    cantitate = models.DecimalField(max_digits=12, decimal_places=2)
    pret_unitar = models.DecimalField(max_digits=12, decimal_places=2)
    suma = models.DecimalField(max_digits=18, decimal_places=2)

    budget_line = models.ForeignKey(
        BudgetLine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items"
    )

    def clean(self):
        if self.budget_line:
            total_existing = FacturaItem.objects.filter(
                denumirea=self.denumirea,
                budget_line=self.budget_line
            ).exclude(pk=self.pk).aggregate(Sum('suma'))['suma__sum'] or 0

            total_after = total_existing + self.suma
            if total_after > self.budget_line.suma_alocata:
                raise ValidationError(
                    f"Totalul pentru produsul „{self.denumirea}” va fi {total_after} MDL, ceea ce depășește bugetul alocat ({self.budget_line.suma_alocata} MDL)."
                )

    def save(self, *args, **kwargs):
        self.suma = self.cantitate * self.pret_unitar
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "factura_items"

    def __str__(self):
        return f"{self.denumirea} ({self.cantitate} x {self.pret_unitar})"

class Plata(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="plati")
    data_platii = models.DateField()
    suma_platita = models.DecimalField(max_digits=18, decimal_places=2)
    metoda = models.CharField(
        max_length=20,
        choices=[
            ("cash", "Cash"),
            ("bank", "Transfer Bancar"),
            ("card", "Card"),
            ("other", "Altele"),
        ],
        default="bank"
    )
    numar_document = models.CharField(max_length=100)

    class Meta:
        db_table = "plati"

    def __str__(self):
        return f"Plata {self.numar_document} - {self.suma_platita}"

class ContBancar(models.Model):
    agent = models.ForeignKey(
        "AgentiComerciali",
        on_delete=models.CASCADE,
        related_name="conturi",
        null=True,
        blank=True
    )
    denumirea = models.CharField(max_length=255)
    iban = models.CharField(max_length=34)
    tip_cont = models.CharField(max_length=50,)
    valuta = models.CharField(max_length=10, blank=True, null=True)
    banca_organizatiei = models.CharField(max_length=255, blank=True, null=True)
    banca_corespondent = models.CharField(max_length=255, blank=True, null=True)
    data_deschiderii = models.DateField(blank=True, null=True)
    data_inchiderii = models.DateField(blank=True, null=True)

    cod_fiscal_trezorerie = models.CharField(max_length=50, blank=True, null=True)
    prin_trezoreria = models.CharField(max_length=255, blank=True, null=True)
    denumirea_trezoreriei = models.CharField(max_length=255, blank=True, null=True)
    numar_cont_trezorerie = models.CharField(max_length=34, blank=True, null=True)
    decontari_directe = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.iban} ({self.denumirea})"

    class Meta:
        db_table = "cont_bancar"







