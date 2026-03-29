# website/models.py
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.timezone import now
import pytz

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Helper function to generate unique paths for all file uploads
def unique_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    class_name = instance.__class__.__name__.lower()
    return f'{class_name}/{new_filename}'


class Photo(models.Model):
    title = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Photo {self.id}"


class Course(models.Model):
    COURSE_CHOICES = [
        ('JEE', 'JEE'),
        ('NEET', 'NEET'),
        ('JEE+NEET', 'JEE+NEET'),
    ]
    name = models.CharField(max_length=20, choices=COURSE_CHOICES)
    batch = models.CharField(max_length=50)
    course_id = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if not self.course_id:
            self.course_id = f"{self.name}-{self.batch}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.course_id


class Announcement(models.Model):
    text = models.TextField()
    pdf = models.FileField(upload_to="announcements/pdfs/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_new(self):
        return self.created_at >= timezone.now() - timedelta(days=3)

    def __str__(self):
        return self.text[:50] + ("..." if len(self.text) > 50 else "")


class TeamMember(models.Model):
    SUBJECT_CHOICES = [
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Mathematics', 'Mathematics'),
        ('Biology', 'Biology'),
    ]
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.subject})"


class UserData(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('administrator', 'Administrator'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userdata')
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    school_name = models.CharField(max_length=255, blank=True, null=True)
    parent_email = models.EmailField(blank=True, null=True)
    parent_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    roll_no = models.CharField(max_length=50, blank=True, null=True)
    batch = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, related_name='students', blank=True, null=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    subject_name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return f"{self.subject_name} ({self.course.name} - {self.course.batch})"


class Chapter(models.Model):
    chapter_name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')

    def __str__(self):
        return f"{self.chapter_name} ({self.subject.subject_name})"


class StudyMaterial(models.Model):
    concept_name = models.CharField(max_length=255, default="Untitled Concept")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.concept_name


class PlayQuestion(models.Model):
    QUESTION_TYPES = [
        ('NUM', 'Numerical'),
        ('MCQ', 'Multiple Choice'),
    ]
    concept_name = models.CharField(max_length=255)
    question_text = models.TextField()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)
    correct_integer = models.IntegerField(blank=True, null=True)
    correct_choice = models.CharField(max_length=255, blank=True, null=True)
    choices = models.TextField(blank=True, null=True, help_text="Comma-separated choices for MCQ")
    image = models.ImageField(upload_to='play_question_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_choices_list(self):
        if self.choices:
            return [c.strip() for c in self.choices.split(',')]
        return []

    def __str__(self):
        return f"{self.concept_name} - {self.question_text[:30]}"


class StudyMaterialFile(models.Model):
    MATERIAL_TYPES = [
        ('PDF', 'PDF'),
        ('VIDEO', 'Video'),
        ('OTHER', 'Other'),
    ]
    study_material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='study_materials/')
    file_type = models.CharField(max_length=10, choices=MATERIAL_TYPES, default='PDF')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.study_material.concept_name} - {self.file.name.split('/')[-1]}"


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('numerical', 'Numerical'),
        ('option', 'Option'),
    ]
    TAG_CHOICES = [
        ('AI generated', 'AI generated'),
        ('PYQ', 'PYQ'),
        ('Expected Question', 'Expected Question'),
    ]
    question_text = models.TextField()
    option_a = models.CharField(max_length=255, null=True, blank=True)
    option_b = models.CharField(max_length=255, null=True, blank=True)
    option_c = models.CharField(max_length=255, null=True, blank=True)
    option_d = models.CharField(max_length=255, null=True, blank=True)
    correct_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')], null=True, blank=True)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    correct_answer_numerical_min = models.FloatField(null=True, blank=True)
    correct_answer_numerical_max = models.FloatField(null=True, blank=True)
    question_file = models.FileField(upload_to=unique_upload_path, null=True, blank=True)
    option_a_file = models.FileField(upload_to=unique_upload_path, null=True, blank=True)
    option_b_file = models.FileField(upload_to=unique_upload_path, null=True, blank=True)
    option_c_file = models.FileField(upload_to=unique_upload_path, null=True, blank=True)
    option_d_file = models.FileField(upload_to=unique_upload_path, null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)
    explanation_file = models.FileField(upload_to=unique_upload_path, null=True, blank=True)
    marks_award = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    marks_deduct = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    chapter = models.ManyToManyField(Chapter, related_name='questions')
    tag = models.CharField(max_length=50, choices=TAG_CHOICES)
    visible = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text[:80]

    def clean(self):
        if self.question_type == 'numerical':
            if self.correct_answer_numerical_min is None or self.correct_answer_numerical_max is None:
                raise ValidationError("Numerical questions must have min and max answers.")
            if self.correct_answer_numerical_min > self.correct_answer_numerical_max:
                raise ValidationError("Min answer can't be greater than max answer.")
        elif self.question_type == 'option':
            if not self.correct_option:
                raise ValidationError("Option questions must have a correct_option.")


