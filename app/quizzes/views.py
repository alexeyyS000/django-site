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

from . import errors
from .filter import TestFilter
from .forms import AnswerQuestionForm
from .models import AttemptPipeline
from .models import AttemptState
from .models import Test
from .utils.constants import DEFAULT_ORDERING_ATTEMPTS_PAGE
from .utils.constants import DEFAULT_SIZES_ATTEMPTS_PAGE
from .utils.constants import DEFAULT_SIZES_FILTER_PAGE
from .utils.general import check_validity_request_ints
from .utils.general import chop_microseconds
from .utils.general import get_time_left


class ResultView(LoginRequiredMixin, View):
    template_name = "quizzes/results.html"

    def get(self, request: HttpRequest, quiz_id: int) -> HttpResponse:
        user = request.user
        test = Test.objects.prefetch_related("questions").get(id=quiz_id)
        questions = test.questions.order_by("order")
        try:
            current_attempt = AttemptPipeline.objects.get(
                user=request.user, test_id=quiz_id, is_attempt_completed=False
            )
        except AttemptPipeline.DoesNotExist:
            raise errors.AttemptNotFoundError
        state = []

        for question in questions:
            state.append(
                AttemptState.objects.get_or_create(
                    attempt=current_attempt, question=question, defaults={"answer": "None"}
                )[0]
            )
        current_attempt.is_attempt_completed = True
        current_attempt.time_end = datetime.datetime.utcnow()
        current_attempt.save()
        if AttemptPipeline.objects.filter(user=user, test_id=quiz_id).count() == test.attempts:
            user.done_tests.add(test)
            user.save()
        context = {"test": test, "results": state}
        return render(request, self.template_name, context)


class DetailQuestionView(LoginRequiredMixin, View):
    template_name = "quizzes/detailquestion.html"

    def get(self, request: HttpRequest, quiz_id: int, question_number: int) -> HttpResponse:
        try:
            test = Test.objects.prefetch_related("questions").get(id=quiz_id)
        except Test.DoesNotExist:
            raise errors.TestNotFoundError
        test.has_first_attempt = True
        test.save()
        if test in request.user.done_tests.all():
            return HttpResponseRedirect(reverse("quizzes:attempts", kwargs={"quiz_id": quiz_id}))
        questions = test.questions.with_quantity_right_answers().order_by("order")
        try:
            current_question = questions[question_number - 1]
        except IndexError:
            raise errors.QuestionNotFoundError
        pipline, created = AttemptPipeline.objects.get_or_create(
            user=request.user, test_id=quiz_id, is_attempt_completed=False
        )
        time_up = get_time_left(pipline.time_start, test.time_for_complete)
        if time_up <= datetime.timedelta(minutes=0, seconds=0):
            return HttpResponseRedirect(reverse("quizzes:result", kwargs={"quiz_id": quiz_id}))
        answered_questions = AttemptState.objects.select_related("question").filter(attempt=pipline)
        context = {
            "form": AnswerQuestionForm(user=request.user, question=current_question, pipline=pipline),
            "time_up": time_up.seconds,
            "default_time_up": str(chop_microseconds(time_up)).split(":", 1)[1],
            "is_current_answered": current_question in [i.question for i in answered_questions],
            "test": test,
            "all_question_list": questions,
            "is_all_done": len(questions) == len(answered_questions),
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, quiz_id: int, question_number: int) -> HttpResponse:
        test = Test.objects.prefetch_related("questions").get(id=quiz_id)
        questions = test.questions.with_quantity_right_answers().order_by("order")
        current_question = questions[question_number - 1]
        pipline, created = AttemptPipeline.objects.get_or_create(
            user=request.user, test=test, is_attempt_completed=False
        )

        time_up = get_time_left(pipline.time_start, test.time_for_complete)
        if time_up <= datetime.timedelta(minutes=0, seconds=0):
            return HttpResponseRedirect(reverse("quizzes:result", kwargs={"quiz_id": quiz_id}))
        form = AnswerQuestionForm(request.POST, user=request.user, pipline=pipline, question=current_question)
        answered_questions = AttemptState.objects.select_related("question").filter(attempt=pipline)
        if form.is_valid():
            form.save(request.user, test)

        context = {
            "form": form,
            "time_up": time_up.seconds,
            "default_time_up": str(chop_microseconds(time_up)).split(":", 1)[1],
            "test": test,
            "all_question_list": questions,
            "is_all_done": len(questions) == len(answered_questions),
            "is_current_answered": current_question in [i.question for i in answered_questions],
        }
        return render(request, self.template_name, context)


