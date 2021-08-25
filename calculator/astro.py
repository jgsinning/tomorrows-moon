import math
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Rectangle
from io import StringIO

# https://rdrr.io/cran/astrolibR/src/R/moonpos.R
# http://www.stargazing.net/kepler/altaz.html
# http://www.castor2.ca/16_Calc/01_Moon/03_Phase/index.html


# Calculate Julian Date given day, month, year
def calc_jd(day, month, year):
    d = day
    m = month
    y = year

    # defensive checks
    if d < 1 or d > 31:
        raise ValueError("Day out of range [1,31]")
    if m < 1 or m > 12:
        raise ValueError("Month out of range [1,12]")
    if y < 1900:
        raise ValueError("Year out of range [1900,+)")

    # adjustment for jan + feb
    if m <= 2:
        y -= 1
        m += 12

    # calculate a+b in gregorian calendar
    a = int(y/100)
    b = 2 - a + int(a/4)

    # calculate julian date
    jd = int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + b - 1524.5
    return jd


# Calculate calendar date (and time) from Julian Date
def calc_date(jd):
    # defensive check
    if jd < 0:
        raise ValueError("Julian Date must be at least 0")

    # adjust jd and separate into int and decimal
    jd2 = jd + 0.5
    z = int(jd2)
    f = jd2 - z

    # calculate a depending on z
    a = z
    if z >= 2299161:
        alpha = int((z-1867216.25)/36524.25)
        a = z + 1 + alpha - int(alpha/4)

    # calculate b-e
    b = a + 1524
    c = int((b-122.1)/365.25)
    d = int(365.25*c)
    e = int((b-d)/30.6001)

    # calculate day of month
    day = b - d - int(30.6001*e) + f

    # calculate month
    month = e - 1
    if e >= 14:
        month = e - 13

    # calculate year
    year = c - 4716
    if month <= 2:
        year = c - 4715

    # calculate time
    hour = (day - int(day)) * 24
    minute = (hour - int(hour)) * 60

    # convert day, hour, and minute to ints
    day = int(day)
    hour = int(hour)
    minute = int(minute)

    # return as tuple (d,m,y,h,m)
    return day, month, year, hour, minute


# Vector-scalar dot product
def dot_product(vector, scalar):
    product = 0
    for i in vector:
        product += i * scalar
    return product


# Reduce angle function
def reduce_angle(ang, radians=False):
    # check if angle is too reduced
    if ang < 0:
        if not radians:
            return ang - math.floor(ang / 360) * 360
        return ang - math.floor(ang / (2 * math.pi)) * 2 * math.pi
    # check if degrees or radians
    if not radians:
        return ang - int(ang / 360) * 360
    return ang - int(ang / (2 * math.pi)) * 2 * math.pi


# Given a primary and secondary list and a scalar, find cross product of scalar and primary, add secondary, find sum
# Helper function for nutate()
def nutate_list_helper(list_primary, list_secondary, scalar):
    # copy the primary list for operations
    list_temp = list_primary.copy()

    # multiply each element in temp (primary) by scalar, add value from secondary list
    for i in range(0, len(list_temp)):
        list_temp[i] = float(list_temp[i])      # ensure all items are floats first
        list_temp[i] *= scalar
        list_temp[i] += list_secondary[i]

    # find sum of elements in temp
    tmp = 0
    for i in list_temp:
        tmp += i

    return tmp


