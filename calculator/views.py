from django.shortcuts import render
from calculator.astro import *

# Create your views here.


def index(request):
    return render(request, "index.html")


def references(request):
    return render(request, "references.html")


def accuracy(request):
    return render(request, "accuracy.html")


def moonphases(request):
    return render(request, "moonphases.html")


def moonrises(request):
    return render(request, "moonrises.html")


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

    if day < 1 or day >= 32:
        msg = "Input day must be in the range [1.0, 32.0)"
        return render(request, "error.html", {"result": msg})

    try:
        month = int(input_month)
    except ValueError:
        msg = "Input month must be an integer"
        return render(request, "error.html", {"result": msg})

    if month < 1 or month > 12:
        msg = "Input month must be in the range [1, 12]"
        return render(request, "error.html", {"result": msg})

    try:
        year = int(input_year)
    except ValueError:
        msg = "Input year must be an integer"
        return render(request, "error.html", {"result": msg})

    if year < 1900:
        msg = "Input year must be at least 1900"
        return render(request, "error.html", {"result": msg})

    try:
        latitude = float(input_latitude)
    except ValueError:
        msg = "Input latitude must be a floating-point number"
        return render(request, "error.html", {"result": msg})

    if abs(latitude) >= 83.5:
        msg = "Input latitude must be in the range (-83.5, 83.5)"
        return render(request, "error.html", {"result": msg})

    try:
        timezone = int(input_timezone)
    except ValueError:
        msg = "Input timezone must be an integer or floating-point number"
        return render(request, "error.html", {"result": msg})

    if abs(timezone) > 12:
        msg = "Input timezone must be in the range [-12.0, 12.0]"
        return render(request, "error.html", {"result": msg})

    # passed defensive checks
    # now do the actual calculations

    if day - int(day) == 0.0:
        day = int(day)

    moon_phase = str_moon_phase(day, month, year)
    illumination = calc_illumination(day, month, year)
    phase_angle = calc_phase_angle(day, month, year)
    julian_date = calc_jd(day, month, year)
    right_ascension, declination = calc_moon_pos(julian_date)
    hour_angle = calc_ha(declination, 0, latitude)
    local_sidereal_time = calc_lst(hour_angle, right_ascension)
    local_time = calc_local_time(local_sidereal_time)
    rise_hour, rise_minute = convert_time_zone(local_time, timezone)
    eclipse = check_eclipse(day, month, year)

    moon_img = get_moon_img(day, month, year)
    system_img = get_system_img(day, month, year)

    end_message = ""
    if moon_phase == "Full Moon":
        end_message = "Watch out: you might see a werewolf drinking a pina colada at Trader Vic's"

    # format results
    illumination = int(1000 * illumination + 0.5) / 10.0
    phase_angle = int(1000 * phase_angle + 0.5) / 1000.0
    right_ascension = int(1000 * right_ascension + 0.5) / 1000.0
    declination = int(1000 * declination + 0.5) / 1000.0
    hour_angle = int(1000 * hour_angle + 0.5) / 1000.0

    if rise_hour < 10:
        rise_hour = f"0{rise_hour}"

    if rise_minute < 10:
        rise_minute = f"0{rise_minute}"

    # render the results page with numbers and images
    return render(request, "result.html", {
        "day": day,
        "month": month,
        "year": year,
        "moon_phase": moon_phase,
        "illumination": illumination,
        "phase_angle": phase_angle,
        "julian_date": julian_date,
        "right_ascension": right_ascension,
        "declination": declination,
        "hour_angle": hour_angle,
        "rise_hour": rise_hour,
        "rise_minute": rise_minute,
        "eclipse": eclipse,
        "moon_img": moon_img,
        "system_img": system_img,
        "end_message": end_message
    })
