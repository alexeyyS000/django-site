import django_filters
from django.contrib.postgres.search import SearchVector
from .models import Test, Tag
from collections import OrderedDict
from django import forms
from django.core.paginator import Paginator


class TestFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr="contains")

    tag = django_filters.CharFilter(method="filter_search", label='find by tags(values separated by space)')
    
    #или можно сделать пагинацию так, не знаю что лучше

    # page_num = django_filters.NumberFilter(label='page_num', method='pagination')
    

    # def pagination(self, queryset, name, value):
    #     LIMIT = 5
    #     paginator = Paginator(self.qs, LIMIT)
    #     current_page = paginator.page(value) 
    #     return current_page
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(tag__name__in=value.split(' '))

    ordering = django_filters.OrderingFilter(
        fields=(("name", "test name"),("created", "created")),
    )



    class Meta:
        model = Test
        fields = ["name"]

    # @property
    # def qs(self):
    #     queryset=super(TestFilter, self).qs
    #     if request.user.has_perm("app_label.has_permission"):       
    #         return queryset.exclude(invited_user!=self.request.user)
    #     return queryset   
# django_filters.FilterSet.form