# Nutate a given Julian Date
def nutate(jd):
    # constants from Meeus
    coeff1 = [297.85036, 445267.111480, -0.0019142, 1 / 189474]
    coeff2 = [357.52772, 35999.050340, -0.0001603, -1 / 300000]
    coeff3 = [134.96298, 477198.867398, 0.0086972, 1.0 / 56250]
    coeff4 = [93.27191, 483202.017538, -0.0036825, -1.0 / 327270]
    coeff5 = [125.04452, -1934.136261, 0.0020708, 1. / 450000]
    d_lng = [0, -2, 0, 0, 0, 0, -2, 0, 0, -2, -2, -2, 0, 2, 0, 2, 0, 0, -2, 0, 2, 0, 0, -2, 0, -2, 0, 0, 2,
              -2, 0, -2, 0, 0, 2, 2, 0, -2, 0, 2, 2, -2, -2, 2, 2, 0, -2, -2, 0, -2, -2, 0, -1, -2, 1, 0, 0, -1, 0, 0,
              2, 0, 2]
    m_lng = [0, 0, 0, 0, 1, 0, 1, 0, 0, -1, 17, 2, 0, 2, 1, 0, -1, 0, 0, 0, 1, 1, -1, 0,
              0, 0, 0, 0, 0, -1, -1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, -1, 1, -1, -1, 0, -1]
    mp_lng = [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, -1, 0, 1, -1, -1, 1, 2, -2, 0, 2, 2, 1, 0, 0, -1, 0, -1,
               0, 0, 1, 0, 2, -1, 1, 0, 1, 0, 0, 1, 2, 1, -2, 0, 1, 0, 0, 2, 2, 0, 1, 1, 0, 0, 1, -2, 1, 1, 1, -1, 3, 0]
    f_lng = [0, 2, 2, 0, 0, 0, 2, 2, 2, 2, 0, 2, 2, 0, 0, 2, 0, 2, 0, 2, 2, 2, 0, 2, 2, 2, 2, 0, 0, 2, 0, 0,
              0, -2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 0, 0, 0, 2, 0, 2, 0, 2, -2, 0, 0, 0, 2, 2, 0, 0, 2, 2, 2, 2]
    om_lng = [1, 2, 2, 2, 0, 0, 2, 1, 2, 2, 0, 1, 2, 0, 1, 2, 1, 1, 0, 1, 2, 2, 0, 2, 0, 0, 1, 0, 1, 2, 1,
               1, 1, 0, 1, 2, 2, 0, 2, 1, 0, 2, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 2, 0, 0, 2, 2, 2, 2]
    sin_lng = [-171996, -13187, -2274, 2062, 1426, 712, -517, -386, -301, 217,
                -158, 129, 123, 63, 63, -59, -58, -51, 48, 46, -38, -31, 29, 29, 26, -22,
                21, 17, 16, -16, -15, -13, -12, 11, -10, -8, 7, -7, -7, -7,
                6, 6, 6, -6, -6, 5, -5, -5, -5, 4, 4, 4, -4, -4, -4, 3, -3, -3, -3, -3, -3, -3, -3]
    sdelt = [-174.2, -1.6, -0.2, 0.2, -3.4, 0.1, 1.2, -0.4, 0, -0.5, 0, 0.1, 0, 0, 0.1, 0, -0.1, 10, -0.1, 0, 0.1, 33]
    cos_lng = [92025, 5736, 977, -895, 54, -7, 224, 200, 129, -95, 0, -70, -53, 0,
                -33, 26, 32, 27, 0, -24, 16, 13, 0, -12, 0, 0, -10, 0, -8, 7, 9, 7, 6, 0, 5, 3, -3, 0, 3, 3,
                0, -3, -3, 3, 3, 0, 3, 3, 3, 14]
    cdelt = [8.9, -3.1, -0.5, 0.5, -0.1, 0.0, -0.6, 0.0, -0.1, 0.3, 53]

    # radians/degrees constant
    rd = math.pi/180

    # find time t from julian date
    t = (jd-2451545.0)/36525

    # find d via dot product of t and coeff1
    d = reduce_angle(dot_product(coeff1, t) * rd, radians=True)

    # find m via dot product of t and coeff2
    m = reduce_angle(dot_product(coeff2, t) * rd, radians=True)

    # find mprime via dot product of t and coeff3
    mprime = reduce_angle(dot_product(coeff3, t) * rd, radians=True)

    # find f via dot product of t and coeff4
    f = reduce_angle(dot_product(coeff4, t) * rd, radians=True)

    # find omega via dot product of t and coeff5
    omega = reduce_angle(dot_product(coeff5, t) * rd, radians=True)

    # initialize longitude, oblique
    long = 0
    oblique = 0

    # find arg
    arg = dot_product(d_lng, d) + dot_product(m_lng, m) + dot_product(mp_lng, mprime) + dot_product(f_lng, f) \
        + dot_product(om_lng, omega)
    sinarg = t * math.sin(arg)
    cosarg = t * math.cos(arg)

    long = 0.0001 * nutate_list_helper(sdelt, sin_lng, t) * sinarg
    oblique = 0.0001 * nutate_list_helper(cdelt, cos_lng, t) * cosarg

    return long, oblique