class FindView(LoginRequiredMixin, View):
    template_name = "quizzes/filter.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        page_size = request.GET.get("page_size", DEFAULT_SIZES_FILTER_PAGE[1])
        page_number = request.GET.get("page_number", 1)
        check_validity_request_ints(page_number, page_size)
        filter = TestFilter(request.GET, queryset=Test.objects.filter(is_hidden=False))
        page_size = int(page_size)
        page_number = int(page_number)
        if page_size not in DEFAULT_SIZES_FILTER_PAGE:
            raise errors.BadRequestParametrError
        paginator = Paginator(filter.qs, page_size)
        try:
            current_page = paginator.page(page_number)
        except EmptyPage:
            raise errors.PageNotFoundError
        total_pages = paginator.num_pages
        context = {
            "filterform": filter.form,
            "page": current_page.object_list,
            "total_pages": range(1, total_pages + 1),
            "current_page": current_page.number,
            "list_of_sizes": DEFAULT_SIZES_FILTER_PAGE,
        }
        return render(request, self.template_name, context)


class DetailTestView(LoginRequiredMixin, View):
    template_name = "quizzes/detailtest.html"

    def get(self, request: HttpRequest, quiz_id: int) -> HttpResponse:
        test = Test.objects.with_count_attempts_used(request.user).filter(id=quiz_id, is_hidden=False).first()
        if not test:
            raise errors.TestNotFoundError
        attempts = test.attempts
        context = {"test": test, "attempts": attempts, "attempts_used": test.attempts_used}
        return render(request, self.template_name, context)


class AttemptsView(LoginRequiredMixin, View):
    template_name = "quizzes/attempts.html"

    def get(self, request: HttpRequest, quiz_id: int) -> HttpResponse:
        page_size = request.GET.get("page_size", DEFAULT_SIZES_ATTEMPTS_PAGE[1])
        page_number = request.GET.get("page_number", 1)
        ordering = request.GET.get("ordering", DEFAULT_ORDERING_ATTEMPTS_PAGE[0])
        if ordering not in DEFAULT_ORDERING_ATTEMPTS_PAGE:
            raise errors.BadRequestParametrError
        check_validity_request_ints(page_number, page_size)
        page_size = int(page_size)
        page_number = int(page_number)
        if page_size not in DEFAULT_SIZES_ATTEMPTS_PAGE:
            raise errors.BadRequestParametrError
        attempts = (
            AttemptPipeline.objects.with_time_took()
            .prefetch_related("pipelines")
            .filter(test_id=quiz_id, user=request.user)
            .order_by(ordering)
        )
        results = []
        try:
            total_questions = attempts[0].pipelines.count()
        except IndexError:
            return render(request, self.template_name, {"none_attempts_yet": True})
        for attempt in attempts:
            state = attempt.pipelines.all()
            right_answers = state.filter(is_right=True).count()
            results.append(
                {
                    "attempt": attempt,
                    "total_questions": total_questions,
                    "right_answers": right_answers,
                    "time_took": chop_microseconds(attempt.time_took),
                }
            )
        paginator = Paginator(results, page_size)
        try:
            current_page = paginator.page(page_number)
        except EmptyPage:
            raise errors.PageNotFoundError
        total_pages = paginator.num_pages
        context = {
            "attempts": current_page,
            "test_id": quiz_id,
            "total_pages": range(1, total_pages + 1),
            "list_of_sizes": DEFAULT_SIZES_ATTEMPTS_PAGE,
            "current_page": current_page.number,
            "possible_ordering": DEFAULT_ORDERING_ATTEMPTS_PAGE,
        }
        return render(request, self.template_name, context)


class DetailAttemptView(LoginRequiredMixin, View):
    template_name = "quizzes/results.html"

    def get(self, request: HttpRequest, quiz_id: int, attempt_id: int) -> HttpResponse:
        state = AttemptState.objects.filter(attempt_id=attempt_id).order_by("question__order")
        test = Test.objects.get(id=quiz_id)
        context = {"test": test, "results": state}
        return render(request, self.template_name, context)