class Test(models.Model):
    test_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test_name = models.CharField(max_length=100, null=True, blank=True)
    duration = models.DurationField()
    question_list = models.ManyToManyField(Question, related_name='tests')
    owner = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name="owned_tests", blank=True, null=True)
    result_released = models.BooleanField(default=False)
    accepting_response = models.BooleanField(default=True)

    def __str__(self):
        return self.test_name or str(self.test_id)


class TestSubmitted(models.Model):
    user_profile = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='test_submissions')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='submissions')
    json_response = models.JSONField(blank=True, null=True)
    analysis = models.JSONField(blank=True, null=True)
    score = models.FloatField(default=0.0, blank=True, null=True)

    class Meta:
        unique_together = ('user_profile', 'test')

    def __str__(self):
        return f"Submission for {self.test.test_name} by {self.user_profile.name}"


class ContactUser(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class MockTest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    open_datetime = models.DateTimeField()
    play_questions = models.ManyToManyField(PlayQuestion, blank=True, related_name="mock_tests")
    created_at = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.IntegerField(
        default=180,  # Default to 3 hours (180 minutes)
        help_text="Duration of the mock test in minutes (e.g., 180 for 3 hours)"
    )
    def is_available(self):
        india = pytz.timezone("Asia/Kolkata")
        return timezone.now().astimezone(india) >= self.open_datetime.astimezone(india)

    def __str__(self):
        return f"MockTest: {self.name}"


class MockTestQuestion(models.Model):
    QUESTION_TYPES = [
        ('NUM', 'Numerical'),
        ('MCQ', 'Multiple Choice'),
    ]
    mocktest = models.ForeignKey(MockTest, on_delete=models.CASCADE, related_name="custom_questions")
    concept_name = models.CharField(max_length=255)
    question_text = models.TextField()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)
    correct_integer = models.IntegerField(blank=True, null=True)
    correct_choice = models.CharField(max_length=255, blank=True, null=True)
    choices = models.TextField(blank=True, null=True, help_text="Comma-separated choices for MCQ")
    image = models.ImageField(upload_to='mock_question_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_choices_list(self):
        return [c.strip() for c in self.choices.split(',')] if self.choices else []

    def __str__(self):
        return f"{self.mocktest.name} | {self.concept_name} - {self.question_text[:30]}"



    


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=255)
    course = models.CharField(max_length=50, choices=[("JEE", "JEE"), ("NEET", "NEET")])

    def __str__(self):
        return f"{self.name} ({self.course})"


class TestResult(models.Model):
    TEST_MODES = [
        ('bullet', 'Bullet'),
        ('blitz', 'Blitz'),
        ('survival', 'Survival'),
        ('subwise', 'Subwise'),
        ('mock', 'Mock Test'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,default=1 )
    test_name = models.CharField(max_length=200)
    mode = models.CharField(max_length=20, choices=TEST_MODES)
    score = models.IntegerField()
    total_possible_score = models.IntegerField()
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    unanswered = models.IntegerField(default=0)
    time_taken = models.IntegerField(null=True, blank=True)
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.test_name} ({self.mode}) - {self.score}"
class UserMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    result_csv = models.TextField(help_text="Stores payload as CSV")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.created_at}"
