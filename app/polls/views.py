from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from .models import Choice
from .models import Question
from .models import Test


class IndexTestView(generic.ListView):
    template_name = "polls/tests.html"
    context_object_name = "latest_tests_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Test.objects.order_by("time_for_complite")[:5]


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("question_text")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"


class DetailTestView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(test_id=self.kwargs["int"]).order_by("question_text")[:5]


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
