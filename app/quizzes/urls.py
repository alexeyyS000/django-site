from django.urls import path

from . import views

app_name = "quizzes"
urlpatterns = [
    path("", views.ListTestView.as_view(), name="testindex"),
    path("<quiz_id>/", views.DetailTestView.as_view(), name="detail_test"),
    path("<quiz_id>/<question_number>/", views.DetailQuestionView.as_view(), name="start_test"),
    path("result/<quiz_id>", views.ResultView.as_view(), name="result"),
    path("find", views.FindView.as_view(), name="find"),
    path("attempts/<quiz_id>", views.AttemptsView.as_view(), name="attempts"),
    path("attempts/<quiz_id>/<attempt_id>", views.DetailAttemptView.as_view(), name="detail_attempt"),
]
