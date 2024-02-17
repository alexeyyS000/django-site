import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views import generic

from . import errors
from .filter import TestFilter
from .forms import AnswerQuestionForm
from .models import AttemptPipeline
from .models import AttemptState
from .models import Question
from .models import Test
from .utils.constants import DEFAULT_SIZES_FILTER_PAGE
from .utils.general import check_validity_request_ints
from .utils.general import chop_microseconds
from .utils.general import is_time_up
from .utils.models import get_one_or_none


class ListTestView(LoginRequiredMixin, generic.ListView):
    template_name = "quizzes/tests.html"
    context_object_name = "latest_tests_list"

    def get_queryset(self):
        """Return the last five published questions."""

        return Test.objects.filter(is_hidden=False).order_by("-created")[:20]


class ResultView(LoginRequiredMixin, View):
    template_name = "quizzes/results.html"

    def get(self, request: HttpRequest, quiz_id: str) -> HttpResponse:
        user = request.user
        test = Test.objects.get(id=quiz_id)
        questions = Question.objects.filter(test_id=quiz_id).order_by("order")
        current_attempt = AttemptPipeline.objects.get(user=request.user, test_id=quiz_id, is_attempt_completed=False)
        for question in questions:
            AttemptState.objects.get_or_create(attempt=current_attempt, question=question, defaults={"answer": False})
        current_attempt.is_attempt_completed = True
        current_attempt.time_end = datetime.datetime.now()
        current_attempt.save()
        state = AttemptState.objects.filter(attempt=current_attempt).order_by("question__order")
        if AttemptPipeline.objects.filter(user=user, test_id=quiz_id).count() == test.attempts:
            user.done_tests.add(Test.objects.get(id=quiz_id))
            user.save()
        context = {"test": test, "results": state}
        return render(request, self.template_name, context)


class DetailQuestionView(LoginRequiredMixin, View):
    template_name = "quizzes/detailquestion.html"

    def get(self, request: HttpRequest, quiz_id: str, question_number: str) -> HttpResponse:
        test = Test.objects.get(id=quiz_id)
        if test in request.user.done_tests.all():
            return HttpResponseRedirect(reverse("quizzes:attempts", kwargs={"quiz_id": quiz_id}))

        questions = Question.objects.filter(test_id=quiz_id).order_by("order")
        current_question = questions[int(question_number) - 1]
        pipline = AttemptPipeline.objects.get_or_create(user=request.user, test_id=quiz_id, is_attempt_completed=False)
        try:
            time_up = is_time_up(pipline[0].time_start, test.time_for_complete)
        except TimeoutError:
            return HttpResponseRedirect(reverse("quizzes:result", kwargs={"quiz_id": quiz_id}))
        answered_questions = AttemptState.objects.filter(attempt=pipline[0])
        context = {
            "form": AnswerQuestionForm(question=current_question),
            "time_up": chop_microseconds(time_up).total_seconds(),
            "answered_questions": [i.question_id for i in answered_questions],
            "test": test,
            "all_question_list": questions,
            "next_question": int(question_number) + 1 if int(question_number) + 1 <= len(questions) else None,
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, quiz_id: str, question_number: str) -> HttpResponse:
        test = Test.objects.get(id=quiz_id)
        questions = Question.objects.filter(test=test).order_by("order")
        current_question = questions[int(question_number) - 1]
        pipline = AttemptPipeline.objects.get_or_create(user=request.user, test=test, is_attempt_completed=False)
        try:
            time_up = is_time_up(pipline[0].time_start, test.time_for_complete)
        except TimeoutError:
            return HttpResponseRedirect(reverse("quizzes:result", kwargs={"quiz_id": quiz_id}))

        form = AnswerQuestionForm(request.POST, question=current_question)
        answered_questions = AttemptState.objects.filter(attempt=pipline[0])
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
        filter = TestFilter(request.GET, queryset=Test.objects.filter(is_hidden=False))
        page_size = request.GET.get("page_size", DEFAULT_SIZES_FILTER_PAGE[1])
        page_number = request.GET.get("page_number", 1)
        check_validity_request_ints(page_number, page_size)
        page_size = int(page_size)
        page_number = int(page_number)
        if page_size not in DEFAULT_SIZES_FILTER_PAGE:
            raise errors.BadFindParametrError
        paginator = Paginator(filter.qs, page_size)
        try:
            current_page = paginator.page(page_number)
        except EmptyPage:
            raise errors.PageNotFoundError
        total_pages = paginator.num_pages
        context = {
            "filterform": filter.form,
            "page": current_page.object_list,
            "total_pages": [i for i in range(1, total_pages + 1)],
            "current_page": current_page.number,
            "list_of_sizes": DEFAULT_SIZES_FILTER_PAGE,
        }
        return render(request, self.template_name, context)


class DetailTestView(LoginRequiredMixin, View):
    template_name = "quizzes/detailtest.html"

    def get(self, request: HttpRequest, quiz_id: str) -> HttpResponse:
        check_validity_request_ints(quiz_id)
        test = get_one_or_none(Test, id=quiz_id, is_hidden=False)
        if not test:
            raise errors.TestNotFoundError
        attempts = test.attempts
        attempts_used = AttemptPipeline.objects.filter(user=request.user, test_id=quiz_id).count()
        context = {"test": test, "attempts": attempts, "attempts_used": attempts_used}
        return render(request, self.template_name, context)


class AttemptsView(LoginRequiredMixin, View):
    template_name = "quizzes/attempts.html"

    def get(self, request: HttpRequest, quiz_id: str) -> HttpResponse:
        check_validity_request_ints(quiz_id)
        attempts = AttemptPipeline.objects.filter(test_id=quiz_id, user=request.user).order_by("-time_start")
        results = []
        for attempt in attempts:
            state = AttemptState.objects.filter(attempt=attempt)
            total_questions = len(state)
            right_answers = len([i for i in state if i.answer])
            time_took = chop_microseconds(attempt.time_end - attempt.time_start)
            results.append(
                {
                    "attempt": attempt,
                    "total_questions": total_questions,
                    "right_answers": right_answers,
                    "time_took": time_took,
                }
            )
        context = {"attempts": results, "test_id": quiz_id}
        return render(request, self.template_name, context)


class DetailAttemptView(LoginRequiredMixin, View):
    template_name = "quizzes/results.html"

    def get(self, request: HttpRequest, quiz_id: str, attempt_id: str) -> HttpResponse:
        check_validity_request_ints(quiz_id, attempt_id)
        state = AttemptState.objects.filter(attempt_id=attempt_id).order_by("question__order")
        test = Test.objects.get(id=quiz_id)
        context = {"test": test, "results": state}
        return render(request, self.template_name, context)
