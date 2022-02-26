# helper functions

import machine
import time
import urequests
import ujson

# fetches time from web based on ip and returns it in proper format to initialize rtc
def set_time():
    # fetch public ip
    public_ip = urequests.get("https://icanhazip.com").text
    # to remove the "\n" at the end
    public_ip = public_ip[:len(public_ip)-1]
    
    # get accurate time with public ip to initialize the rtc
    time_api = urequests.get("https://www.timeapi.io/api/Time/current/ip" + "?ipAddress=" + public_ip)

    t = time_api.json()
    time_now = (t["year"], t["month"], t["day"], 0, t["hour"], t["minute"], t["seconds"], t["milliSeconds"])

    time_api.close()

    return time_now

# converts 24h time format to 12h time format
def conv24h_12h(hour24):
    hour12 = ""
    ampm = ""

    if hour24 == 0:
        hour12 = "1"
        ampm = "AM"

    elif hour24 < 12:
        hour12 = str(hour24)
        ampm = "AM"

    elif hour24 == 12:
        hour12 = "12"
        ampm = "PM"

    elif hour24 > 12:
        hour12 = str(hour24 - 12)
        ampm = "PM"

    return (hour12, ampm)

# fetch covid-19 data
def covid19(country):
    if country == "world":
        covid_api = urequests.get("https://disease.sh/v3/covid-19/all")
        covid_api_json = covid_api.json()

    else:
        covid_api = urequests.get("https://disease.sh/v3/covid-19/countries/" + country)
        covid_api_json = covid_api.json()
        country = covid_api_json["countryInfo"]["iso3"]

    covid_api.close()

    return {"country": country, "cases": str(covid_api_json["cases"]), "deaths": str(covid_api_json["deaths"])}
