
from django.contrib import admin
from .models import Course
from .models import Article
from .models import Progress,Chapter,Enrollment

class CourseAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('id','title', 'category', 'created_at', 'updated_at')

    # Fields to search in the admin list view
    search_fields = ('title', 'category')

    # Fields to filter by in the admin list view
    list_filter = ('category',)

    # Default ordering for the list view
    ordering = ('-created_at',)

    # Number of items to display per page in the admin list view
    list_per_page = 25

    # Define fieldsets to organize the form fields in the admin panel
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Category & Dates', {
            'fields': ('category', 'updated_at'),  # Don't include 'created_at'
            'classes': ('collapse',),  # Collapsible section for better UI
        }),
    )

    # Make 'updated_at' field read-only
    readonly_fields = ('updated_at',)  # Only make 'updated_at' read-only

    # Exclude 'created_at' from the form entirely
    exclude = ('created_at',)  # This ensures 'created_at' is not in the form

admin.site.register(Course, CourseAdmin)


class ArticleAdmin(admin.ModelAdmin):
    # Display these fields in the list view
    list_display = ('title', 'course', 'order')

    # Add search functionality for title and course title
    search_fields = ('title', 'course__title')  # Search articles by title and course title
    
    # Add filter functionality for filtering by course
    list_filter = ('course',)  # Filter articles by course
    
    # Specify the organization of fields in form view
    fieldsets = (
        ('Article Information', {
            'fields': ('course', 'title', 'content')
        }),
        ('Ordering', {
            'fields': ('order',),
            'classes': ('collapse',),  # Optionally collapse this section for better UI
        }),
    )

    # You can also make some fields read-only (like 'order' if you don't want it editable)
    readonly_fields = ('order',)

admin.site.register(Article, ArticleAdmin)


class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter', 'get_course_title', 'get_course_category', 'completed', 'completed_at')  # Added 'get_course_title'
    list_filter = ('completed', 'completed_at', 'chapter__course__category')  # Added filter for course category
    search_fields = ('user__username', 'chapter__title', 'chapter__course__title', 'chapter__course__category')  # Added search for course title and category
    ordering = ('completed', 'completed_at')

    # Customize the form layout
    fieldsets = (
        (None, {
            'fields': ('user', 'chapter')
        }),
        ('Progress Information', {
            'fields': ('completed', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    # Define a custom method to display course category
    def get_course_category(self, obj):
        return obj.chapter.course.category  # Access the course category through chapter and course

    get_course_category.short_description = 'Course Category'  # Label for the column

    # Define a custom method to display course title
    def get_course_title(self, obj):
        return obj.chapter.course.title  # Access the course title through chapter and course

    get_course_title.short_description = 'Course Title'  # Label for the column


admin.site.register(Progress, ProgressAdmin)  # Register the Progress model with the custom admin
class ChapterAdmin(admin.ModelAdmin):
    # List view configuration for the Chapter model
    list_display = ('id','get_course_title', 'title', 'order', 'created_at', 'updated_at')  # Reordered to: Course Title, Title, Order
    search_fields = ('title', 'course__title')  # Search functionality based on chapter title and related course title
    list_filter = ('course',)  # Filter chapters by course

    # Custom method to display the course title
    def get_course_title(self, obj):
        return obj.course.title  # Access the title of the related course

    get_course_title.short_description = 'Course Title'  # Set the column name in the admin interface

    # Customize form fields and layout
    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'description', 'order')
        }),
        # Removed 'created_at' and 'updated_at' as they are non-editable
    )

# Register the Chapter model with the customized ChapterAdmin class
admin.site.register(Chapter, ChapterAdmin)



class EnrollmentAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('user', 'course', 'enrolled_at')

    # Fields to search in the admin list view
    search_fields = ('user__username', 'course__title')

    # Fields to filter by in the admin list view
    list_filter = ('course',)

    # Default ordering for the list view
    ordering = ('-enrolled_at',)

    # Number of items to display per page in the admin list view
    list_per_page = 25

    # Specify the organization of fields in form view
    fieldsets = (
        ('Enrollment Information', {
            'fields': ('user', 'course')
        }),
        ('Timestamps', {
            'fields': ('enrolled_at',),
            'classes': ('collapse',),  # Optionally collapse this section for better UI
        }),
    )

    # Make 'enrolled_at' field read-only
    readonly_fields = ('enrolled_at',)

# Register the Enrollment model with the custom admin
admin.site.register(Enrollment, EnrollmentAdmin)




