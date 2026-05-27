from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import Student, Payment
from .tasks import send_enrollment_email, send_welcome_email


@receiver(m2m_changed, sender=Student.courses.through)
def student_enrolled(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for course_id in pk_set:
            from .models import Course
            course = Course.objects.get(pk=course_id)
            send_enrollment_email.delay(
                instructor_email=course.instructor.email,
                student_username=instance.user.username,
                course_title=course.title
            )


@receiver(post_save, sender=Payment)
def payment_completed(sender, instance, created, **kwargs):
    if created and instance.status == 'completed':
        send_welcome_email.delay(
            student_email=instance.user.email,
            course_title=instance.course.title
        )