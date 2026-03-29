from django.contrib import admin
from .models import (
    Announcement, TeamMember, Photo,
    StudyMaterial, StudyMaterialFile,
    PlayQuestion, MockTest, MockTestQuestion,
    TestResult, Profile,UserMessage
)
from django.contrib.auth.models import User

# ---- PlayQuestion Admin ----
@admin.register(PlayQuestion)
class PlayQuestionAdmin(admin.ModelAdmin):
    list_display = ('concept_name', 'question_text', 'question_type', 'created_at')
    list_filter = ('question_type', 'concept_name')
    search_fields = ('concept_name', 'question_text')

# ---- Photo Admin ----
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_at")
    search_fields = ("title",)

# ---- TeamMember Admin ----
@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'role')
    list_filter = ('subject',)
    search_fields = ('name', 'role')

# ---- Announcement Admin ----
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'created_at') 
    search_fields = ('text',)

    def text_preview(self, obj):
        return obj.text[:50] + ("..." if len(obj.text) > 50 else "")
    text_preview.short_description = "Announcement"

# ---- StudyMaterial Admin ----
class StudyMaterialFileInline(admin.TabularInline):
    model = StudyMaterialFile
    extra = 1

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('concept_name', 'description', 'created_at')
    inlines = [StudyMaterialFileInline]

# ---- MockTest Admin ----
class MockTestQuestionInline(admin.StackedInline):
    model = MockTestQuestion
    extra = 1
    fields = (
        "concept_name",
        "question_text",
        "question_type",
        "choices",
        "correct_choice",
        "correct_integer",
        "image",
    )

@admin.register(MockTest)
class MockTestAdmin(admin.ModelAdmin):
    list_display = ("name", "open_datetime", "duration_minutes","created_at")
    search_fields = ("name",)
    filter_horizontal = ("play_questions",)  
    fields = (
        "name",
        "description",
        "open_datetime",
        "duration_minutes",  
        "play_questions",
    )
    inlines = [MockTestQuestionInline]
#testresult
@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test_name', 'mode', 'score', 'total_possible_score', 
                    'correct_answers', 'wrong_answers', 'unanswered', 'time_taken', 'taken_at')
    list_filter = ('mode', 'taken_at')
    search_fields = ('user__username', 'test_name')
# ---- Profile Admin ----
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'course')
    search_fields = ('user__email', 'name')
    list_filter = ('course',)
@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'result_csv', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'result_csv')
# ---- Admin Site Titles ----
admin.site.site_header = 'LEAP Admin'
admin.site.index_title = 'Welcome to the LEAP Administration Panel'
admin.site.site_title = 'LEAP Admin Portal'
