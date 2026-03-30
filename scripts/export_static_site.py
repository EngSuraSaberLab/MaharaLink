from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django

django.setup()

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db.models import Count, Q
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.utils import translation

from blog.models import Category, Post
from comments.models import Comment
from courses.models import Course, Enrollment


DOCS_DIR = ROOT_DIR / "docs"
STATIC_SOURCE = ROOT_DIR / "staticfiles"
MEDIA_SOURCE = ROOT_DIR / "media"
BASE_PATH = "/MaharaLink"

REQUIRED_STATIC_DIRS = ("css", "js", "img")
REQUIRED_VENDOR_FILES = (
    "bootstrap/css/bootstrap.min.css",
    "bootstrap/js/bootstrap.bundle.min.js",
    "bootstrap-icons/bootstrap-icons.css",
    "bootstrap-icons/fonts/bootstrap-icons.woff",
    "bootstrap-icons/fonts/bootstrap-icons.woff2",
    "aos/aos.css",
    "aos/aos.js",
    "glightbox/css/glightbox.min.css",
    "glightbox/js/glightbox.min.js",
    "swiper/swiper-bundle.min.css",
    "swiper/swiper-bundle.min.js",
    "imagesloaded/imagesloaded.pkgd.min.js",
    "isotope-layout/isotope.pkgd.min.js",
    "purecounter/purecounter_vanilla.js",
    "php-email-form/validate.js",
)


def ensure_clean_docs_dir() -> None:
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


def copy_tree(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copytree(src, dst, dirs_exist_ok=True)


def copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_publish_assets() -> None:
    assets_dir = DOCS_DIR / "assets"
    for name in REQUIRED_STATIC_DIRS:
        copy_tree(STATIC_SOURCE / name, assets_dir / name)

    vendor_dir = assets_dir / "vendor"
    for relative_path in REQUIRED_VENDOR_FILES:
        copy_file(STATIC_SOURCE / "vendor" / relative_path, vendor_dir / relative_path)

    media_dir = DOCS_DIR / "media"
    for name in ("blog", "courses"):
        copy_tree(MEDIA_SOURCE / name, media_dir / name)


def minify_css(content: str) -> str:
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.S)
    content = re.sub(r"\s+", " ", content)
    content = re.sub(r"\s*([{}:;,])\s*", r"\1", content)
    return content.strip()


def minify_js(content: str) -> str:
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.S)
    content = re.sub(r"(?m)^\s*//.*$", "", content)
    content = re.sub(r"\n+", "\n", content)
    content = re.sub(r"[ \t]+", " ", content)
    return content.strip()


def compress_published_assets() -> None:
    css_file = DOCS_DIR / "assets" / "css" / "main.css"
    js_file = DOCS_DIR / "assets" / "js" / "main.js"
    if css_file.exists():
        css_file.write_text(minify_css(css_file.read_text(encoding="utf-8")), encoding="utf-8")
    if js_file.exists():
        js_file.write_text(minify_js(js_file.read_text(encoding="utf-8")), encoding="utf-8")


def write_publish_markers() -> None:
    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")


def base_url(lang: str) -> str:
    return f"{BASE_PATH}/ar/" if lang == "ar" else f"{BASE_PATH}/"


def docs_lang_dir(lang: str) -> Path:
    return DOCS_DIR / "ar" if lang == "ar" else DOCS_DIR


