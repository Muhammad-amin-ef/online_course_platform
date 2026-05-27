from rest_framework import serializers
from .models import Course, Lesson, Student, Review, Payment


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'created_at']
        read_only_fields = ['created_at']


class CourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.username', read_only=True)
    lessons_count = serializers.IntegerField(source='lessons.count', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'price', 'instructor', 'instructor_name', 'lessons_count', 'created_at']
        read_only_fields = ['instructor', 'created_at']


class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'username', 'joined_at']
        read_only_fields = ['joined_at']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'course', 'amount', 'status', 'payment_date']
        read_only_fields = ['payment_date', 'user']