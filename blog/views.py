from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count, Q
from .models import Category, Post
from comments.models import Comment
from comments.forms import CommentForm


def blogPage(request):
    selected_category_slug = request.GET.get("category")
    posts = Post.objects.filter(is_published=True).select_related("category")
    categories = Category.objects.annotate(
        published_posts_count=Count("posts", filter=Q(posts__is_published=True))
    ).filter(published_posts_count__gt=0)

    selected_category = None
    if selected_category_slug:
        selected_category = get_object_or_404(categories, slug=selected_category_slug)
        posts = posts.filter(category=selected_category)

    context = {
        "posts": posts,
        "categories": categories,
        "selected_category": selected_category,
    }

    return render(request, "blog/blog_list.html", context)


def blogDetail(request, slug):
    post = get_object_or_404(Post.objects.select_related("category"), slug=slug, is_published=True)
    categories = Category.objects.annotate(
        published_posts_count=Count("posts", filter=Q(posts__is_published=True))
    ).filter(published_posts_count__gt=0)

    comments = Comment.objects.filter(
        post=post,
        parent__isnull=True
    )

    comments_count = Comment.objects.filter(post=post).count()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')

        comment_form = CommentForm(request.POST)

        parent_id = request.POST.get("parent_id")

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post

            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass

            comment.save()

            return redirect(
                reverse('blog:blogDetail', kwargs={'slug': post.slug}) + '#comments-section'
            )
    else:
        comment_form = CommentForm()

    context = {
        "post": post,
        "categories": categories,
        "comments": comments,
        "comments_count": comments_count,
        "comment_form": comment_form,
    }

    return render(request, "blog/blog_detail.html", context)
