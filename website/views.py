import json
import logging
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import Http404
from .models import MockTest
from pytubefix.exceptions import PytubeFixError
from .models import TestResult
from .models import Chapter, ContactUser, Course,TestResult,Question, StudyMaterial, TeamMember, Test, TestSubmitted, UserData,Announcement,Photo,PlayQuestion
from .utils import get_youtube_streams
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from .models import UserMessage
import csv
from io import StringIO
logger = logging.getLogger(__name__)


def home(request):
    announcements = Announcement.objects.all().order_by("-created_at")[:5]
    photos = Photo.objects.all().order_by("-uploaded_at")
    return render(request, "index.html", {
        "announcements": announcements,
        "photos": photos,
    })


def team(request):
    subjects = ['Physics', 'Chemistry', 'Mathematics', 'Biology']
    team_data = {subject: TeamMember.objects.filter(subject=subject) for subject in subjects}
    return render(request, 'team.html', {'team_data': team_data})

def legacy(request):
    legacy_members = TeamMember.objects.filter(is_legacy=True)
    context = {
        'coordinators': legacy_members.filter(role='Coordinator').order_by('subject'),
        'maths_tutors': legacy_members.filter(subject='Maths', role='Tutor').order_by('name'),
        'physics_tutors': legacy_members.filter(subject='Physics', role='Tutor').order_by('name'),
        'chemistry_tutors': legacy_members.filter(subject='Chemistry', role='Tutor').order_by('name'),
        'biology_tutors': legacy_members.filter(subject='Biology', role='Tutor').order_by('name'),
    }
    return render(request, 'legacy.html', context)

def entrance(request):
    return render(request, 'entrance.html')


def contactus(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        ContactUser.objects.create(name=name, email=email, message=message)
        messages.success(request, 'Your message has been sent successfully.')
        return redirect('contact')
    return render(request, 'contacts.html')

def about(request):
    return render(request, 'about.html')

def login_route(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')
@login_required
def update_profile(request):
    if request.method == 'POST':
        try:
            user = request.user
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            
            if not first_name or not last_name:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'message': 'Both first name and last name are required.'
                    })
                else:
                    messages.error(request, 'Both first name and last name are required.')
                    return render(request, 'dashboard.html')
            
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
           
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Profile updated successfully!',
                    'first_name': user.first_name,
                    'last_name': user.last_name
                })
            else:
                messages.success(request, 'Profile updated successfully!')
                return redirect('dashboard')
                
        except Exception as e:
           
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'message': f'Error updating profile: {str(e)}'
                })
            else:
                messages.error(request, 'Error updating profile. Please try again.')
                return render(request, 'dashboard.html')
    
    return render(request, 'dashboard.html')
