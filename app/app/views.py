from django.shortcuts import render


def page_not_found_view(request, exception):
    context = {"status": 404, "error_name": "Page not found.", "message": "The page you’re looking for doesn’t exist."}
    return render(request, "errors/user.html", context=context)


def page_bad_request_view(request, exception):
    context = {"status": 400, "error_name": "Bad request.", "message": "You are sending an invalid request."}
    return render(request, "errors/user.html", context=context)
