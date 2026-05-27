from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Course, Lesson, Student, Review, Payment
from .serializers import (
    CourseSerializer, LessonSerializer,
    StudentSerializer, ReviewSerializer, PaymentSerializer
)
from .permissions import IsInstructor, IsInstructorOrReadOnly
from .filters import CourseFilter
from .pagination import CoursePagination
from .throttles import ReviewRateThrottle


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    pagination_class = CoursePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'instructor__username']
    ordering_fields = ['price', 'created_at']
    ordering = ['created_at']

    def get_queryset(self):
        return Course.objects.select_related('instructor').annotate(
            avg_rating=Avg('reviews__rating')
        )

    def get_permissions(self):
        if self.action in ['create']:
            return [IsInstructor()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsInstructorOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[IsInstructor])
    def students(self, request, pk=None):
        course = self.get_object()
        if course.instructor != request.user:
            return Response({'detail': 'Ruxsat yo\'q.'}, status=status.HTTP_403_FORBIDDEN)
        students = Student.objects.filter(courses=course)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        payment = Payment.objects.filter(
            user=request.user, course=course, status='completed'
        ).first()
        if not payment:
            return Response(
                {'detail': 'Avval kursni sotib olishingiz kerak.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        student, created = Student.objects.get_or_create(user=request.user)
        if course in student.courses.all():
            return Response({'detail': 'Siz allaqachon bu kursga yozilgansiz.'})
        student.courses.add(course)
        return Response({'detail': 'Kursga muvaffaqiyatli yozildingiz!'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def pay(self, request, pk=None):
        course = self.get_object()
        existing = Payment.objects.filter(
            user=request.user, course=course, status='completed'
        ).first()
        if existing:
            return Response({'detail': 'Siz bu kursni allaqachon sotib olgansiz.'})
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=course.price,
            status='completed'
        )
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticated])
    def reviews(self, request, pk=None):
        course = self.get_object()
        if request.method == 'GET':
            reviews = Review.objects.filter(course=course)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)

        self.throttle_classes = [ReviewRateThrottle]
        self.check_throttles(request)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Lesson.objects.none()
        return Lesson.objects.filter(course_id=self.kwargs['course_pk'])

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInstructor()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        serializer.save(course=course)


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)