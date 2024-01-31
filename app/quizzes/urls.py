from django.urls import path

from . import views

app_name = "quizzes"
urlpatterns = [
    path("", views.ListTestView.as_view(), name="testindex"),
    path("<test_number>/<question_number>/", views.DetailQuestionView.as_view(), name="firstquestion"),
    path("result/<test_number>", views.ResultView.as_view(), name="result"),
    path("find", views.FindView.as_view(), name="find"),
    path("filter", views.FilterView.as_view(), name="filter"),
]