# Calculate Moon's right ascension and declination given Julian Date
def calc_moon_pos(jd):
    # constants from Meeus Chapter 47
    d_lng = [0, 2, 2, 0, 0, 0, 2, 2, 2, 2, 0, 1, 0, 2, 0, 0, 4, 0, 4, 2, 2, 1, 1, 2, 2, 4, 2, 0, 2, 2, 1, 2, 0, 0,
              2, 2, 2, 4, 0, 3, 2, 4, 0, 2, 2, 2, 4, 0, 4, 1, 2, 0, 1, 3, 4, 2, 0, 1, 2, 2]
    m_lng = [0, 0, 0, 0, 1, 0, 0, -1, 0, -1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, -1, 0, 0, 0, 1, 0, -1, 0,
              -2, 1, 2, -2, 0, 0, -1, 0, 0, 1, -1, 2, 2, 1, -1, 0, 0, -1, 0, 1, 0, 1, 0, 0, -1, 2, 1, 0, 0]
    mp_lng = [1, -1, 0, 2, 0, 0, -2, -1, 1, 0, -1, 0, 1, 0, 1, 1, -1, 3, -2, -1, 0, -1, 0, 1, 2, 0, -3, -2,
               -1, -2, 1, 0, 2, 0, -1, 1, 0, -1, 2, -1, 1, -2, -1, -1, -2, 0, 1, 4, 0, -2, 0, 2, 1, -2, -3, 2, 1, -1,
               3, -1]
    f_lng = [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, -2, 2, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0,
              0, 0, 0, -2, 2, 0, 2, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0, -2, -2, 0, 0, 0, 0, 0, 0, 0, -2]
    sin_lng = [6288774, 1274027, 658314, 213618, -185116, -114332, 58793, 57066, 53322,
                45758, -40923, -34720, -30383, 15327, -12528, 10980, 10675, 10034, 8548, -7888, -6766,
                -5163, 4987, 4036, 3994, 3861, 3665, -2689, -2602, 2390, -2348, 2236, -2120, -2069, 2048,
                -1773, -1595, 1215, -1110, -892, -810, 759, -713, -700, 691, 596, 549, 537, 520, -487,
                -399, -381, 351, -340, 330, 327, -323, 299, 294, 0.0]
    cos_lng = [-20905355, -3699111, -2955968, -569925, 48888, -3149, 246158, -152138,
                -170733, -204586, -129620, 108743, 104755, 10321, 0, 79661, -34782, -23210, -21636,
                24208, 30824, -8379, -16675, -12831, -10445, -11650, 14403, -7003, 0, 10056, 6322,
                -9884, 5751, 0, -4950, 4130, 0, -3958, 0, 3258, 2616, -1897, -2117, 2354, 0, 0, -1423,
                -1117, -1571, -1739, 0, -4421, 0, 0, 0, 0, 1165, 0, 0, 8752.0]
    d_lat = [0, 0, 0, 2, 2, 2, 2, 0, 2, 0, 2, 2, 2, 2, 2, 2, 2, 0, 4, 0, 0, 0, 1, 0, 0, 0, 1, 0, 4, 4, 0, 4, 2, 2,
              2, 2, 0, 2, 2, 2, 2, 4, 2, 2, 0, 2, 1, 1, 0, 2, 1, 2, 0, 4, 4, 1, 4, 1, 4, 2]
    m_lat = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 1, -1, -1, -1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0,
              0, 0, -1, 0, 0, 0, 0, 1, 1, 0, -1, -2, 0, 1, 1, 1, 1, 1, 0, -1, 1, 0, -1, 0, 0, 0, -1, -2]
    mp_lat = [0, 1, 1, 0, -1, -1, 0, 2, 1, 2, 0, -2, 1, 0, -1, 0, -1, -1, -1, 0, 0, -1, 0, 1, 1, 0, 0, 3, 0,
               -1, 1, -2, 0, 2, 1, -2, 3, 2, -3, -1, 0, 0, 1, 0, 1, 1, 0, 0, -2, -1, 1, -2, 2, -2, -1, 1, 1, -1, 0, 0]
    f_lat = [1, 1, -1, -1, 1, -1, 1, 1, -1, -1, -1, -1, 1, -1, 1, 1, -1, -1, -1, 1, 3, 1, 1, 1, -1, -1, -1,
              1, -1, 1, -3, 1, -3, -1, -1, 1, -1, 1, -1, 1, 1, 1, 1, -1, 3, -1, -1, 1, -1, -1, 1, -1, 1, -1, -1,
              -1, -1, -1, -1, 1]
    sin_lat = [5128122, 280602, 277693, 173237, 55413, 46271, 32573, 17198, 9266, 8822,
                8216, 4324, 4200, -3359, 2463, 2211, 2065, -1870, 1828, -1794, -1749, -1565, -1491,
                -1475, -1410, -1344, -1335, 1107, 1021, 833, 777, 671, 607, 596, 491, -451, 439, 422,
                421, -366, -351, 331, 315, 302, -283, -229, 223, 223, -220, -220, -185, 181, -177, 176,
                166, -164, 132, -119, 115, 107.0]
    coeff0 = [218.3164477, 481267.88123421, -0.00157860, 1.0 / 538841.0, -1.0 / 65194000]
    coeff1 = [297.8501921, 445267.1114034, -0.0018819, 1.0 / 545868.0, -1.0 / 113065000]
    coeff2 = [357.5291092, 35999.0502909, -0.0001536, 1.0 / 24490000]
    coeff3 = [134.9633964, 477198.8675055, 0.0087414, 1.0 / 69699, -1.0 / 14712000]
    coeff4 = [93.2720950, 483202.0175233, -0.0036539, -1.0 / 35260000, 1.0 / 863310000]
    coeff5 = [21.448, -4680.93, -1.55, 1999.25, -51.38, -249.67, -39.05, 7.12, 27.87, 5.79, 2.45]

    # radians/degrees constant
    rd = math.pi/180

    # find time t from julian date
    t = (jd-2451545.0)/36525

    # find lprime via dot product of t and coeff0
    lprime = reduce_angle(dot_product(coeff0, t)) * rd

    # find d via dot product of t and coeff1
    d = reduce_angle(dot_product(coeff1, t)) * rd

    # find m via dot product of t and coeff2
    m = reduce_angle(dot_product(coeff2, t)) * rd

    # find mprime via dot product of t and coeff3
    mprime = reduce_angle(dot_product(coeff3, t)) * rd

    # find f via dot product of t and coeff4
    f = reduce_angle(dot_product(coeff4, t)) * rd

    # find a1-a3
    a1 = (119.75 + 131.849 * t) * rd
    a2 = (53.09 + 479264.290 * t) * rd
    a3 = (313.45 + 481266.484 * t) * rd

    # find suml and sumb
    suml = 3958 * math.sin(a1) + 1962 * math.sin(lprime - f) + 318 * math.sin(a2)
    sumb = -2235 * math.sin(lprime) + 382 * math.sin(a3) + 175 * math.sin(a1 - f) + 175 * math.sin(a1 + f) \
        + 127 * math.sin(lprime - mprime) - 115 * math.sin(lprime + mprime)

    # find e
    e = 1 - 0.002516*t - 0.0000074*(t**2)

    # initialize geolong, geolat, dis
    geolong = 1
    geolat = 1
    dis = 1

    # updated sin_lng, cos_lng, sin_lat
    sinlng = sin_lng
    coslng = cos_lng
    sinlat = sin_lat

    for i in range(0, len(sinlng)):
        mag = abs(m_lng[i])
        if mag == 1:
            sinlng[i] *= e
            coslng[i] *= e
        elif mag == 2:
            sinlng[i] *= e**2
            coslng[i] *= e**2

    for i in range(0, len(sinlat)):
        mag = abs(m_lat[i])
        if mag == 1:
            sinlat[i] *= e
        elif mag == 2:
            sinlat[i] *= e**2

    # find arg, geolong, dis, geolat
    arg = dot_product(d_lng, d) + dot_product(m_lng, m) + dot_product(mp_lng, mprime) + dot_product(f_lng, f)
    geolong = dot_product(coeff0, t) + (dot_product(sinlng, math.sin(arg)) + suml) / 1000000
    dis = 385000.56 + dot_product(coslng, math.cos(arg)) / 1000
    arg = dot_product(d_lat, d) + dot_product(m_lat, m) + dot_product(mp_lat, mprime) + dot_product(f_lat, f)
    geolat = (dot_product(sinlat, math.sin(arg)) + sumb) / 1000000

    # nutate julian date to correct longitude
    nut_long, nut_oblique = nutate(jd)
    geolong += nut_long / 3600
    geolong = reduce_angle(geolong)

    # find lambda, beta, epsilon
    lmda = geolong * rd
    beta = geolat * rd
    epsilon = (((23 + 26/60)/360 + dot_product(coeff5, t)/3600) + nut_oblique/3600) * rd

    # find right ascension and declination
    ra = math.atan2(math.sin(lmda) * math.cos(epsilon) - math.tan(beta) * math.sin(epsilon), math.cos(lmda))
    ra = reduce_angle(ra, radians=True) / rd
    dec = math.asin(math.sin(beta) * math.cos(epsilon) + math.cos(beta) * math.sin(epsilon) * math.sin(lmda)) / rd

    return ra, dec


