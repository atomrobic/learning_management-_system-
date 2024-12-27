from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect  # Use csrf_protect instead of csrf_exempt
from django.utils import timezone
import json
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Article, Progress, Chapter, Enrollment
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token


# Sign Up View
# @csrf_exempt
# def signup_view(request):
#     if request.method == 'POST':
#         try:
#             # Parse the incoming JSON request body
#             data = json.loads(request.body)
#             email = data.get('email')
#             password1 = data.get('password1')
#             password2 = data.get('password2')
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON data provided.'}, status=400)

#         # Validate input
#         if not email or not password1 or not password2:
#             return JsonResponse({'error': 'All fields (email, password1, password2) are required'}, status=400)
#         if password1 != password2:
#             return JsonResponse({'error': 'Passwords do not match'}, status=400)
#         if User.objects.filter(username=email).exists():
#             return JsonResponse({'error': 'Email already registered!'}, status=400)

#         # Create user
#         user = User.objects.create_user(username=email, email=email, password=password1)
#         user.save()
#         return JsonResponse({'success': 'Account created successfully!'}, status=201)

#     return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        try:
            # Check content type and parse data accordingly
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:  # For form-data or x-www-form-urlencoded
                data = request.POST

            email = data.get('email')
            password1 = data.get('password1')
            password2 = data.get('password2')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data provided.'}, status=400)

        # Validate input
        if not email or not password1 or not password2:
            return JsonResponse({'error': 'All fields (email, password1, password2) are required'}, status=400)
        if password1 != password2:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)
        if User.objects.filter(username=email).exists():
            return JsonResponse({'error': 'Email already registered!'}, status=400)

        # Create user
        user = User.objects.create_user(username=email, email=email, password=password1)
        user.save()
        return JsonResponse({'success': 'Account created successfully!'}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required  # Ensure user is logged in
@csrf_protect  # Apply CSRF protection
def enroll_in_course(request, course_id):
    if request.method == 'POST':
        try:
            user = request.user  # Get the logged-in user
            course = get_object_or_404(Course, pk=course_id)  # Get course object
            
            # Check if the user is already enrolled
            if Enrollment.objects.filter(user=user, course=course).exists():
                return JsonResponse({'error': 'You are already enrolled in this course.'}, status=400)
            
            # Enroll the user in the course
            enrollment = Enrollment.objects.create(user=user, course=course)
            
            # Create progress entries for each chapter in the course
            for chapter in course.chapters.all():
                Progress.objects.create(user=user, chapter=chapter, completed=False)
            
            return JsonResponse({
                'success': f'You have successfully enrolled in "{course.title}".',
                'enrollment_id': enrollment.id
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_protect  # Ensure CSRF protection is applied to login
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Ensure proper parsing of JSON
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)
            
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)  # Log the user in
                return JsonResponse({'success': 'Logged in successfully!'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data provided.'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# Course List View

@csrf_exempt
def course_list(request):
    courses = Course.objects.values('id', 'title')
    return JsonResponse({'courses': list(courses)}, safe=False)


# Course Detail View
@csrf_exempt
def course_detail(request, course_id):
    # Get the course by ID or return a 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Fetch chapters related to the course
    chapters = Chapter.objects.filter(course=course).order_by('order')

    # Prepare chapter data, including progress for the logged-in user
    chapter_data = []
    for chapter in chapters:
        # Correctly filter progress by Chapter instance, not by course title
        progress = Progress.objects.filter(user=request.user, chapter=chapter).first() if request.user.is_authenticated else None
        chapter_data.append({
            'id': chapter.id,
            'title': chapter.title,
            'description': chapter.description,
            'order': chapter.order,
            'completed': progress.completed if progress else False,
        })

    # Prepare course data to return as a JSON response
    course_data = {
        'id': course.id,
        'title': course.title,
        'description': course.description,
    }

    return JsonResponse(course_data)

@csrf_exempt
def course_articles(request, course_id):
    # Get the course by ID or return a 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Fetch the articles for the course, sorted by order
    articles = Article.objects.filter(course=course).order_by('order')

    # Prepare the article data to send as JSON response
    article_data = []
    for article in articles:
        article_data.append({
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'order': article.order,
        })

    # Return the article data as JSON
    return JsonResponse({'course': {
        'id': course.id,
        'title': course.title,
        'articles': article_data,
    }})


# Enroll in Course View
# @csrf_protect  # Ensures CSRF protection is applied to this view
# @csrf_exempt
# @login_required
# def enroll_in_course(request, course_id):
#     try:
#         # Log the request method and body to debug
#         print(f"Request Method: {request.method}")
#         if request.method == 'POST':
#             print(f"Request Body: {request.body}")

#         # Ensure the user is authenticated (optional if using @login_required)
#         if not request.user.is_authenticated:
#             return JsonResponse({'error': 'You must be logged in to enroll in a course.'}, status=401)

#         # Get the logged-in user and the specified course
#         user = request.user
#         course = get_object_or_404(Course, pk=course_id)

#         # Check if the user is already enrolled in the course
#         if Enrollment.objects.filter(user=user, course=course).exists():
#             return JsonResponse({'error': 'You are already enrolled in this course.'}, status=400)

#         # Create a new enrollment
#         enrollment = Enrollment.objects.create(user=user, course=course)

#         # Create progress entries for each chapter in the course
#         for chapter in course.chapters.all():
#             Progress.objects.create(user=user, chapter=chapter, completed=False)

#         # Respond with success message
#         return JsonResponse({
#             'success': f'You have been successfully enrolled in "{course.title}"!',
#             'enrollment_id': enrollment.id
#         }, status=201)

#     except Exception as e:
#         # Handle unexpected errors
#         return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

@csrf_exempt
@login_required
def user_chapters(request, course_id, chapter_id):
    print(f"Request Method: {request.method}")
    print(f"Course ID: {course_id}, Chapter ID: {chapter_id}")

    user = request.user
    print(user)

    # Check if the user is enrolled in the course
    if not Enrollment.objects.filter(user=user, course_id=course_id).exists():
        
        return JsonResponse({'error': 'You are not enrolled in this course.'}, status=403)

    # Retrieve the specific chapter
    try:
        chapter = get_object_or_404(Chapter, course_id=course_id, order=chapter_id)
    except Chapter.DoesNotExist:
        return JsonResponse({'error': 'Chapter not found.'}, status=404)

    # Retrieve or create a progress record for this user and chapter
    progress, created = Progress.objects.get_or_create(user=user, chapter=chapter)

    if request.method == "POST":
        completed = request.POST.get("completed", "false") == "true"
        progress.completed = completed
        progress.completed_at = timezone.now() if completed else None
        progress.save()

    # Prepare chapter data with progress and course title
    chapter_data = {
        'id': chapter.id,
        'title': chapter.title,
        'description': chapter.description,
        'course_title': chapter.course.title,
        'completed': progress.completed if progress else False,
        'completed_at': progress.completed_at if progress and progress.completed else None,
    }

    return JsonResponse({'chapter': chapter_data}, status=200)

# @csrf_exempt
# @login_required
# def user_chapters(request, course_id, chapter_id):
#     print(f"Request Method: {request.method}")
#     print(f"Course ID: {course_id}, Chapter ID: {chapter_id}")

#     user = request.user
#     print(f"User: {user}")

#     # Check if the user is enrolled in the course
#     if not Enrollment.objects.filter(user=user, course_id=course_id).exists():
#         return JsonResponse({'error': 'You are not enrolled in this course.'}, status=403)

#     # Retrieve the specific chapter
#     try:
#         chapter = Chapter.objects.get(course_id=course_id, order=chapter_id)
#     except Chapter.DoesNotExist:
#         return JsonResponse({'error': 'Chapter not found.'}, status=404)

#     # Retrieve or create a progress record for this user and chapter
#     progress, created = Progress.objects.get_or_create(user=user, chapter=chapter)

#     if request.method == "POST":
#         completed = request.POST.get("completed", "false") == "true"
#         progress.completed = completed
#         progress.completed_at = timezone.now() if completed else None
#         progress.save()

#     # Prepare chapter data with progress and course title
#     chapter_data = {
#         'id': chapter.id,
#         'title': chapter.title,
#         'description': chapter.description,
#         'course_title': chapter.course.title,
#         'completed': progress.completed if progress else False,
#         'completed_at': progress.completed_at if progress and progress.completed else None,
#     }

#     return JsonResponse({'chapter': chapter_data}, status=200)

# Mark Chapter Complete View
@csrf_exempt

@login_required
def progress_view(request, course_id, chapter_id):
    # Retrieve the chapter
    chapter = get_object_or_404(Chapter, id=chapter_id)

    # Check if the user is enrolled in the course associated with the chapter
    course = chapter.course
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()

    if not enrollment:
        return JsonResponse({'error': 'You are not enrolled in this course.'}, status=403)

    # Retrieve or create the user's progress on the chapter
    progress = Progress.objects.filter(user=request.user, chapter=chapter).first()

    # Construct the response with enrollment ID and course category included
    progress_data = {
        'enrollment_id': enrollment.id,  # Add enrollment ID to the response
        'chapter_id': chapter.id,
        'chapter_title': chapter.title,
        'completed': progress.completed,
        'completed_at': progress.completed_at if progress.completed else None,
        'course_category': course.category,  # Use course.category directly if it's a string
    }

    return JsonResponse({'progress': progress_data}, status=200)

def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

