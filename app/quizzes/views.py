from itertools import chain
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views import generic
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist

from .utils.constants import DEFAULT_SIZES_FILTER_PAGE
from .forms import AnswerQuestionForm
from .models import Question
from .models import Test
from .models import TestPipeline
from .models import TestState
from .utils.general import chop_microseconds
from .utils.general import is_time_up
from .service import TestFilter
from django.contrib.auth.mixins import LoginRequiredMixin


class ListTestView(LoginRequiredMixin, generic.ListView):
    template_name = "quizzes/tests.html"
    context_object_name = "latest_tests_list"

    def get_queryset(self):
        """Return the last five published questions."""

        return Test.objects.order_by("-created")[:20]


class ResultView(LoginRequiredMixin, View):
    template_name = "quizzes/results.html"

    def get(self, request: HttpRequest, quiz_id) -> HttpResponse:
        user = request.user
        test = Test.objects.get(id=quiz_id)
        questions = Question.objects.filter(test_id = quiz_id).order_by('id')
        for question in questions:
            TestState.objects.get_or_create(user=user, test_id=quiz_id, question=question, defaults={"answer": False})
        state = TestState.objects.filter(user=user, test=quiz_id).order_by('question_id')
        user.done_tests.add(Test.objects.get(id=quiz_id))
        user.save()
        try:
            TestPipeline.objects.get(user = user, test_id = quiz_id).delete()
        except ObjectDoesNotExist:
            pass
        # results = [i for i in questions]
        context = {"test": test, "results": state}
        return render(request, self.template_name, context)


class DetailQuestionView(LoginRequiredMixin, View):# тут очень много дублирования кода, стоит ли делить на куски и выносить в отдельную функцию ?
    template_name = "quizzes/detailtest.html"

    def get(self, request: HttpRequest, quiz_id, question_number) -> HttpResponse:
        test = Test.objects.get(id=quiz_id)
        if test in request.user.done_tests.all():
            return HttpResponseRedirect(reverse("quizzes:result", kwargs={"quiz_id": quiz_id}))
        questions = Question.objects.filter(test_id=quiz_id).order_by("text")
        current_question = questions[int(question_number) - 1]
        pipline = TestPipeline.objects.get_or_create(user=request.user, test_id=quiz_id)
        try:
            time_up = is_time_up(pipline[0].time_start, test.time_to_timedelta())
        except TimeoutError:
            return HttpResponseRedirect(reverse("quizzes:result", kwargs={"quiz_id": quiz_id}))
        answered_questions = TestState.objects.filter(user=request.user, test=test)
        context = {
            "form": AnswerQuestionForm(question=current_question),
            "time_up": chop_microseconds(time_up).total_seconds(),
            "answered_questions": [i.question_id for i in answered_questions],
            "test": test,
            "all_question_list": questions,
            "next_question": int(question_number) + 1 if int(question_number) + 1 <= len(questions) else None,
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, quiz_id, question_number) -> HttpResponse:
        test = Test.objects.get(id=quiz_id)
        questions = Question.objects.filter(test=test).order_by("text")
        current_question = questions[int(question_number) - 1]
        pipline = TestPipeline.objects.get_or_create(user=request.user, test=test)
        try:
            time_up = is_time_up(pipline[0].time_start, test.time_to_timedelta())
        except TimeoutError:
            return HttpResponseRedirect(reverse("quizzes:result", kwargs={"quiz_id": quiz_id}))
        
        form = AnswerQuestionForm(request.POST, question=current_question)
        answered_questions = TestState.objects.filter(user=request.user, test=test)
        if form.is_valid():
            form.save(request.user, test)

        context = {
                "form": form,
                "time_up": chop_microseconds(time_up).total_seconds(),
                "answered_questions": [i.question_id for i in answered_questions],
                "test": test,
                "all_question_list": questions,
                "next_question": int(question_number) + 1 if int(question_number) + 1 <= len(questions) else None,
            }
        return render(request, self.template_name, context)


class FindView(LoginRequiredMixin, View):
    template_name = "quizzes/filter.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        filter = TestFilter(request.GET, queryset=Test.objects.all())
        page_size = request.GET.get('page_size', DEFAULT_SIZES_FILTER_PAGE[1])
        page_number = request.GET.get('page_number', 1)
        paginator = Paginator(filter.qs, page_size)
        current_page = paginator.page(page_number)
        total_pages = paginator.num_pages
        context = {"filterform":filter.form,
                    "page": current_page.object_list,
                    "prev_page": current_page.previous_page_number() if current_page.number>1 else None,
                    "next_page": current_page.next_page_number() if current_page.number< paginator.num_pages else None,
                    "total_pages": [i for i in range(1, total_pages+1)],
                    "current_page": current_page.number,
                    "list_of_sizes":DEFAULT_SIZES_FILTER_PAGE
                    }
        return render(request, self.template_name, context)