# Calculate hour angle given declination, altitude, and observer latitude
def calc_ha(dec, alt, lat):
    cos_ha = (math.sin(math.radians(alt)) - math.sin(math.radians(dec)) * math.sin(math.radians(lat))) \
             / (math.cos(math.radians(dec)) * math.cos(math.radians(lat)))
    return math.degrees(math.acos(cos_ha))


# Calculate local sidereal time given hour angle and right ascension
def calc_lst(ha, ra):
    return reduce_angle(ha + ra)


# Convert local sidereal time to local time (returns hour,minute tuple)
def calc_local_time(lst):
    frac = lst / 360
    hour = frac * 24
    minute = (hour - int(hour)) * 60
    return int(hour), int(minute)


# Time zone converter
def convert_time_zone(time, gmt):
    # convert hours
    hour = time[0] + int(gmt)
    while not 0 <= hour <= 23:
        if hour < 0:
            hour += 24
        elif hour > 23:
            hour -= 24

    # convert minutes (if gmt is float)
    minute = time[1] + 60 * (gmt - int(gmt))
    while not 0 <= minute < 60:
        if minute < 0:
            minute += 60
        elif minute >= 60:
            hour -= 60

    return int(hour), int(minute)


# Convert day,month,year to floating-point years
def calc_float_years(day, month, year):
    month_days = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    passed_days = day
    for i in range(0, month):
        passed_days += month_days[i]
    return year + passed_days / 365.25