def build_page_urls(lang: str, route_name: str, slug: str | None = None) -> dict[str, str]:
    home = base_url(lang)
    language_en = f"{BASE_PATH}/"
    language_ar = f"{BASE_PATH}/ar/"

    if route_name == "blog":
        language_en = f"{BASE_PATH}/blog/"
        language_ar = f"{BASE_PATH}/ar/blog/"
    elif route_name == "blog_detail" and slug:
        language_en = f"{BASE_PATH}/blog/{slug}/"
        language_ar = f"{BASE_PATH}/ar/blog/{slug}/"
    elif route_name == "course_detail" and slug:
        language_en = f"{BASE_PATH}/courses/{slug}/"
        language_ar = f"{BASE_PATH}/ar/courses/{slug}/"
    elif route_name in {"terms", "privacy", "cookies"}:
        language_en = f"{BASE_PATH}/{route_name}/"
        language_ar = f"{BASE_PATH}/ar/{route_name}/"

    return {
        "home": home,
        "blog": f"{home}blog/",
        "terms": f"{home}terms/",
        "privacy": f"{home}privacy/",
        "cookies": f"{home}cookies/",
        "language_en": language_en,
        "language_ar": language_ar,
    }


def build_request(path: str):
    request = RequestFactory().get(path)
    request.user = AnonymousUser()
    return request


def attach_course_urls(courses: list[Course], lang: str) -> None:
    root = base_url(lang)
    for course in courses:
        course.static_url = f"{root}courses/{course.slug}/"


def attach_post_urls(posts: list[Post], lang: str) -> None:
    root = base_url(lang)
    for post in posts:
        post.static_url = f"{root}blog/{post.slug}/"


def render_page(*, template_name: str, output_path: Path, lang: str, route_name: str, current_page: str, context: dict, slug: str | None = None) -> None:
    request_path = "/" + output_path.relative_to(DOCS_DIR).as_posix().replace("index.html", "")
    render_context = {
        "static_export": True,
        "static_base_path": BASE_PATH,
        "page_urls": build_page_urls(lang, route_name, slug=slug),
        "current_page": current_page,
        **context,
    }
    with translation.override(lang):
        html = render_to_string(template_name, render_context, request=build_request(request_path))
    html = html.replace("\ufeff", "")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def export_home(lang: str, courses: list[Course]) -> None:
    attach_course_urls(courses, lang)
    render_page(
        template_name="home.html",
        output_path=docs_lang_dir(lang) / "index.html",
        lang=lang,
        route_name="home",
        current_page="home",
        context={"courses": courses, "my_courses": []},
    )


def export_courses(lang: str, courses: list[Course]) -> None:
    attach_course_urls(courses, lang)
    for course in courses:
        render_page(
            template_name="courses/course_detail.html",
            output_path=docs_lang_dir(lang) / "courses" / course.slug / "index.html",
            lang=lang,
            route_name="course_detail",
            current_page="courses",
            slug=course.slug,
            context={
                "course": course,
                "user_enrolled": False,
                "comments": list(Comment.objects.filter(course=course, parent__isnull=True).select_related("user")),
                "comments_count": Comment.objects.filter(course=course).count(),
                "students_count": Enrollment.objects.filter(course=course, is_active=True).count(),
            },
        )


def export_blog(lang: str, posts: list[Post], categories: list[Category]) -> None:
    attach_post_urls(posts, lang)
    render_page(
        template_name="blog/blog_list.html",
        output_path=docs_lang_dir(lang) / "blog" / "index.html",
        lang=lang,
        route_name="blog",
        current_page="blog",
        context={"posts": posts, "categories": categories, "selected_category": None},
    )

    for post in posts:
        render_page(
            template_name="blog/blog_detail.html",
            output_path=docs_lang_dir(lang) / "blog" / post.slug / "index.html",
            lang=lang,
            route_name="blog_detail",
            current_page="blog",
            slug=post.slug,
            context={
                "post": post,
                "categories": categories,
                "comments": list(Comment.objects.filter(post=post, parent__isnull=True).select_related("user")),
                "comments_count": Comment.objects.filter(post=post).count(),
            },
        )


