from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views import generic

from .models import Choice
from .models import Question
from .models import Test
from .models import TestState


class ListTestView(generic.ListView):
    template_name = "polls/tests.html"
    context_object_name = "latest_tests_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Test.objects.order_by("time_for_complite")[:5]


class DetailTestPollView(View):
    template_name = "polls/detail.html"

    def get(self, request: HttpRequest, test_number, poll_number) -> HttpResponse:
        all_polls_list = Question.objects.filter(test_id=test_number)

        for i in all_polls_list:
            if i.id == int(poll_number):
                this_poll = i
                break
        try:
            TestState.objects.get(user=request.user, question=this_poll)
        except TestState.DoesNotExist:
            is_complete_question = False
        else:
            is_complete_question = True
        if len(TestState.objects.filter(user=request.user)) == len(all_polls_list):
            return HttpResponseRedirect(reverse("polls:result", kwargs={"test_number": test_number}))
        context = {
            "question": this_poll,
            "all_polls_list": all_polls_list,
            "test_number": test_number,
            "is_complete_question": is_complete_question,
        }
        return render(request, self.template_name, context)


class ResultView(View):
    template_name = "polls/results.html"

    def get(self, request: HttpRequest, test_number) -> HttpResponse:
        context = {"test_number": test_number}
        return render(request, self.template_name, context)


def vote(request, test_number, poll_number):
    question = get_object_or_404(Question, pk=poll_number)
    choice = request.POST["choice"]
    right_answers = Choice.objects.get(question=question.id, right_answer=True)
    if right_answers.choice_text == choice:
        TestState.objects.create(user=request.user, question=question, answer=True)
    else:
        TestState.objects.create(user=request.user, question=question, answer=False)

    return HttpResponseRedirect(
        reverse("polls:firstquestion", kwargs={"test_number": test_number, "poll_number": poll_number})
    )
