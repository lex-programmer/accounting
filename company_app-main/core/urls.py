from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),

    # Агенты (Suppliers)
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    # Контракты (Contracts)
    path('contracts/', views.contract_list, name='contract_list'),
    path('contracts/add/', views.contract_add, name='contract_add'),
    path('contracts/<int:pk>/edit/', views.contract_edit, name='contract_edit'),
    path('contracts/<int:pk>/delete/', views.contract_delete, name='contract_delete'),

    # Накладные (Facturi)
    path('facturi/', views.factura_list, name='factura_list'),
    path('facturi/add/', views.factura_add, name='factura_add'),
    path('facturi/<int:pk>/edit/', views.factura_edit, name='factura_edit'),
    path('facturi/<int:pk>/delete/', views.factura_delete, name='factura_delete'),
    path("factura/<int:pk>/", views.factura_detail, name="factura_detail"),
    path("facturi/archive/", views.factura_archive, name="factura_archive"),

    # Платежи (Plati)
    path('plati/', views.plata_list, name='plata_list'),
    path('plati/add/', views.plata_add, name='plata_add'),
    path('plati/<int:pk>/edit/', views.plata_edit, name='plata_edit'),
    path('plati/<int:pk>/delete/', views.plata_delete, name='plata_delete'),
    path("plati/<int:pk>/", views.plata_detail, name="plata_detail"),
    path('plati/<int:pk>/pdf/', views.plata_pdf, name='plata_pdf'),

    # Отчеты и Архивы
    path("report/plati/", views.report_plati, name="report_plati"),
    path('reports/contracts/', views.report_contracts, name='report_contracts'),

    # Банковские счета (Conturi Bancare)
    path('suppliers/<int:supplier_id>/conturi/', views.cont_bancar_list, name='cont_bancar_list'),
    # Оставляем только эту
    path('suppliers/<int:supplier_id>/conturi/<int:pk>/edit/', views.cont_bancar_edit, name='cont_bancar_edit'),
    path('suppliers/<int:supplier_id>/conturi/add/', views.cont_bancar_add, name='cont_bancar_add'),
    path("conturi/<int:pk>/delete/", views.cont_bancar_delete, name="cont_bancar_delete"),

    # Бюджетные линии и Загрузка (Linia Bugetara & Upload)
    path('linia-bugetara/', views.linia_bugetara_view, name='linia_bugetara'),
    path('handle-excel-upload/', views.handle_excel_upload, name='handle_excel_upload'),
    path('search-budget-lines/', views.search_budget_lines, name='search_budget_lines'),

    # AJAX-автозаполнение (Autocomplete)
    path("ajax/eco-autocomplete/", views.eco_autocomplete, name="eco_autocomplete"),
    path('ajax/coduri-buget-autocomplete/', views.budget_line_autocomplete, name='budget_line_autocomplete'),
    # <-- Новый рабочий путь

]