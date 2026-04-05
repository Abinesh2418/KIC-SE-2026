from django.urls import path
from . import views

app_name = 'debugchallenge'

urlpatterns = [
    # Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Participant
    path('waiting/', views.waiting_room, name='waiting_room'),
    path('challenge/', views.challenge_view, name='challenge'),
    path('api/upload-submission/', views.upload_submission, name='upload_submission'),
    path('api/tab-switch/', views.record_tab_switch, name='tab_switch'),
    path('api/submit/', views.submit_challenge, name='submit_challenge'),
    path('api/time-remaining/', views.time_remaining, name='time_remaining'),
    path('api/event-status/', views.event_status, name='event_status'),
    path('result/', views.result_view, name='result'),
    path('download-notebook/<int:challenge_id>/', views.download_notebook, name='download_notebook'),
    path('download-all-materials/', views.download_all_materials, name='download_all_materials'),

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
    path('admin-dashboard/reset-challenge/', views.reset_challenge, name='reset_challenge'),
    path('admin-dashboard/remove/<int:participant_id>/', views.remove_participant, name='remove_participant'),
    path('admin-dashboard/remove-all-users/', views.remove_all_users, name='remove_all_users'),
    path('admin-dashboard/submissions/<int:participant_id>/', views.view_submissions, name='view_submissions'),
    path('admin-dashboard/grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('admin-dashboard/download-submission/<int:submission_id>/', views.download_submission, name='download_submission'),

    # Evaluator management (admin)
    path('admin-dashboard/set-role/<int:participant_id>/', views.set_role, name='set_role'),
    path('admin-dashboard/evaluators/', views.evaluator_management, name='evaluator_management'),
    path('admin-dashboard/evaluators/assign/', views.assign_participants, name='assign_participants'),

    # Evaluator panel (evaluator users)
    path('evaluator/', views.evaluator_panel, name='evaluator_panel'),
    path('evaluator/grade/<int:participant_id>/', views.evaluate_participant, name='evaluate_participant'),
]
