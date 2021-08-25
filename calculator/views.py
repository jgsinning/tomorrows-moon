from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "index.html")


def calculation(request):
    # get post requests from index.html
    input_day = request.POST['input_day']
    input_month = request.POST['input_month']
    input_year = request.POST['input_year']
    input_latitude = request.POST['input_latitude']
    input_timezone = request.POST['input_timezone']

    # defensive checks because somebody will definitely try to break this
    # also if you're reading this hi! hope your day is going well :)
    try:
        day = float(input_day)
    except ValueError:
        msg = "Input day must be an integer or floating-point number"
        return render(request, "error.html", {"result": msg})

    try:
        month = int(input_month)
    except ValueError:
        msg = "Input month must be an integer"
        return render(request, "error.html", {"result": msg})

    try:
        year = int(input_year)
    except ValueError:
        msg = "Input year must be an integer"
        return render(request, "error.html", {"result": msg})

    try:
        latitude = int(input_latitude)
    except ValueError:
        msg = "Input latitude must be a floating-point number"
        return render(request, "error.html", {"result": msg})

    try:
        timezone = int(input_timezone)
    except ValueError:
        msg = "Input month must be an integer or floating-point number"
        return render(request, "error.html", {"result": msg})

    # passed defensive checks
    # now do the actual calculations

    # calculations here

    # render the results page with numbers and images
