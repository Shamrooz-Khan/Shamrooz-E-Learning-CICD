from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Course
from .models import Attendance
from datetime import date
from .models import Feedback
from .models import Notification  

def home(request):
    return render(request, 'core/home.html')

@login_required
def student_dashboard(request):
    return render(request, 'core/student_dashboard.html')

@login_required
def instructor_dashboard(request):
    return render(request, 'core/instructor_dashboard.html')
    

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'instructor':
                return redirect('instructor_dashboard')
            else:
                return redirect('home')  # fallback
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'core/login.html')
    return render(request, 'core/login.html')

# List all students
@login_required
def student_list(request):
    if request.user.role != 'instructor':
        return redirect('home')
    
    query = request.GET.get('q', '')
    students = CustomUser.objects.filter(role='student')
    if query:
        students = students.filter(username__icontains=query) | students.filter(email__icontains=query)

    return render(request, 'core/student_list.html', {'students': students, 'query': query})

@login_required
def create_student(request):
    if request.user.role != 'instructor':
        return redirect('home')
    form = CustomUserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.role = 'student'  # force role to student
        user.set_password(form.cleaned_data['password1'])
        user.save()
        return redirect('student_list')
    return render(request, 'core/create_student.html', {'form': form})

# Edit student
@login_required
def edit_student(request, pk):
    if request.user.role != 'instructor':
        return redirect('home')
    student = get_object_or_404(CustomUser, pk=pk, role='student')
    form = CustomUserCreationForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        return redirect('student_list')
    return render(request, 'core/edit_student.html', {'form': form, 'student': student})

# Delete student
@login_required
def delete_student(request, pk):
    if request.user.role != 'instructor':
        return redirect('home')
    student = get_object_or_404(CustomUser, pk=pk, role='student')
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'core/delete_student.html', {'student': student})

# Instructor View: All Courses
@login_required
def instructor_courses(request):
    if request.user.role != 'instructor':
        return redirect('home')
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'core/instructor_courses.html', {'courses': courses})

# Student View: Available Courses
@login_required
def available_courses(request):
    if request.user.role != 'student':
        return redirect('home')
    enrolled = request.user.enrolled_courses.all()
    available = Course.objects.exclude(id__in=enrolled.values_list('id', flat=True))
    return render(request, 'core/available_courses.html', {'courses': available})

# Enroll in course
@login_required
def enroll_course(request, course_id):
    if request.user.role != 'student':
        return redirect('home')
    course = get_object_or_404(Course, id=course_id)
    course.students.add(request.user)
    # After course.students.add(request.user)
    Notification.objects.create(
    user=course.instructor,
    message=f"{request.user.username} enrolled in {course.title}"
)
    return redirect('my_courses')

# View my enrolled courses
@login_required
def my_courses(request):
    if request.user.role != 'student':
        return redirect('home')
    courses = request.user.enrolled_courses.all()
    return render(request, 'core/my_courses.html', {'courses': courses})

@login_required
def unenroll_course(request, course_id):
    if request.user.role != 'student':
        return redirect('home')
    course = get_object_or_404(Course, id=course_id)
    course.students.remove(request.user)
    return redirect('my_courses')


# Instructor: Mark Attendance
@login_required
def mark_attendance(request, course_id):
    if request.user.role != 'instructor':
        return redirect('home')

    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    students = course.students.all()

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}', 'Absent')
            
            Attendance.objects.update_or_create(
                student=student,
                course=course,
                date=date.today(),
                defaults={'status': status}
            )

            Notification.objects.create(
                user=student,
                message=f"Attendance marked for {course.title} on {date.today()}"
            )

        return redirect('instructor_courses')

    return render(request, 'core/mark_attendance.html', {
        'course': course,
        'students': students,
        'today': date.today()
    })

# Student: View Attendance
from django.utils.dateparse import parse_date
from django.db.models import Count

@login_required
def view_attendance(request):
    if request.user.role != 'student':
        return redirect('home')

    # Get filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    records = Attendance.objects.filter(student=request.user).order_by('-date')

    # Apply date filters
    if start_date:
        records = records.filter(date__gte=parse_date(start_date))
    if end_date:
        records = records.filter(date__lte=parse_date(end_date))

    # Attendance percentage
    total = records.count()
    present_count = records.filter(status='Present').count()
    percentage = round((present_count / total) * 100, 1) if total > 0 else 0

    context = {
        'records': records,
        'start_date': start_date,
        'end_date': end_date,
        'percentage': percentage,
        'present_count': present_count,
        'total': total
    }
    return render(request, 'core/view_attendance.html', context)

