from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/edit/<int:pk>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:pk>/', views.delete_student, name='delete_student'),
    path('students/create/', views.create_student, name='create_student'),
    path('courses/instructor/', views.instructor_courses, name='instructor_courses'),
    path('courses/available/', views.available_courses, name='available_courses'),
    path('courses/enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('courses/unenroll/<int:course_id>/', views.unenroll_course, name='unenroll_course'),
    path('courses/my/', views.my_courses, name='my_courses'),
    path('attendance/', views.attendance_home, name='attendance_home'),  
    path('attendance/<int:course_id>/', views.mark_attendance, name='mark_attendance'),
    path('attendance/view/', views.view_attendance, name='view_attendance'),
    path('feedback/submit/<int:course_id>/', views.submit_feedback, name='submit_feedback'),
    path('feedback/view/', views.view_feedback, name='view_feedback'),
    path('notifications/', views.notifications, name='notifications'),
    path('simulate/devops/', views.simulate_devops, name='simulate_devops'),
    path('feedback/', views.feedback_page, name='feedback_page'),
    path('assignments/', views.assignment_page, name='assignment_page'),
    path('books/', views.course_books, name='course_books'),
    path('materials/upload/', views.upload_materials, name='upload_materials'),
    path('courses/create/', views.create_course, name='create_course'),

]






