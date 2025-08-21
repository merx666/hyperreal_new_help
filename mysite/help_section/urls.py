from django.urls import path
from . import views

urlpatterns = [
    path('', views.help_view, name='help_page'),
    path('kategorie-placowek/', views.facility_categories_view, name='facility_categories'),
    path('search/', views.search_facilities, name='search_facilities'),
    path('alfabetyczny-spis/', views.facility_list_alphabetical, name='facility_list_alphabetical'),
    path('alfabetyczny-spis/<str:letter>/', views.facility_list_alphabetical, name='facility_list_alphabetical_letter'),
    path('mapa-placowek/', views.facility_map_view, name='facility_map'),
    path('api/map-data/', views.facility_map_data, name='facility_map_data'),
    path('najlepsze-placowki/', views.top_rated_facilities, name='top_rated_facilities'),
    path('api/newsletter/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('faq/', views.faq_view, name='faq'),
    # Nowy, generyczny wzorzec URL dla kategorii
    path('kategorie/<str:category_type>/<slug:category_slug>/', views.facility_list_by_category, name='facility_list_by_category'),
    path('placowka/<slug:slug>/', views.facility_detail_view, name='facility_detail'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    # URLs dla systemu powiadomień
    path('powiadomienia/', views.notifications_view, name='notifications'),
    path('ustawienia-powiadomien/', views.notification_preferences_view, name='notification_preferences'),
    path('api/unread-notifications/', views.get_unread_notifications_count, name='unread_notifications_count'),
    path('api/mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/create-samples/', views.create_sample_notifications, name='create_sample_notifications'),
]
