import django_filters
from .models import Course


class CourseFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    instructor = django_filters.CharFilter(
        field_name='instructor__username',
        lookup_expr='icontains'
    )

    class Meta:
        model = Course
        fields = ['min_price', 'max_price', 'instructor']