def legal_content(lang: str) -> dict[str, dict[str, str]]:
    if lang == "ar":
        return {
            "terms": {
                "title": "???? ????????? - MaharaLink",
                "kicker": "???? ?????????",
                "heading": "???? ??????? ???? ????? ???????",
                "intro": "??? ?????? ?????? ?????? ????? ??? ??? GitHub Pages.",
                "content": "<p>?????? ??????? ????? ????????? ??? ????? ???????? ?????? ?? ????????? ?????.</p><p>??????? ??????? ???? ????? ??????? ??????? ??? ??????? ??? ???? ?????.</p>",
            },
            "privacy": {
                "title": "????? ???????? - MaharaLink",
                "kicker": "????????",
                "heading": "????? ????????",
                "intro": "???? GitHub Pages ?? ???? ?????? ?????? ?? ??????? ??????.",
                "content": "<p>??? ?????? ?? ?????? ?????? ??? ?? ????? ?????? ??????.</p><p>??? ????? ????? ????? ??? ???? ??????? ???????? ???????.</p>",
            },
            "cookies": {
                "title": "????? ????? ???????? - MaharaLink",
                "kicker": "????? ????????",
                "heading": "????? ????? ????????",
                "intro": "???? ????? ?????? ??? ??? ???? ?? ?????? ?????? ?? ???????.",
                "content": "<p>?? ????? ??? ?????? ??? ????? ????? ?????.</p><p>?? ??????? ??????? ?????? ???????? ????? ??????? ????? ????????? ?????? ?? ???????.</p>",
            },
        }

    return {
        "terms": {
            "title": "Terms of Service - MaharaLink",
            "kicker": "Terms",
            "heading": "Static Showcase Terms",
            "intro": "This GitHub Pages build is a static showcase version of MaharaLink.",
            "content": "<p>This edition is published for presentation only and does not enable live enrollment, checkout, or user interaction.</p><p>It reflects the original Django project after conversion into a static front-end showcase.</p>",
        },
        "privacy": {
            "title": "Privacy Policy - MaharaLink",
            "kicker": "Privacy",
            "heading": "Privacy Policy",
            "intro": "The GitHub Pages version does not process real account or payment data.",
            "content": "<p>This static build does not provide live authentication or visitor database storage.</p><p>Your browser only loads the static assets required to display the site.</p>",
        },
        "cookies": {
            "title": "Cookies Policy - MaharaLink",
            "kicker": "Cookies",
            "heading": "Cookies Policy",
            "intro": "This showcase uses only minimal browser-side behavior.",
            "content": "<p>The current build does not rely on a full application session system.</p><p>If a future live deployment is added, its cookie usage may differ from this static version.</p>",
        },
    }


def export_legal_pages(lang: str) -> None:
    for slug, page in legal_content(lang).items():
        render_page(
            template_name="static/legal_page.html",
            output_path=docs_lang_dir(lang) / slug / "index.html",
            lang=lang,
            route_name=slug,
            current_page="legal",
            context={
                "page_title": page["title"],
                "page_kicker": page["kicker"],
                "page_heading": page["heading"],
                "page_intro": page["intro"],
                "page_content": page["content"],
            },
        )


def export_not_found(lang: str) -> None:
    render_page(
        template_name="404.html",
        output_path=docs_lang_dir(lang) / "404.html",
        lang=lang,
        route_name="home",
        current_page="legal",
        context={},
    )


def main() -> None:
    settings.STATIC_URL = f"{BASE_PATH}/assets/"
    settings.MEDIA_URL = f"{BASE_PATH}/media/"

    ensure_clean_docs_dir()
    copy_publish_assets()

    courses = list(Course.objects.filter(is_active=True))
    posts = list(Post.objects.filter(is_published=True).select_related("category"))
    categories = list(Category.objects.annotate(published_posts_count=Count("posts", filter=Q(posts__is_published=True))).filter(published_posts_count__gt=0))

    for lang in ("en", "ar"):
        export_home(lang, courses)
        export_courses(lang, courses)
        export_blog(lang, posts, categories)
        export_legal_pages(lang)
        export_not_found(lang)

    compress_published_assets()
    write_publish_markers()
    print(f"Static export generated in {DOCS_DIR}")


if __name__ == "__main__":
    main()