@login_required
def saving_result(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'POST request required.'}, status=400)

    try:
        data = json.loads(request.body or '{}')

        required = ['test_name', 'mode', 'score', 'total_possible_score', 
                    'correct_answers', 'wrong_answers', 'unanswered']
        missing = [f for f in required if f not in data]
        if missing:
            return JsonResponse({'success': False, 'message': f'Missing fields: {", ".join(missing)}'}, status=400)

        user = User.objects.first()

        result = TestResult.objects.create(
            user=user,
            test_name=data['test_name'],
            mode=data['mode'],
            score=int(data['score']),
            total_possible_score=int(data['total_possible_score']),
            correct_answers=int(data['correct_answers']),
            wrong_answers=int(data['wrong_answers']),
            unanswered=int(data['unanswered']),
            time_taken=int(data.get('time_taken') or 0)
        )

        return JsonResponse({
            'success': True,
            'result_id': result.id,
            'message': 'Saved successfully!'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
@login_required
@csrf_exempt
def save_message(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'POST required'}, status=400)

    try:
        data = json.loads(request.body or '{}')
        test_name = data.get("test_name")
        mode = data.get("mode")

       
        if mode == "mock":
           
            existing = UserMessage.objects.filter(user=request.user, result_csv__icontains=f"test_name={test_name}").exists()
            if existing:
                return JsonResponse({'success': False, 'message': f"You have already attended the mock test '{test_name}'."}, status=400)

        result_csv = ",".join(f"{k}={v}" for k, v in data.items())

        obj = UserMessage.objects.create(
            user=request.user,
            result_csv=result_csv
        )

        return JsonResponse({'success': True, 'id': obj.id})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def get_messages(request):
    results = []
    for msg in UserMessage.objects.filter(user=request.user).order_by('-id'):
     
        parts = msg.result_csv.split(",")
        result_dict = dict(p.split("=", 1) for p in parts if "=" in p)
        result_dict["taken_at"] = msg.created_at.isoformat() 
        results.append(result_dict)

    return JsonResponse({"success": True, "results": results})
@login_required
def league_data(request):
    """
    Retrieves mock test results for ALL users to populate the league/leaderboard.
    It filters results where mode=mock and extracts essential score data.
    """
    league_results = []
    
    # Fetch all user messages (no user filter) ordered by newest first
    for msg in UserMessage.objects.all().order_by('-id'):
        
        # Parse the CSV data string into a dictionary
        result_dict = {}
        parts = msg.result_csv.split(",")
        for p in parts:
            if "=" in p:
                key, value = p.split("=", 1)
                result_dict[key.strip()] = value.strip()

        # Check if the message is a Mock Test submission
        if result_dict.get("mode") == "mock":
            
            # Add user and timestamp data
            result_dict["taken_at"] = msg.created_at.isoformat()
            
            # Add user identification
            username = msg.user.first_name or msg.user.username or f"User-{msg.user.id}"
            result_dict["username"] = username
            
            # Ensure required score fields exist (for safety)
            score = result_dict.get("score")
            total_score = result_dict.get("total_possible_score")

            if score and total_score:
                try:
                    score = int(score)
                    total_score = int(total_score)
                    
                    # Calculate percentage for sorting/display
                    percentage = (score / total_score) * 100 if total_score > 0 else 0
                    result_dict["score_percentage"] = round(percentage, 1)

                    league_results.append(result_dict)
                except ValueError:
                    # Skip if score data is not convertible to integer
                    continue

    return JsonResponse({"success": True, "results": league_results})

@login_required
def get_test_results(request):
    """
    Get user's test results with pagination
    """
    try:
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 10)), 50) 
        
        results = TestResult.objects.filter(user=request.user).order_by('-taken_at')
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_results = results[start_idx:end_idx]
        
        results_data = []
        for result in paginated_results:
            results_data.append({
                'id': result.id,
                'test_name': result.test_name,
                'mode': result.get_mode_display() if hasattr(result, 'get_mode_display') else result.mode,
                'score': result.score,
                'total_possible_score': result.total_possible_score,
                'correct_answers': result.correct_answers,
                'wrong_answers': result.wrong_answers,
                'unanswered': result.unanswered,
                'percentage': result.get_percentage(),
                'accuracy': result.get_accuracy(),
                'time_taken': result.time_taken,
                'taken_at': result.taken_at.strftime('%d %b %Y, %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'results': results_data,
            'has_more': len(results) > end_idx,
            'total_count': len(results)
        })
        
    except Exception as e:
        logger.error(f'Error fetching test results for user {request.user.id}: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': 'Error fetching results.'
        }, status=500)
