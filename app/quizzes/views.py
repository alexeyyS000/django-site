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
from .forms import AnswerQuestionForm,PaginationForm
from .models import Question
from .models import Test
from .models import TestPipeline
from .models import TestState
from .utils.utils import chop_microseconds
from .utils.utils import is_time_up
from .service import TestFilter


class ListTestView(generic.ListView):
    template_name = "quizzes/tests.html"
    context_object_name = "latest_tests_list"

    def get_queryset(self):
        """Return the last five published questions."""

        return Test.objects.order_by("-created")[:20]


class ResultView(View):
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


class DetailQuestionView(View):# тут очень много дублирования кода, стоит ли делить на куски и выносить в отдельную функцию ?
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


class FindView(View):
    template_name = "quizzes/filter.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        filter = TestFilter(request.GET, queryset=Test.objects.all())
        form = PaginationForm()
        if request.GET: 
            page_size = request.GET['page_size'] 
            page_number = request.GET['page_number']
        else:
            page_size = 10000
            page_number = 1
        paginator = Paginator(filter.qs, page_size)#проблема в том что бьется на страницы уже имеющийся queryset, не знаю как это возможно сделать на уровне запроса 

        current_page = paginator.page(page_number) 
        
        context = {"filterform":filter.form,
                    "paginationform":form,
                    "page": current_page.object_list,
                    "prev_page": current_page.previous_page_number() if current_page.number>1 else None,
                    "next_page": current_page.next_page_number() if current_page.number< paginator.num_pages else None,
                    }
        return render(request, self.template_name, context)
