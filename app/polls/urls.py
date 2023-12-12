from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("tests", views.IndexTestView.as_view(), name="testindex"),
    path("tests/<int>/", views.DetailTestView.as_view(), name="detailtest"),
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