# Get decimal moon phase given day,month,year
def calc_moon_phase(day, month, year):
    # convert d,m,y to years
    yrs = calc_float_years(day, month, year)

    # find value of k
    k = (yrs - 2000) * 12.3685 - 0.25   # offset k by a quarter cycle
    return k                            # phase is k - int(k)


# Get string moon phase given day,month,year
def str_moon_phase(day, month, year):
    # Get decimal moon phase
    k = calc_moon_phase(day, month, year)
    frac = k - int(k)

    # initialize phase variable
    phase = "Moon Phase"

    # check if positive (year 2000+) or negative (before 2000)
    if k >= 0:
        if frac < 0.5/29.53059 or frac > 1 - 0.5/29.53059:
            phase = "New Moon"
        elif frac < 0.25 - 0.5/29.53059:
            phase = "Waxing Crescent"
        elif frac < 0.25 + 0.5/29.53059:
            phase = "First Quarter"
        elif frac < 0.5 - 0.5/29.53059:
            phase = "Waxing Gibbous"
        elif frac < 0.5 + 0.5/29.53059:
            phase = "Full Moon"
        elif frac < 0.75 - 0.5/29.53059:
            phase = "Waning Gibbous"
        elif frac < 0.75 + 0.5/29.53059:
            phase = "Last Quarter"
        elif frac < 1 - 0.5/29.53059:
            phase = "Waning Crescent"
        else:
            phase = "New Moon"
    else:
        if frac < 0.5/29.53059 or frac > 1 - 0.5/29.53059:
            phase = "New Moon"
        elif frac < 0.25 - 0.5/29.53059:
            phase = "Waning Crescent"
        elif frac < 0.25 + 0.5/29.53059:
            phase = "Last Quarter"
        elif frac < 0.5 - 0.5/29.53059:
            phase = "Waning Gibbous"
        elif frac < 0.5 + 0.5/29.53059:
            phase = "Full Moon"
        elif frac < 0.75 - 0.5/29.53059:
            phase = "Waxing Gibbous"
        elif frac < 0.75 + 0.5/29.53059:
            phase = "First Quarter"
        elif frac < 1 - 0.5/29.53059:
            phase = "Waxing Crescent"
        else:
            phase = "New Moon"

    return phase


