from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from website import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('about/', views.about, name='about'),
    path('', views.home, name='home'),
    path('team/', views.team, name='team'),
    path('legacy/', views.legacy, name='legacy'),
    path('entrance/', views.entrance, name='entrance'),
    path('contact-us/', views.contactus, name='contact'),
    path('login/', views.login_route, name='login'),
    path('signup/', views.signup_route, name='signup'),
    path('logout/', views.logout_route, name='logout'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("mocktest/<int:pk>/", views.mock_test_view, name="mock_test_view"),
   path('saving_result/', views.saving_result, name='saving_result'),
    path("save-result/", views.save_test_result, name="save_test_result"),
    path('league-data/', views.league_data, name='league_data'),
    path("get-results/", views.get_test_results, name="get_test_results"),
    
    # core
     path('save-message/', views.save_message, name='save_message'),
     path("get-messages/", views.get_messages, name="get_messages"),
    path('study/', views.study_page_route, name='study'),
    # Add a 'courses' alias to prevent missing template references
    path('courses/', views.study_page_route, name='courses'),
    path('profile/', views.profile, name='profile'),
    path('watch/<int:video_id>/', views.yt_render, name='yt_render'),
    
    # tests
    path('create_test/<int:chapter_id>/', views.create_test, name='create_test'),
    path('test/<uuid:test_id>/', views.route_test, name='route_test'),
    path('submit_test/<uuid:test_id>/', views.submit_test, name='submit_test'),
    path('analyse/<uuid:test_id>/', views.analyse, name='analyse'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)