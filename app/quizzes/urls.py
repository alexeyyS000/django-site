from django.urls import path

from . import views

app_name = "quizzes"
urlpatterns = [
    path("<int:quiz_id>/", views.DetailTestView.as_view(), name="detail_test"),
    path("<int:quiz_id>/<int:question_number>/", views.DetailQuestionView.as_view(), name="start_test"),
    path("<int:quiz_id>/result", views.ResultView.as_view(), name="result"),
    path("find", views.FindView.as_view(), name="find"),
    path("attempts/<int:quiz_id>", views.AttemptsView.as_view(), name="attempts"),
    path("attempts/<int:quiz_id>/<int:attempt_id>", views.DetailAttemptView.as_view(), name="detail_attempt"),
]
