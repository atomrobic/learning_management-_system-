from django.contrib import admin
from django.urls import path, include
from e_app import views  # Ensure the correct app name here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('courses/', views.course_list, name='course_detail'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/articles/', views.course_articles, name='course_articles'),
    path('courses/<int:course_id>/enroll/',views.enroll_in_course, name='enroll_in_course'),
    path('courses/<int:course_id>/chapters/<int:chapter_id>/', views.user_chapters, name='user_chapter_detail'),
    path('courses/<int:course_id>/chapters/<int:chapter_id>/progress/', views.progress_view, name='progress_view'),

]
