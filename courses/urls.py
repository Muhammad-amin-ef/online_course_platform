from django.urls import path, include
from rest_framework_nested import routers
from .views import CourseViewSet, LessonViewSet, PaymentListView

router = routers.DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

courses_router = routers.NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'lessons', LessonViewSet, basename='course-lessons')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
]