@login_required
def attendance_home(request):
    if request.user.role != 'instructor':
        return redirect('home')

    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'core/attendance_home.html', {'courses': courses})

# Student: Submit feedback
@login_required
def submit_feedback(request, course_id):
    if request.user.role != 'student':
        return redirect('home')
    
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        
        Feedback.objects.update_or_create(
            student=request.user,
            course=course,
            defaults={'content': content}
        )

        Notification.objects.create(
            user=course.instructor,
            message=f"{request.user.username} submitted feedback on {course.title}"
        )

        return redirect('my_courses')
    
    return render(request, 'core/submit_feedback.html', {'course': course})


# Instructor: View all feedback on their courses
@login_required
def view_feedback(request):
    if request.user.role != 'instructor':
        return redirect('home')
    
    feedbacks = Feedback.objects.filter(course__instructor=request.user).order_by('-date')
    return render(request, 'core/view_feedback.html', {'feedbacks': feedbacks})

@login_required
def notifications(request):
    all_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/notifications.html', {'notifications': all_notifications})

@login_required
def simulate_devops(request):
    devoops_errors = {
    "bad_yaml": {
        "title": "Invalid GitHub Actions YAML",
        "error": "Unrecognized key 'runs-on'",
        "fix": "Make sure 'runs-on' is under correct indentation under 'jobs:'."
    },
    "missing_req": {
        "title": "Missing requirements.txt",
        "error": "ModuleNotFoundError: No module named 'django'",
        "fix": "Add 'django' to your requirements.txt and commit the file."
    },
    "test_fail": {
        "title": "Failing Unit Tests",
        "error": "AssertionError: Expected status code 200, got 500",
        "fix": "Check your view logic and ensure templates exist."
    },
    "docker_error": {
        "title": "Dockerfile Build Error",
        "error": "COPY failed: file not found in context",
        "fix": "Ensure file paths in Dockerfile match the actual project structure."
    },
    # New DevOps simulation examples:
    "broken_pipeline": {
        "title": "CI Pipeline Misconfigured",
        "error": "Job failed due to unknown command",
        "fix": "Verify all CI job steps and correct syntax errors."
    },
    "missing_dockerfile": {
        "title": "Dockerfile Missing",
        "error": "Cannot build container without Dockerfile",
        "fix": "Ensure Dockerfile is in project root and named correctly."
    },
    "port_conflict": {
        "title": "Port Conflict",
        "error": "Port 8000 already in use",
        "fix": "Stop the other process using the port or change port number."
    }
    }

    selected = request.GET.get('error')
    detail = devoops_errors.get(selected)

    return render(request, 'core/simulate_devops.html', {
        'errors': devoops_errors,
        'detail': detail,
        'selected': selected
    })

@login_required
def feedback_page(request):
    courses = request.user.enrolled_courses.all()
    if request.method == 'POST':
        course_id = request.POST.get('course')
        message = request.POST.get('message')  # still okay to use 'message' here as variable
        if course_id and message:
            course = Course.objects.get(id=course_id)
            Feedback.objects.create(
                student=request.user,
                course=course,
                content=message  # <- correct field name
            )
            messages.success(request, "Feedback submitted.")
            return redirect('feedback_page')
    return render(request, 'core/feedback.html', {'courses': courses})


@login_required
def assignment_page(request):
    courses = request.user.enrolled_courses.all()
    if request.method == 'POST' and request.FILES.get('file'):
        course_id = request.POST.get('course')
        file = request.FILES['file']
        Assignment.objects.create(student=request.user, course_id=course_id, file=file)
        messages.success(request, "Assignment uploaded.")
        return redirect('assignment_page')
    return render(request, 'core/assignment_page.html', {'courses': courses})

@login_required
def upload_materials(request):
    if request.user.role != 'instructor':
        return redirect('home')
    return render(request, 'core/upload_materials.html')


@login_required
def course_books(request):
    return render(request, 'core/course_books.html')

from .forms import CourseForm  # you'll create this next

@login_required
def create_course(request):
    if request.user.role != 'instructor':
        return redirect('home')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('instructor_courses')
    else:
        form = CourseForm()
    
    return render(request, 'core/create_course.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


