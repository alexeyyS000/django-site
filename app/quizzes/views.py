from itertools import chain
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.views import View
from django.views import generic
from users.models import User
from django.db.models import Prefetch
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import AnswerQuestionForm, FilterForm, PaginationForm
from .models import Choice
from .models import Question
from .models import Test, Tag
from .models import TestPipeline
from .models import TestState
from .utils.utils import chop_microseconds
from .utils.utils import is_time_up
from .utils.utils import time_to_timedelta
from .service import TestFilter


class ListTestView(generic.ListView):
    template_name = "tests/tests.html"
    context_object_name = "latest_tests_list"

    def get_queryset(self):
        """Return the last five published questions."""

        return Test.objects.order_by("created")[:20]


class ResultView(View):
    template_name = "tests/results.html"

    def get(self, request: HttpRequest, test_number) -> HttpResponse:
        user = User.objects.get(id=request.user.id)
        results = TestState.objects.filter(user=user, test=int(test_number))
        user.done_tests.add(Test.objects.get(id=int(test_number)))
        user.save()
        pipeline = TestPipeline.objects.get(user=request.user, test=int(test_number))
        print(pipeline)
        context = {"test_number": test_number, "results": results}
        return render(request, self.template_name, context)


class DetailQuestionView(View):
    template_name = "tests/detailtest.html"

    def get(self, request: HttpRequest, test_number, question_number) -> HttpResponse:
        test = Test.objects.get(id=test_number)
        questions = Question.objects.filter(test=test).order_by("question_text")
        current_question = questions[int(question_number) - 1]
        pipline = TestPipeline.objects.get_or_create(user=request.user, test=test)
        try:
            time_up = is_time_up(pipline[0].time_start, test.time_to_timedelta())
        except TimeoutError:
            return HttpResponseRedirect(reverse("tests:result", kwargs={"test_number": test_number}))
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

    def post(self, request: HttpRequest, test_number, question_number) -> HttpResponse:
        test = Test.objects.get(id=test_number)
        questions = Question.objects.filter(test=test).order_by("question_text")
        current_question = questions[int(question_number) - 1]
        pipline = TestPipeline.objects.get_or_create(user=request.user, test=test)
        try:
            time_up = is_time_up(pipline[0].time_start, test.time_to_timedelta())
        except TimeoutError:
            return HttpResponseRedirect(reverse("tests:result", kwargs={"test_number": test_number}))
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
        else:
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
    template_name = "tests/filter.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        filter = TestFilter(request.GET, queryset=Test.objects.all())
        form = PaginationForm()
        if request.GET: 
            page_size = request.GET['page_size'] 
            page_number = request.GET['page_number']
        else:
            page_size = 1000
            page_number = 1
        paginator = Paginator(filter.qs, page_size)#проблема в том что ражется на страницы queryset, не знаю как это возможно сделать на уровне запроса 

        current_page = paginator.page(page_number) 
        
        context = {"filterform":filter.form,
                    "paginationform":form,
                    "page": current_page.object_list,
                    "prev_page": current_page.previous_page_number() if current_page.number>1 else None,
                    "next_page": current_page.next_page_number() if current_page.number< paginator.num_pages else None,
                    }
        return render(request, self.template_name, context)
    
    # def post(self, request: HttpRequest) -> HttpResponse:

    #     filter = TestFilter(request.POST, queryset=Test.objects.all())
    #     form = PaginationForm(request.POST)
    #     if form.is_valid():
    #         page_size = form.cleaned_data.get("page_size")
    #         page_number = form.cleaned_data.get("page_number")


    #     paginator = Paginator(filter.qs, page_size)

    #     current_page = paginator.page(page_number) 
        
    #     context = {"filter":filter,
    #                 "form":form,
    #                 "page": current_page.object_list,
    #                 "prev_page": current_page.previous_page_number() if current_page.number>1 else None,
    #                 "next_page": current_page.next_page_number() if current_page.number< paginator.num_pages else None,
    #                 }
    #     return render(request, self.template_name, context)

class FilterView(View):
    template_name = "tests/filter2.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {"form": FilterForm}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest):
        form = FilterForm(request.POST)
        if form.is_valid():
            order_value = form.cleaned_data.get("order_field")
            find_value = form.cleaned_data.get("find_field")
            page_size = form.cleaned_data.get("page_size")
            page_number = form.cleaned_data.get("page_number")

        find_result = Test.objects.filter(Q(name__contains=find_value) | Q(tag__name__contains=find_value))
        if order_value:
            find_result = find_result.order_by(order_value)

        paginator = Paginator(find_result, page_size)
        current_page = paginator.page(page_number)
        context = {
            "form": form,
            "page": current_page.object_list,
            "prev_page": current_page.previous_page_number() if current_page.number>1 else None,
            "next_page": current_page.next_page_number() if current_page.number< paginator.num_pages else None,
        }
        print(paginator.num_pages)
        return render(request, self.template_name, context)


# class DetailTestPollView(View):
#     template_name = "tests/detail.html"

#     def get(self, request: HttpRequest, test_number, poll_number) -> HttpResponse:
#         all_polls_list = Question.objects.filter(test_id=test_number)
#         test_state = TestState.objects.filter(user=request.user, test = test_number)
#         this_poll = all_polls_list.get(id = poll_number)

#         if test_state.filter(question=this_poll).exists():
#             is_answered_question = True
#         else:
#             is_answered_question = False

#         if len(test_state) == len(all_polls_list):
#             return HttpResponseRedirect(reverse("tests:result", kwargs={"test_number": test_number}))
#         context = {
#             "question": this_poll,
#             "all_polls_list": all_polls_list,
#             "test_number": test_number,
#             "is_answered_question": is_answered_question,
#             "time_for_complete": Test.objects.get(id = int(test_number)).time_in_seconds()
#         }
#         return render(request, self.template_name, context)


# def vote(request, test_number, poll_number):
#     question = get_object_or_404(Question, pk=poll_number)
#     test = Test.objects.get(id = test_number)
#     choices = Choice.objects.filter(question=question.id)
#     right_answers = Choice.objects.filter(question=question.id, right_answer=True)
#     answers_list = []
#     for choice in choices:
#         try:
#             answers_list.append(request.POST[str(choice.id)])
#         except MultiValueDictKeyError:
#             continue


#     if len(right_answers) != len(answers_list):
#         TestState.objects.create(user=request.user,test = test,  question=question, answer=False)
#     else:
#         for i in range(len(right_answers)):
#             if right_answers[i].choice_text != answers_list[i]:
#                 TestState.objects.create(user=request.user,test = test,  question=question, answer=False)
#                 return HttpResponseRedirect(reverse("tests:firstquestion", kwargs={"test_number": test_number, "poll_number": poll_number}))
#         TestState.objects.create(user=request.user, test = test, question=question, answer=True)


#     return HttpResponseRedirect(
#         reverse("tests:firstquestion", kwargs={"test_number": test_number, "poll_number": poll_number})
#     )
