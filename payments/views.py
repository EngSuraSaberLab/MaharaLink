import stripe
from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from courses.models import Course, Enrollment

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_checkout_session(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    success_path = reverse("payment_success", kwargs={"slug": course.slug})

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='payment',
        metadata={
            'course_slug': course.slug,
            'user_id': request.user.id,
        },
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': course.title,
                        'description': course.short_description,
                    },
                    'unit_amount': int(course.price * 100),
                },
                'quantity': 1,
            }
        ],
        success_url=request.build_absolute_uri(
            f"{success_path}?session_id={{CHECKOUT_SESSION_ID}}"
        ),
        cancel_url=request.build_absolute_uri(
            f'/courses/{course.slug}/'
        ),
    )

    if not checkout_session.url:
        raise Http404("Stripe checkout URL was not created.")

    request.session["last_checkout_session_id"] = checkout_session.id

    return redirect(checkout_session.url, code=303)


@login_required
def payment_success(request, slug):
    course = get_object_or_404(Course, slug=slug)
    session_id = request.GET.get("session_id")

    if not session_id or session_id == "{CHECKOUT_SESSION_ID}":
        session_id = request.session.get("last_checkout_session_id")

    if not session_id:
        raise Http404("Missing checkout session.")

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
    except Exception as exc:
        raise Http404("Invalid checkout session.") from exc

    if checkout_session.get("payment_status") != "paid":
        raise Http404("Payment has not been completed.")

    metadata = checkout_session.get("metadata", {})
    course_slug = metadata.get("course_slug")
    user_id = metadata.get("user_id")

    if course_slug != course.slug or str(user_id) != str(request.user.id):
        raise Http404("Checkout session does not match this user or course.")

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    if not enrollment.is_paid or not enrollment.is_active:
        enrollment.is_paid = True
        enrollment.is_active = True
        enrollment.save()

    request.session.pop("last_checkout_session_id", None)

    context = {
        "course": course,
    }

    return render(request, "payments/payment_success.html", context)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    print("=== WEBHOOK CALLED ===")
    print("Signature header:", sig_header)
    print("Webhook secret from settings:", settings.STRIPE_WEBHOOK_SECRET)

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
        print("Webhook verified successfully. Event type:", event["type"])

    except ValueError as e:
        print("Invalid payload error:", str(e))
        return HttpResponse(status=400)

    except Exception as e:
        print("Signature verification / construct error:", str(e))
        return HttpResponse(status=400)

    try:
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            course_slug = session["metadata"].get("course_slug")
            user_id = session["metadata"].get("user_id")

            print("Metadata course_slug:", course_slug)
            print("Metadata user_id:", user_id)

            if course_slug and user_id:
                course = Course.objects.get(slug=course_slug)

                enrollment, created = Enrollment.objects.get_or_create(
                    user_id=user_id,
                    course=course
                )

                enrollment.is_paid = True
                enrollment.is_active = True
                enrollment.save()

                print("Enrollment activated successfully.")

    except Exception as e:
        print("Webhook processing error:", str(e))
        return HttpResponse(status=400)

    return HttpResponse(status=200)
