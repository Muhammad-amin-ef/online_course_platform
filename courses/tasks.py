from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_enrollment_email(instructor_email, student_username, course_title):
    send_mail(
        subject=f'Yangi o\'quvchi: {course_title}',
        message=f'{student_username} sizning "{course_title}" kursingizga yozildi!',
        from_email='noreply@onlinecourse.com',
        recipient_list=[instructor_email],
    )


@shared_task
def send_welcome_email(student_email, course_title):
    send_mail(
        subject='Kursga xush kelibsiz!',
        message=f'Siz "{course_title}" kursini muvaffaqiyatli sotib oldingiz! Xush kelibsiz!',
        from_email='noreply@onlinecourse.com',
        recipient_list=[student_email],
    )