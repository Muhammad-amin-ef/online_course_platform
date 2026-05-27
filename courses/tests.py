import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from users.models import User
from courses.models import Course, Payment, Student, Review


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def instructor(db):
    return User.objects.create_user(
        username='instructor',
        email='instructor@test.com',
        password='test1234',
        is_instructor=True
    )


@pytest.fixture
def student(db):
    return User.objects.create_user(
        username='student',
        email='student@test.com',
        password='test1234',
        is_instructor=False
    )


@pytest.fixture
def instructor_client(client, instructor):
    client.force_authenticate(user=instructor)
    return client


@pytest.fixture
def student_client(client, student):
    client.force_authenticate(user=student)
    return client


@pytest.fixture
def course(db, instructor):
    return Course.objects.create(
        title='Test kurs',
        description='Test tavsif',
        price=50.00,
        instructor=instructor
    )


@pytest.mark.django_db
def test_create_course_as_instructor(instructor_client):
    url = reverse('course-list')
    data = {
        'title': 'Yangi kurs',
        'description': 'Tavsif',
        'price': '30.00'
    }
    response = instructor_client.post(url, data)
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_course_as_student(student_client):
    url = reverse('course-list')
    data = {
        'title': 'Yangi kurs',
        'description': 'Tavsif',
        'price': '30.00'
    }
    response = student_client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_get_courses(student_client):
    url = reverse('course-list')
    response = student_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_pay_course(student_client, student, course):
    url = reverse('course-pay', kwargs={'pk': course.pk})
    response = student_client.post(url)
    assert response.status_code == 201
    assert Payment.objects.filter(user=student, course=course).exists()


@pytest.mark.django_db
def test_enroll_after_payment(student_client, student, course):
    Payment.objects.create(
        user=student,
        course=course,
        amount=course.price,
        status='completed'
    )
    url = reverse('course-enroll', kwargs={'pk': course.pk})
    response = student_client.post(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_enroll_without_payment(student_client, course):
    url = reverse('course-enroll', kwargs={'pk': course.pk})
    response = student_client.post(url)
    assert response.status_code == 400


@pytest.mark.django_db
def test_add_review(student_client, student, course):
    url = reverse('course-reviews', kwargs={'pk': course.pk})
    data = {'rating': 5, 'comment': 'Zo\'r kurs!'}
    response = student_client.post(url, data)
    assert response.status_code == 201