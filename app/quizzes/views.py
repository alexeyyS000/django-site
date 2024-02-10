from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views import generic

from .forms import AnswerQuestionForm
from .models import Question
from .models import Test
from .models import TestPipeline
from .models import TestState
from .service import TestFilter
from .utils.constants import DEFAULT_SIZES_FILTER_PAGE
from .utils.general import chop_microseconds
from .utils.general import is_time_up


class ListTestView(LoginRequiredMixin, generic.ListView):
    template_name = "quizzes/tests.html"
    context_object_name = "latest_tests_list"

    def get_queryset(self):
        """Return the last five published questions."""

        return Test.objects.order_by("-created")[:20]


class ResultView(LoginRequiredMixin, View):
    template_name = "quizzes/results.html"

    def get(self, request: HttpRequest, quiz_id: str) -> HttpResponse:
        user = request.user
        test = Test.objects.get(id=quiz_id)
        questions = Question.objects.filter(test_id=quiz_id).order_by("id")
        for question in questions:
            TestState.objects.get_or_create(user=user, test_id=quiz_id, question=question, defaults={"answer": False})
        state = TestState.objects.filter(user=user, test=quiz_id).order_by("question_id")
        user.done_tests.add(Test.objects.get(id=quiz_id))
        user.save()
        try:
            TestPipeline.objects.get(user=user, test_id=quiz_id).delete()
        except ObjectDoesNotExist:
            pass
        # results = [i for i in questions]
        context = {"test": test, "results": state}
        return render(request, self.template_name, context)


class DetailQuestionView(
    LoginRequiredMixin, View
):  # тут очень много дублирования кода, стоит ли делить на куски и выносить в отдельную функцию ?
    template_name = "quizzes/detailquestion.html"

    def get(self, request: HttpRequest, quiz_id: str, question_number: str) -> HttpResponse:
        test = Test.objects.get(id=quiz_id)
        if test in request.user.done_tests.all():
            return HttpResponseRedirect(reverse("quizzes:result", kwargs={"quiz_id": quiz_id}))
        questions = Question.objects.filter(test_id=quiz_id).order_by("text")
        current_question = questions[int(question_number) - 1]
        pipline = TestPipeline.objects.get_or_create(user=request.user, test_id=quiz_id)
        try:
            time_up = is_time_up(pipline[0].time_start, test.time_for_complete)
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

    def post(self, request: HttpRequest, quiz_id: str, question_number: str) -> HttpResponse:
        test = Test.objects.get(id=quiz_id)
        questions = Question.objects.filter(test=test).order_by("text")
        current_question = questions[int(question_number) - 1]
        pipline = TestPipeline.objects.get_or_create(user=request.user, test=test)
        try:
            time_up = is_time_up(pipline[0].time_start, test.time_for_complete)
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
        try:
            page_size = int(request.GET.get("page_size", DEFAULT_SIZES_FILTER_PAGE[1]))
            page_number = int(request.GET.get("page_number", 1))
        except ValueError:
            raise BadRequest
        if page_size not in DEFAULT_SIZES_FILTER_PAGE:
            raise BadRequest
        paginator = Paginator(filter.qs, page_size)
        try:
            current_page = paginator.page(page_number)
        except EmptyPage:
            raise Http404
        total_pages = paginator.num_pages
        context = {
            "filterform": filter.form,
            "page": current_page.object_list,
            "prev_page": current_page.previous_page_number() if current_page.number > 1 else None,
            "next_page": current_page.next_page_number() if current_page.number < paginator.num_pages else None,
            "total_pages": [i for i in range(1, total_pages + 1)],
            "current_page": current_page.number,
            "list_of_sizes": DEFAULT_SIZES_FILTER_PAGE,
        }
        return render(request, self.template_name, context)


class DetailTestView(
    LoginRequiredMixin, View
):
    template_name = "quizzes/detailtest.html"

    def get(self, request: HttpRequest, quiz_id: str) -> HttpResponse:
        test = Test.objects.get(id=quiz_id)
        context = {"test": test}
        return render(request, self.template_name, context)
