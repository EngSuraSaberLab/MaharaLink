from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Enrollment

admin.site.site_header='Mahara Platform'
admin.site.site_title ='Mahara'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        'course_image',
        'title',
        'price',
        'is_active',
        'created_at',
    )

    list_filter = (
        'is_active',
        'created_at',
    )

    search_fields = (
        'title',
        'short_description',
        'description',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    readonly_fields = (
        'created_at',
    )

    fieldsets = (

        ("Course Information", {
            'fields': (
                'title',
                'slug',
                'price',
                'is_active',
            )
        }),

        ("Course Content", {
            'fields': (
                'short_description',
                'description',
                'image',
                'video',
            )
        }),

        ("System Info", {
            'fields': (
                'created_at',
            )
        }),
    )

    def course_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:60px;height:40px;object-fit:cover;border-radius:4px;" />',
                obj.image.url
            )
        return "—"

    course_image.short_description = "Image"


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'course',
        'is_paid',
        'is_active',
        'enrolled_at',
    )

    list_filter = (
        'is_paid',
        'is_active',
        'enrolled_at',
    )

    search_fields = (
        'user__username',
        'course__title',
    )

    readonly_fields = (
        'enrolled_at',
    )

    autocomplete_fields = (
        'user',
        'course',
    )