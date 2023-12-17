from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("tests", views.ListTestView.as_view(), name="testindex"),
    path("tests/<test_number>/<poll_number>/", views.DetailTestPollView.as_view(), name="firstquestion"),
    path("tests/result/<test_number>", views.ResultView.as_view(), name="result"),
    path("tests/<test_number>/<poll_number>/vote/", views.vote, name="vote"),
]
