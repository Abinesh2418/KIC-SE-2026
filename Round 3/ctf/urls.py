from django.urls import path
from . import views
from . import evaluation

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Auth
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/pending/', views.pending_approval, name='pending_approval'),

    # Challenges
    path('challenges/', views.challenges_list, name='challenges_list'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('challenges/<int:challenge_id>/download/<str:filename>/', views.challenge_download, name='challenge_download'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Flag submission API (AJAX)
    path('api/challenges/<int:challenge_id>/flags/<int:flag_order>/submit/', views.submit_flag, name='submit_flag'),

    # Notebook auth API (used by Jupyter notebooks)
    path('api/notebook-login/', views.notebook_login, name='notebook_login'),

    # Leaderboard
    path('leaderboard/', views.leaderboard_page, name='leaderboard'),
    path('api/leaderboard/', views.leaderboard_api, name='leaderboard_api'),
    path('leaderboard/export/', views.export_leaderboard_xlsx, name='export_leaderboard'),

    # Admin dashboard
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/toggle-event/', views.admin_toggle_event, name='admin_toggle_event'),
    path('admin-panel/toggle-leaderboard/', views.admin_toggle_leaderboard, name='admin_toggle_leaderboard'),
    path('admin-panel/reset-leaderboard/', views.admin_reset_leaderboard, name='admin_reset_leaderboard'),
    path('admin-panel/toggle-challenges/', views.admin_toggle_challenges, name='admin_toggle_challenges'),
    path('admin-panel/approve-user/<int:user_id>/', views.admin_approve_user, name='admin_approve_user'),
    path('admin-panel/reject-user/<int:user_id>/', views.admin_reject_user, name='admin_reject_user'),
    path('admin-panel/delete-user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-panel/toggle-evaluator/<int:user_id>/', views.admin_toggle_evaluator, name='admin_toggle_evaluator'),
    path('admin-panel/assign-evaluator/', views.admin_assign_evaluator, name='admin_assign_evaluator'),
    path('admin-panel/unassign-evaluator/<int:assignment_id>/', views.admin_unassign_evaluator, name='admin_unassign_evaluator'),
    path('admin-panel/reveal-challenge/<int:challenge_id>/', views.admin_toggle_challenge_reveal, name='admin_toggle_challenge_reveal'),
    path('admin-panel/reveal-all/', views.admin_reveal_all, name='admin_reveal_all'),
    path('admin-panel/hide-all/', views.admin_hide_all, name='admin_hide_all'),
    path('admin-panel/update-challenge/<int:challenge_id>/', views.admin_update_challenge, name='admin_update_challenge'),
    path('admin-panel/user-flags/', views.admin_user_flags, name='admin_user_flags'),
    path('admin-panel/regenerate-flags/<int:user_id>/', views.admin_regenerate_user_flags, name='admin_regenerate_user_flags'),
    path('admin-panel/remove-all-users/', views.remove_all_users, name='remove_all_users'),

    # Evaluator dashboard
    path('evaluator/', views.evaluator_dashboard, name='evaluator_dashboard'),
    path('evaluator/approve/<int:score_id>/', views.evaluator_approve, name='evaluator_approve'),
    path('evaluator/reject/<int:score_id>/', views.evaluator_reject, name='evaluator_reject'),

    # Evaluation endpoints (called by challenge notebooks)
    path('evaluate/challenge-1', evaluation.evaluate_challenge_1, name='evaluate_challenge_1'),
    path('evaluate/challenge-2', evaluation.evaluate_challenge_2, name='evaluate_challenge_2'),
    path('evaluate/challenge-3', evaluation.evaluate_challenge_3, name='evaluate_challenge_3'),
    path('evaluate/challenge-4', evaluation.evaluate_challenge_4, name='evaluate_challenge_4'),
    path('evaluate/challenge-5', evaluation.evaluate_challenge_5, name='evaluate_challenge_5'),
]