# Check for solar/lunar eclipse, returns string
# Works well for solar eclipses, inconsistent with lunar eclipses
def check_eclipse(day, month, year):
    eclipse_type = "No eclipse"
    iterations = 0

    while iterations < 10:
        # get k from date + variation in day
        k = calc_moon_phase(day+iterations/10, month, year)

        # get phase fraction
        frac = k - int(k)

        # check for moon phases
        if frac < 0.5 / 29.53059 or frac > 1 - 0.5 / 29.53059:
            eclipse_type = "Solar"
        if 0.5 + 1 / 29.53059 > frac > 0.5 - 1 / 29.5309:       # increased boundary for better lunar eclipse accuracy
            eclipse_type = "Lunar"
        else:
            iterations += 1
            continue

        # calculate t and f (Meeus Chapter 49)
        t = k / 1236.85
        f = 160.7108 + 390.67050284 * k - 0.0016118 * t**2 - 0.00000227 * t**3 + 0.000000011 * t**4

        # calculate distance between f and nearest multiple of 180
        dist = f - int(f/180)*180

        # check distance for eclipse conditions
        if dist < 13.9:
            eclipse_type = f"{eclipse_type} eclipse"
            return eclipse_type
        if dist > 21 or abs(math.sin(math.radians(f))) > 0.36:
            eclipse_type = "No eclipse"
        else:
            temp_type = eclipse_type
            eclipse_type = f"{temp_type} possible"
            return eclipse_type

        # iterate
        iterations += 1

    if eclipse_type == "Solar" or eclipse_type == "Lunar":
        eclipse_type = "No eclipse"
    return eclipse_type


# Get illumination percentage from day, month, year
def calc_illumination(day, month, year):
    k = calc_moon_phase(day, month, year)
    return 0.5 - math.cos(2 * math.pi * (k - int(k))) / 2


