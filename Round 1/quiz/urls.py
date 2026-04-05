from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Participant
    path('waiting/', views.waiting_room, name='waiting_room'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('api/save-answer/', views.save_answer, name='save_answer'),
    path('api/tab-switch/', views.record_tab_switch, name='tab_switch'),
    path('api/submit/', views.submit_quiz, name='submit_quiz'),
    path('api/time-remaining/', views.time_remaining, name='time_remaining'),
    path('api/event-status/', views.event_status, name='event_status'),
    path('result/', views.result_view, name='result'),

    # Leaderboard
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('leaderboard/export/', views.export_leaderboard_xlsx, name='export_leaderboard'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/approve/<int:participant_id>/', views.approve_participant, name='approve_participant'),
    path('admin-dashboard/disqualify/<int:participant_id>/', views.disqualify_participant, name='disqualify_participant'),
    path('admin-dashboard/start-event/', views.start_event, name='start_event'),
    path('admin-dashboard/stop-event/', views.stop_event, name='stop_event'),
    path('admin-dashboard/update-settings/', views.update_settings, name='update_settings'),
    path('admin-dashboard/approve-all/', views.approve_all, name='approve_all'),
    path('admin-dashboard/reset-quiz/', views.reset_quiz, name='reset_quiz'),
    path('admin-dashboard/remove/<int:participant_id>/', views.remove_participant, name='remove_participant'),
    path('admin-dashboard/remove-all-users/', views.remove_all_users, name='remove_all_users'),
]