@transaction.atomic
def signup_route(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        phno = request.POST.get('phno')
        batch = request.POST.get('batch')
        name = request.POST.get('name')
        course_name = request.POST.get('course')

        if User.objects.filter(username=username).exists():
            messages.error(request, "A user with that email already exists.")
        else:
            try:
                course_obj = Course.objects.get(name=course_name, batch=batch)
                user = User.objects.create_user(username=username, password=password, email=username)
                UserData.objects.create(
                    user=user,
                    name=name,
                    phone_number=phno,
                    batch=batch,
                    course=course_obj
                )
                login(request, user)
                return redirect('dashboard')
            except Course.DoesNotExist:
                messages.error(request, f"We do not currently have the course '{course_name}' for batch '{batch}'.")

    batch_names = list(Course.objects.values_list('batch', flat=True).distinct().order_by('batch'))
    course_names = list(Course.objects.values_list('name', flat=True).distinct().order_by('name'))
    context = {"batch_names": batch_names, "course_names": course_names}
    return render(request, 'signup.html', context=context)

@login_required
def logout_route(request):
    logout(request)
    return redirect('home')
from django.db.models import Avg, Max
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Avg, Max

@login_required
def dashboard(request):
    # --- Study materials ---
    study_materials = StudyMaterial.objects.all()
    announcements = Announcement.objects.all().order_by("-created_at")[:5]
    # --- Questions ---
    questions_qs = PlayQuestion.objects.all().order_by('id')
    questions = [{
        'id': q.id,
        'concept_name': q.concept_name,
        'question_text': q.question_text,
        'question_type': q.question_type,
        'correct_integer': q.correct_integer,
        'correct_choice': q.correct_choice,
        'choices_list': q.get_choices_list(),
        'image': q.image.url if q.image else None,
    } for q in questions_qs]

    # --- Mock tests ---
    mocktests = list(MockTest.objects.all().order_by("open_datetime"))

    # --- User test history ---
    test_history = TestResult.objects.filter(user=request.user).order_by("-taken_at")
    from django.db.models import Avg, Max
    avg_score = test_history.aggregate(Avg('score'))['score__avg'] or 0
    best_score = test_history.aggregate(Max('score'))['score__max'] or 0

    # --- Process UserMessages for leaderboard ---
    user_messages = UserMessage.objects.select_related('user').all()
    mock_results = {}
    for msg in user_messages:
        result_dict = {}
        for p in msg.result_csv.split(","):
            if "=" in p:
                key, value = p.split("=", 1)
                result_dict[key.strip()] = value.strip()

        if result_dict.get("mode") == "mock":
            test_name = result_dict.get("test_name")
            if not test_name:
                continue

            try:
                score = int(result_dict.get("score", 0))
                total = int(result_dict.get("total_possible_score", 0))
                percentage = round((score / total) * 100, 1) if total > 0 else 0
            except ValueError:
                score = total = percentage = 0

            username = msg.user.first_name or msg.user.username or f"User-{msg.user.id}"

            entry = {
                "username": username,
                "score": score,
                "total_score": total,
                "percentage": percentage,
                "correct": int(result_dict.get("correct_answers", 0)),
                "wrong": int(result_dict.get("wrong_answers", 0)),
                "unanswered": int(result_dict.get("unanswered", 0)),
                "time_taken": int(result_dict.get("time_taken", 0)),
            }

            mock_results.setdefault(test_name, []).append(entry)

    # Sort results
    for results in mock_results.values():
        results.sort(key=lambda x: x["percentage"], reverse=True)

    # --- Attach results directly to mock objects ---
    for mock in mocktests:
        mock.results = mock_results.get(mock.name, [])
    
    # --- Context ---
    context = {
        'study_materials': study_materials,
        'questions': questions,
        'mocktests': mocktests,  
        'test_history': test_history,
        'avg_score': avg_score,
        'best_score': best_score,
        "announcements": announcements,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def mock_test_view(request, pk):
    mocktest = get_object_or_404(MockTest, pk=pk)

    from django.utils import timezone
    
  
    mock_open = mocktest.open_datetime
    if timezone.is_naive(mock_open):
        mock_open = timezone.make_aware(mock_open, timezone.get_current_timezone())

 
    if mock_open > timezone.now():
        return JsonResponse({
            "status": "not_available",
            "message": f"This mock test will be available at {mock_open.strftime('%d %b %Y, %H:%M')}",
            "current_server_time": timezone.now().strftime('%d %b %Y, %H:%M:%S')
        })

    questions = []
   
    for q in list(mocktest.custom_questions.all()) + list(mocktest.play_questions.all()):
        questions.append({
            "id": q.id,
            "concept_name": q.concept_name,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "correct_integer": q.correct_integer,
            "correct_choice": q.correct_choice,
            "choices_list": q.get_choices_list(),
            "image": q.image.url if q.image else None,
        })

    
    duration_minutes = getattr(mocktest, 'duration_minutes', 180)

    duration_seconds = duration_minutes * 60

    return JsonResponse({
        "status": "ok",
        "mock_name": mocktest.name,
        "questions": questions,
        "duration": duration_seconds 
    })

@csrf_exempt  
@login_required
def submit_test(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)
        test = TestHistory.objects.create(
            user=request.user,
            test_name=data.get("test_mode", "Unknown"),
            score=data.get("score", 0),
            correct=data.get("correct", 0),
            wrong=data.get("wrong", 0),
            total=len(data.get("answers", [])),
            answers=data.get("answers", []),
            duration=data.get("duration", 0)
        )
        return JsonResponse({"status": "ok", "id": test.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def test_history_view(request):
    history = TestHistory.objects.filter(user=request.user).order_by("-date")
    
    return JsonResponse({
        "history": [
            {
                "test_name": h.test_name,
                "date": h.date.strftime("%d %b %Y, %H:%M"),
                "score": h.score,
                "correct": h.correct,
                "wrong": h.wrong,
                "total": h.total,
                "duration": h.duration,
            } for h in history
        ]
    })

@login_required
def profile(request):
    user_profile = get_object_or_404(UserData, user=request.user)

    submitted_test_ids = set(TestSubmitted.objects.filter(user_profile=user_profile).values_list('test__test_id', flat=True))
    all_tests = Test.objects.filter(Q(owner=user_profile) | Q(owner__isnull=True))

    testlist = []
    submittedtest = []
    for test in all_tests:
        attempted = test.test_id in submitted_test_ids
        test_data = {
            'test_id': test.test_id,
            'test_name': test.test_name,
            'available': test.accepting_response,
            'result_released': test.result_released,
            'attempted': attempted,
        }
        testlist.append(test_data)
        if attempted:
            submittedtest.append(test_data)

    context = {
        'username': user_profile.name,
        "testlist": testlist,
        "submittedtest": submittedtest
    }
    return render(request, 'profile.html', context=context)

@login_required(login_url='/login/')
def study_page_route(request):
    user_profile = get_object_or_404(UserData, user=request.user)

    courses_qs = Course.objects.prefetch_related('subjects__chapters__study_materials')

    if user_profile.course:
        courses = courses_qs.filter(batch=user_profile.batch, name=user_profile.course.name)
    else:
        courses = courses_qs.filter(batch=user_profile.batch)

    entire_dict = {}
    subject_list = []  

    for course in courses:
        course_dict = {}
        for subject in course.subjects.all():
            subject_dict = {}
            if subject.subject_name not in subject_list:
                subject_list.append(subject.subject_name) 
            for chapter in subject.chapters.all():
                chapter_materials = []
                for material in chapter.study_materials.all():
                    m = {
                        'desc': material.description,
                        'type': 'pdf' if material.type_of_material == "PDF" else 'video',
                        'url': material.file.url if material.type_of_material == "PDF" else material.pk,
                    }
                    chapter_materials.append(m)
                subject_dict[chapter.chapter_name] = {"materials": chapter_materials, "key": chapter.pk}
            course_dict[subject.subject_name] = subject_dict
        entire_dict[course.name] = course_dict

    return render(request, 'study.html', context={
        "entire_dict": entire_dict,
        "subject_list": subject_list, 
    })

@login_required
def yt_render(request, video_id):
    material = get_object_or_404(StudyMaterial, id=video_id, type_of_material="YT")

    try:
        video_data = get_youtube_streams(material.youtube_link)
        if not video_data:
            messages.error(request, "No video streams could be found for this link.")
            return redirect('study')

    except PytubeFixError as e:
        logger.error("Failed to get YouTube streams for material ID %s: %s", video_id, e)
        messages.error(request, "Sorry, there was a problem loading this video.")
        return redirect('study')

    context = {
        'video_data': video_data,
        'video_title': material.description
    }
    return render(request, 'video.html', context)


@login_required
def create_test(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    user_profile = get_object_or_404(UserData, user=request.user)
    questions = Question.objects.filter(chapter=chapter, visible=True)

    duration_seconds = max(1, questions.count()) * 5 * 60
    duration = timedelta(seconds=duration_seconds)

    test = Test.objects.create(
        owner=user_profile,
        test_name=f"Practice Test for {chapter.chapter_name}",
        duration=duration,
        result_released=True,
        accepting_response=True
    )
    test.question_list.set(questions)

    return redirect(reverse('route_test', kwargs={'test_id': test.test_id}))


@login_required
def route_test(request, test_id):
    test = get_object_or_404(Test, test_id=test_id)
    user_profile = get_object_or_404(UserData, user=request.user)

    if not test.accepting_response:
        messages.error(request, "This test is no longer accepting responses.")
        return redirect('profile')

    if TestSubmitted.objects.filter(user_profile=user_profile, test=test).exists():
        messages.info(request, "You have already submitted this test.")
        return redirect('profile')

    questions_dict = {}
    for q in test.question_list.all():
        question_data = {
            'question': q.question_text,
            'question_id': q.pk,
            'type': q.question_type,
            'question_file': q.question_file.url if q.question_file else None,
        }
        if question_data['type'] != 'numerical':
            question_data.update({
                'a': q.option_a, 'b': q.option_b, 'c': q.option_c, 'd': q.option_d,
                'a_file': q.option_a_file.url if q.option_a_file else None,
                'b_file': q.option_b_file.url if q.option_b_file else None,
                'c_file': q.option_c_file.url if q.option_c_file else None,
                'd_file': q.option_d_file.url if q.option_d_file else None,
            })
        questions_dict[q.pk] = question_data

    context = {'test': {"questions": questions_dict, "time": int(test.duration.total_seconds()), "test_id": test.test_id}}
    return render(request, 'test.html', context=context)


@login_required
def submit_test(request, test_id):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid method'}, status=405)

    test = get_object_or_404(Test, test_id=test_id)
    user_profile = get_object_or_404(UserData, user=request.user)

    if not test.accepting_response:
        return JsonResponse({'error': 'Test not accepting responses'}, status=403)

    if TestSubmitted.objects.filter(user_profile=user_profile, test=test).exists():
        return JsonResponse({'message': 'Test submitted already'}, status=200)

    try:
        data = json.loads(request.body.decode('utf-8'))
        TestSubmitted.objects.create(
            user_profile=user_profile,
            test=test,
            json_response=data
        )
        return JsonResponse({'message': 'Test submitted successfully'}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.exception("Error saving test submission for user %s test %s: %s", user_profile, test, e)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
def analyse(request, test_id):
    test = get_object_or_404(Test, test_id=test_id)
    user_profile = get_object_or_404(UserData, user=request.user)

    submission = get_object_or_404(TestSubmitted, user_profile=user_profile, test=test)

    if not test.result_released:
        messages.info(request, "Results for this test have not been released yet.")
        return redirect('profile')

    if submission.analysis and submission.score is not None:
        context = {"qna": submission.analysis, "total": submission.score, "test_name": test.test_name}
        return render(request, 'analyse.html', context=context)

    answer_dict = {}
    for q in test.question_list.all():
        temp = {
            'marks_awarded': q.marks_award,
            'marks_deducted': q.marks_deduct,
            'question': q.question_text,
            'explanation_text': q.explanation,
            'question_file': q.question_file.url if q.question_file else None,
            'explanation_file': q.explanation_file.url if q.explanation_file else None,
            'type': q.question_type,
        }
        if temp['type'] == 'numerical':
            temp['min_ans'] = q.correct_answer_numerical_min
            temp['max_ans'] = q.correct_answer_numerical_max
        else:
            temp['answer'] = q.correct_option.lower() if q.correct_option else ''
        answer_dict[q.pk] = temp

    qna_dict, total = check_answers(submission.json_response or {}, answer_dict)
    qna_list = [{"id": key, **value} for key, value in qna_dict.items()]

    submission.analysis = qna_list
    submission.score = total
    submission.save()

    context = {"qna": qna_list, "total": total, "test_name": test.test_name}
    return render(request, 'analyse.html', context=context)


def check_answers(user_entry, actual_answers):
    total_score = 0
    final_dict = {}

    for q_id, correct_ans_data in actual_answers.items():
        q_id_str = str(q_id)
        result = {}
        user_answer = user_entry.get(q_id_str) if isinstance(user_entry, dict) else None

        result['question'] = correct_ans_data.get("question")
        result['explanation_text'] = correct_ans_data.get("explanation_text")
        result['question_file'] = correct_ans_data.get("question_file")
        result['explanation_file'] = correct_ans_data.get("explanation_file")

        if user_answer is not None and user_answer != '':
            result['your_answer'] = user_answer
            is_correct = False

            if correct_ans_data.get('type') == 'numerical':
                result['correct_ans'] = f"Range: {correct_ans_data.get('min_ans')} to {correct_ans_data.get('max_ans')}"
                try:
                    user_ans_float = float(user_answer)
                    if correct_ans_data.get('min_ans') <= user_ans_float <= correct_ans_data.get('max_ans'):
                        is_correct = True
                except (ValueError, TypeError):
                    is_correct = False
            else:
                result['correct_ans'] = correct_ans_data.get('answer', '').upper()
                if str(user_answer).lower() == correct_ans_data.get('answer', '').lower():
                    is_correct = True

            if is_correct:
                result['status'] = "Correct"
                result['marks'] = correct_ans_data.get('marks_awarded', 0)
            else:
                result['status'] = "Incorrect"
                result['marks'] = -correct_ans_data.get('marks_deducted', 0)
        else:
            result['status'] = "Unattempted"
            result['marks'] = 0
            if correct_ans_data.get('type') == 'numerical':
                result['correct_ans'] = f"Range: {correct_ans_data.get('min_ans')} to {correct_ans_data.get('max_ans')}"
            else:
                result['correct_ans'] = correct_ans_data.get('answer', '').upper()

        total_score += result['marks']
        final_dict[q_id] = result

    return final_dict, total_score

from django.shortcuts import render

def register(request):
    return render(request, 'register.html')
@csrf_exempt
def save_test_result(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)

        mode = data.get("mode")
        correct = data.get("correct_answers", 0)
        wrong = data.get("wrong_answers", 0)
        score = data.get("score", 0)
        mock_id = data.get("mocktest_id")

        mocktest = None
        if mode == "mock" and mock_id:
            mocktest = MockTest.objects.filter(id=mock_id).first()

        TestResult.objects.create(
            user=request.user,
            mode=mode,
            mocktest=mocktest,
            correct_answers=correct,
            wrong_answers=wrong,
            score=score,
        )
        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)