# Get illuminated Moon image
def get_moon_img(day, month, year):
    # get phase from date
    phase = str_moon_phase(day, month, year)

    # get illumination from phase
    illumination = calc_illumination(day, month, year)
    print(phase)
    print(illumination)

    # setup matplotlib plot
    fig = plt.figure()
    fig.patch.set_facecolor('black')
    plt.axis('off')
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    ax.set_facecolor('black')

    # handle new moon
    if phase == "New Moon":
        moon_backdrop = Circle(xy=(0.5, 0.5), radius=0.5, edgecolor=(0.8, 0.8, 0.8, 0.1), fc=(0.8, 0.8, 0.8, 0.1))
        ax.add_patch(moon_backdrop)
    else:
        # add moon to plot
        moon = Circle(xy=(0.5, 0.5), radius=0.5, edgecolor='lightgrey', fc='lightgrey')
        ax.add_patch(moon)

        # add vertical bar over moon
        if phase == "First Quarter" or phase == "Waxing Crescent" or phase == "Waxing Gibbous":
            rect = Rectangle(xy=(0, 0), width=0.5, height=1, edgecolor='k', fc='k')
            ax.add_patch(rect)
        elif phase == "Last Quarter" or phase == "Waning Crescent" or phase == "Waning Gibbous":
            rect = Rectangle(xy=(0.5, 0), width=0.5, height=1, edgecolor='k', fc='k')
            ax.add_patch(rect)

        # draw ellipses for crescents and gibbouses
        if phase == "Waxing Crescent" or phase == "Waning Crescent":
            ellipse = Ellipse(xy=(0.5, 0.5), width=(1-2*illumination), height=1, edgecolor='k', fc='k')
            ax.add_patch(ellipse)
        elif phase == "Waxing Gibbous" or phase == "Waning Gibbous":
            ellipse = Ellipse(xy=(0.5, 0.5), width=(2*illumination-1), height=1, edgecolor='lightgrey', fc='lightgrey')
            ax.add_patch(ellipse)

    img = StringIO()
    fig.savefig(img, format='svg')
    img.seek(0)
    return img.getvalue()


# Get image of Sun-Earth-Moon system
def get_system_img(day, month, year):
    k = calc_moon_phase(day, month, year)

    # setup matplotlib plot
    fig = plt.figure()
    plt.axis('off')
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    ax.set_facecolor('black')

    # add sun
    sun = Circle(xy=(0.5, 0.5), radius=0.1, edgecolor='orange', fc='orange')
    ax.add_patch(sun)

    # add earth's orbit
    earth_orbit_radius = 0.35
    earth_orbit = Circle(xy=(0.5, 0.5), radius=earth_orbit_radius, edgecolor='k', fill=False)
    ax.add_patch(earth_orbit)

    # add earth at proper position
    float_years = calc_float_years(day, month, year)
    earth_angle = reduce_angle(2 * math.pi * (float_years - int(float_years)) + math.pi / 2, radians=True)
    earth_x = 0.5 + earth_orbit_radius * math.cos(earth_angle)
    earth_y = 0.5 + earth_orbit_radius * math.sin(earth_angle)
    earth = Circle(xy=(earth_x, earth_y), radius=0.05, edgecolor='b', fc='b')
    ax.add_patch(earth)

    # add moon's orbit
    moon_orbit_radius = 0.15
    moon_orbit = Circle(xy=(earth_x, earth_y), radius=moon_orbit_radius, edgecolor='k', fill=False)
    ax.add_patch(moon_orbit)

    # add moon at proper position
    moon_angle = reduce_angle(earth_angle + math.pi + (2 * math.pi * (k - int(k))), radians=True)
    moon_x = earth_x + moon_orbit_radius * math.cos(moon_angle)
    moon_y = earth_y + moon_orbit_radius * math.sin(moon_angle)
    moon = Circle(xy=(moon_x, moon_y), radius=0.035, edgecolor='grey', fc='grey')
    ax.add_patch(moon)

    img = StringIO()
    fig.savefig(img, format='svg')
    img.seek(0)
    return img.getvalue()
