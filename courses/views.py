from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import FileResponse, Http404
from django.conf import settings
from django.urls import reverse
from pathlib import Path
from .models import Course, Enrollment
from comments.models import Comment
from comments.forms import CommentForm


def homePage(request):
    courses = Course.objects.filter(is_active=True)

    my_courses = []
    if request.user.is_authenticated:
        my_courses = Course.objects.filter(
            enrollments__user=request.user,
            enrollments__is_active=True
        ).distinct()

    context = {
        'courses': courses,
        'my_courses': my_courses,
    }
    return render(request, 'home.html', context)


def course_list(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'courses/list.html', {'courses': courses})


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)

    user_enrolled = False
    if request.user.is_authenticated:
        user_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=course,
            is_active=True
        ).exists()

    comments = Comment.objects.filter(
        course=course,
        parent__isnull=True
    )

    comments_count = Comment.objects.filter(course=course).count()

    students_count = Enrollment.objects.filter(
        course=course,
        is_active=True
    ).count()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')

        comment_form = CommentForm(request.POST)
        parent_id = request.POST.get("parent_id")

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.course = course

            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass

            comment.save()

            return redirect(
                reverse('course_detail', kwargs={'slug': course.slug}) + '#comments-section'
            )
    else:
        comment_form = CommentForm()

    context = {
        'course': course,
        'user_enrolled': user_enrolled,
        'comments': comments,
        'comment_form': comment_form,
        'comments_count': comments_count,
        'students_count': students_count,
    }

    return render(request, 'courses/course_detail.html', context)


def media_file(request, file_path):
    if file_path.startswith("course_videos/"):
        raise Http404("Direct access to course videos is not allowed")

    file_full_path = Path(settings.MEDIA_ROOT) / file_path

    if not file_full_path.exists() or not file_full_path.is_file():
        raise Http404("Media file not found")

    return FileResponse(open(file_full_path, 'rb'))


@login_required
def course_video(request, slug):
    course = get_object_or_404(Course, slug=slug)

    enrolled = Enrollment.objects.filter(
        user=request.user,
        course=course,
        is_active=True
    ).exists()

    if not enrolled:
        raise Http404("You are not enrolled in this course")

    if not course.video:
        raise Http404("Video not found")

    video_path = Path(settings.MEDIA_ROOT) / course.video.name

    return FileResponse(open(video_path, "rb"), content_type="video/mp4")
