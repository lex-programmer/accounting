import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
from .models import AgentiComerciali, Contracte, Factura, Plata, ContBancar, BudgetLine, EcoCode
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, DecimalField
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from datetime import datetime
from django.db.models import Q
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .forms import ContBancarForm, ContracteForm
from .forms import SupplierForm
from django.contrib import messages
from django.http import JsonResponse
from .forms import ExcelUploadForm
from django.views.decorators.csrf import csrf_exempt
from .serializers import BudgetLineSerializer
from .services.excel_parser import BudgetExcelParser


@login_required
def home(request):
    return render(request, "core/home.html")


# agenti
class SupplierForm(forms.ModelForm):
    class Meta:
        model = AgentiComerciali
        fields = [
            "cod", "denumirea", "cod_fiscal", "denumirea_completa",
            "conducator", "forma_juridica", "adresa_juridica", "adresa_postala",
            "telefoane", "email", "rezident", "tara", "cod_tva",
            "cont_bancar_iban", "contract_baza"
        ]


@login_required
def supplier_list(request):
    suppliers = AgentiComerciali.objects.all()
    return render(request, "core/supplier_list.html", {"suppliers": suppliers})


def supplier_add(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm()
    return render(request, "core/supplier_form.html", {"form": form})


def supplier_edit(request, pk):
    supplier = get_object_or_404(AgentiComerciali, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "core/supplier_form.html", {"form": form})


def supplier_delete(request, pk):
    supplier = get_object_or_404(AgentiComerciali, pk=pk)
    supplier.delete()
    return redirect("supplier_list")


# контракты

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contracte
        fields = [
            "cod", "denumirea", "institutia", "programul", "componente_de_sursa",
            "originea_sursei", "iban", "eco", "agent", "contul_de_decontare",
            "nr_contractului", "data_contractului", "conditii_plata",
            "termen_valabilitate", "suma_contractului", "cota_avans",
            "suma_in_valuta", "cod_obiectului", "cod_valutei",
            "continut_prescurtat", "data_indeplinirii_obligatiilor",
            "masura", "contractul_nu_este_inregistrat_la_trezorerie",
            "prin_achizitii_publice", "contract_produse_alimentare"
        ]
        widgets = {
            "data_contractului": forms.DateInput(attrs={"type": "date"}),
            "termen_valabilitate": forms.DateInput(attrs={"type": "date"}),
            "data_indeplinirii_obligatiilor": forms.DateInput(attrs={"type": "date"}),
        }


@login_required(login_url='login')
def contract_list(request):
    contracts = Contracte.objects.select_related("agent").all()

    return render(
        request,
        "core/contract_list.html",
        {"contracts": contracts},
    )


def contract_add(request):
    if request.method == "POST":
        form = ContractForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("contract_list")
    else:
        form = ContractForm()
    return render(request, "core/contract_form.html", {"form": form})


def contract_edit(request, pk):
    contract = get_object_or_404(Contracte, pk=pk)
    if request.method == "POST":
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            return redirect("contract_list")
    else:
        form = ContractForm(instance=contract)
    return render(request, "core/contract_form.html", {"form": form})


def contract_delete(request, pk):
    contract = get_object_or_404(Contracte, pk=pk)
    contract.delete()
    return redirect("contract_list")


# накладные

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ["contract", "numar", "data_facturii", "suma_facturii", "valuta", "comentariu"]
        widgets = {
            "data_facturii": forms.DateInput(attrs={"type": "date"}),
        }


@login_required(login_url='login')
def factura_list(request):
    contract_id = request.GET.get("contract")
    facturi = Factura.objects.select_related("contract").all()

    if contract_id:
        facturi = facturi.filter(contract_id=contract_id)

    total_sum = facturi.aggregate(total=Sum("suma_facturii"))["total"] or 0
    print("DEBUG total_sum =", total_sum)

    return render(
        request,
        "core/factura_list.html",
        {"facturi": facturi, "total_sum": total_sum},
    )


def factura_add(request):
    form = FacturaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("factura_list")
    return render(request, "core/factura_form.html", {"form": form, "warnings": getattr(form, "warnings", [])})



def factura_edit(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == "POST":
        form = FacturaForm(request.POST, instance=factura)
        if form.is_valid():
            form.save()
            return redirect("factura_list")
    else:
        form = FacturaForm(instance=factura)
    return render(request, "core/factura_form.html", {"form": form})


def factura_delete(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    factura.delete()
    return redirect("factura_list")

def factura_detail(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    return render(request, "core/factura_detail.html", {"factura": factura})


class PlataForm(forms.ModelForm):
    class Meta:
        model = Plata
        fields = ["factura", "data_platii", "suma_platita", "metoda", "numar_document"]
        widgets = {
            "data_platii": forms.DateInput(attrs={"type": "date"}),
        }


class PlataForm(forms.ModelForm):
    class Meta:
        model = Plata
        fields = ["factura", "data_platii", "suma_platita", "metoda", "numar_document"]


@login_required(login_url='login')
def plata_list(request):
    plati = Plata.objects.select_related("factura").all()
    return render(request, "core/plata_list.html", {"plati": plati})


def plata_add(request):
    if request.method == "POST":
        form = PlataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("plata_list")
    else:
        form = PlataForm()
    return render(request, "core/plata_form.html", {"form": form})


def plata_edit(request, pk):
    plata = get_object_or_404(Plata, pk=pk)
    if request.method == "POST":
        form = PlataForm(request.POST, instance=plata)
        if form.is_valid():
            form.save()
            return redirect("plata_list")
    else:
        form = PlataForm(instance=plata)
    return render(request, "core/plata_form.html", {"form": form})


def plata_delete(request, pk):
    plata = get_object_or_404(Plata, pk=pk)
    plata.delete()
    return redirect("plata_list")


def plata_detail(request, pk):
    plata = get_object_or_404(Plata, pk=pk)
    return render(request, "core/plata_detail.html", {"plata": plata})


print("DEBUG: plata_detail загружена")


def report_plati(request):
    plati = Plata.objects.select_related("factura__contract").all()
    return render(request, "core/report_plati.html", {"plati": plati})


def plata_pdf(request, pk):
    plata = get_object_or_404(Plata, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="plata_{plata.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Платежка")
    y -= 40

    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"ID: {plata.id}");
    y -= 20
    p.drawString(50, y, f"Дата: {plata.data_platii}");
    y -= 20
    p.drawString(50, y, f"Сумма: {plata.suma_platita}");
    y -= 20
    p.drawString(50, y, f"Метод оплаты: {plata.metoda}");
    y -= 20
    p.drawString(50, y, f"Документ: {plata.numar_document}");
    y -= 20
    p.drawString(50, y, f"Накладная: {plata.factura.numar}");
    y -= 20
    p.drawString(50, y, f"Контракт: {plata.factura.contract.denumirea}");
    y -= 20

    p.showPage()
    p.save()
    return response


def report_contracts(request):
    contracts = Contracte.objects.select_related("agent").all()
    return render(request, "core/report_contracts.html", {"contracts": contracts})


def factura_archive(request):
    facturi = Factura.objects.select_related("contract").all()
    data = request.GET.get("data")
    otpravitel = request.GET.get("otpravitel")
    poluchatel = request.GET.get("poluchatel")
    numar = request.GET.get("numar")

    if data:
        if data.startswith(">"):
            try:
                d = datetime.strptime(data[1:], "%Y-%m-%d").date()
                facturi = facturi.filter(data_facturii__gte=d)
            except:
                pass
        else:
            facturi = facturi.filter(data_facturii=data)

    if otpravitel:
        facturi = facturi.filter(contract__institutia__icontains=otpravitel)

    if poluchatel:
        facturi = facturi.filter(contract__denumirea__icontains=poluchatel)

    if numar:
        facturi = facturi.filter(numar__icontains=numar)

    return render(request, "core/factura_archive.html", {"facturi": facturi})


class ContBancarForm(forms.ModelForm):
    class Meta:
        model = ContBancar
        fields = [
            "denumirea", "iban", "tip_cont", "prin_trezoreria", "decontari_directe",
            "valuta", "denumirea_trezoreriei", "cod_fiscal_trezorerie", "numar_cont_trezorerie",
            "banca_organizatiei", "banca_corespondent", "data_deschiderii", "data_inchiderii"
        ]
        widgets = {
            "data_deschiderii": forms.DateInput(attrs={"type": "date"}),
            "data_inchiderii": forms.DateInput(attrs={"type": "date"}),
        }


def cont_bancar_list(request, supplier_id):
    supplier = get_object_or_404(AgentiComerciali, pk=supplier_id)
    conturi = ContBancar.objects.filter(agent=supplier)
    return render(request, 'core/cont_bancar_list.html', {'supplier': supplier, 'conturi': conturi})


def cont_bancar_add(request, supplier_id):
    supplier = get_object_or_404(AgentiComerciali, pk=supplier_id)

    if request.method == 'POST':
        form = ContBancarForm(request.POST)
        if form.is_valid():
            cont = form.save(commit=False)
            cont.agent = supplier
            cont.save()
            return redirect('cont_bancar_list', supplier_id=supplier.pk)
    else:
        form = ContBancarForm()

    return render(request, 'core/cont_bancar_form.html', {
        'form': form,
        'supplier': supplier
    })


def cont_bancar_edit(request, supplier_id, pk):
    supplier = get_object_or_404(AgentiComerciali, pk=supplier_id)
    cont = get_object_or_404(ContBancar, pk=pk, agent=supplier)

    if request.method == 'POST':
        form = ContBancarForm(request.POST, instance=cont)
        if form.is_valid():
            form.save()
            return redirect('cont_bancar_list', supplier_id=supplier.pk)
    else:
        form = ContBancarForm(instance=cont)

    return render(request, 'core/cont_bancar_form.html', {'form': form, 'supplier': supplier})


def cont_bancar_delete(request, pk):
    cont = get_object_or_404(ContBancar, pk=pk)
    agent_id = cont.agent.id
    cont.delete()
    return redirect("supplier_edit", pk=agent_id)


@login_required
def linia_bugetara_view(request):
    """Страница Linia Bugetara с drag&drop для Excel"""
    form = ExcelUploadForm()

    # Получаем существующие бюджетные линии для отображения
    budget_lines = BudgetLine.objects.filter(anul=2025).order_by('cod_bugetar')

    return render(request, 'core/linia_bugetara.html', {
        'form': form,
        'budget_lines': budget_lines
    })


@csrf_exempt
@login_required
def handle_excel_upload(request):
    """Обработка загруженного Excel файла через AJAX"""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        import_type = request.POST.get('import_type', 'suppliers')

        try:
            # Если это импорт бюджетных линий
            if import_type == 'budget_lines':
                return handle_budget_lines_import(excel_file)

            # Остальная твоя существующая логика
            df = pd.read_excel(excel_file)
            result = process_excel_data(df, import_type)

            return JsonResponse({
                'success': True,
                'message': f'Успешно обработано {result["processed"]} записей',
                'processed': result['processed'],
                'errors': result['errors'],
                'import_type': import_type
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Ошибка при обработке файла: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Файл не получен'
    })


def handle_budget_lines_import(excel_file):
    """Обработка импорта бюджетных линий из Excel"""
    try:
        print(f"Starting import for file: {excel_file.name}")

        # Извлекаем год из имени файла
        import re
        year_match = re.search(r'(20\d{2})', excel_file.name)
        target_year = int(year_match.group(1)) if year_match else 2025

        print(f"Target year: {target_year}")

        # Сохраняем файл временно
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            for chunk in excel_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        # Парсим Excel
        from .services.excel_parser import BudgetExcelParser
        parser = BudgetExcelParser()
        budget_data = parser.parse_budget_file(tmp_path, target_year)

        print(f"Parsed {len(budget_data)} budget lines for year {target_year}")

        # Сохраняем данные
        created_count = 0
        updated_count = 0

        for item in budget_data:
            try:
                obj, created = BudgetLine.objects.update_or_create(
                    cod_bugetar=item['cod_bugetar'],
                    anul=item['anul'],
                    defaults={
                        'denumirea': item['denumirea'],
                        'suma_alocata': item['suma_alocata'],
                        'file_name': excel_file.name
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                print(f"Error saving budget line {item['cod_bugetar']}: {e}")

        os.unlink(tmp_path)

        return JsonResponse({
            'success': True,
            'message': f'Импорт бюджетных линий за {target_year} год завершен: {created_count} новых, {updated_count} обновленных',
            'created': created_count,
            'updated': updated_count,
            'year': target_year,
            'import_type': 'budget_lines'
        })

    except Exception as e:
        print(f"Import error: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при импорте бюджетных линий: {str(e)}'
        })


@login_required
def search_budget_lines(request):
    """Поиск бюджетных линий по коду"""
    search_code = request.GET.get('cod', '').strip()
    year = request.GET.get('anul', 2025)

    try:
        budget_lines = BudgetLine.objects.filter(anul=year)

        if search_code:
            budget_lines = budget_lines.filter(cod_bugetar__icontains=search_code)

        # Ограничиваем количество результатов
        budget_lines = budget_lines.order_by('cod_bugetar')[:100]

        data = []
        for line in budget_lines:
            data.append({
                'id': line.id,
                'cod_bugetar': line.cod_bugetar,
                'denumirea': line.denumirea,
                'suma_alocata': float(line.suma_alocata),
                'suma_cheltuita': float(line.suma_cheltuita),
                'suma_ramasa': float(line.suma_ramasa),
                'procent_cheltuit': line.procent_cheltuit,
            })

        return JsonResponse({
            'success': True,
            'budget_lines': data,
            'count': len(data),
            'search_code': search_code,
            'year': year
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def eco_autocomplete(request):
    """AJAX-подсказки для поля ECO"""
    term = request.GET.get("term", "").strip()
    results = []

    if term:
        eco_list = EcoCode.objects.filter(cod__icontains=term).order_by("cod")[:20]
        for eco in eco_list:
            results.append({
                "label": f"{eco.cod} — {eco.descriere}",
                "value": eco.cod
            })

    return JsonResponse(results, safe=False)

def create_contract(request):
    form = ContracteForm(request.POST or None)
    budget_lines = BudgetLine.objects.filter(anul=2025).order_by('cod_bugetar')

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("contract_list")

    return render(request, "core/contract_form.html", {
        "form": form,
        "budget_lines": budget_lines,
    })

def autocomplete_coduri_buget(request):
    term = request.GET.get("term", "")
    results = BudgetLine.objects.filter(cod__icontains=term).values("cod", "denumirea")[:10]
    data = [{"label": f"{r['cod']} — {r['denumirea']}", "value": r["cod"]} for r in results]
    return JsonResponse(data, safe=False)



@login_required
def budget_line_autocomplete(request):
    """
    AJAX-подсказки для поля "Код объекта" (BudgetLine).
    Ищет по полю cod_bugetar и denumirea.
    """
    term = request.GET.get("term", "").strip()
    results = []

    if term:
        # Ищем по коду ИЛИ по названию
        qs = BudgetLine.objects.filter(
            Q(cod_bugetar__icontains=term) |
            Q(denumirea__icontains=term)
        ).order_by("cod_bugetar")[:20]

        for line in qs:
            results.append({
                # label: Что отображается пользователю в выпадающем списке
                "label": f"[{line.cod_bugetar}] — {line.denumirea}",
                # value: Что вставляется в поле ввода после выбора
                "value": line.cod_bugetar
            })

    return JsonResponse(results, safe=False)