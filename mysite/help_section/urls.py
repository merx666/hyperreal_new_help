from django.urls import path
from . import views

urlpatterns = [
    path('', views.help_view, name='help_page'),
    path('kategorie-placowek/', views.facility_categories_view, name='facility_categories'),
    # Nowy, generyczny wzorzec URL dla kategorii
    path('kategorie/<str:category_type>/<slug:category_slug>/', views.facility_list_by_category, name='facility_list_by_category'),
    path('placowka/<slug:slug>/', views.facility_detail_view, name='facility_detail'),
]
