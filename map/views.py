import os
import requests
from django.shortcuts import render
from django.apps import apps
import geojson
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def shelter_json_geojson(json_obj):
    geojson_obj = []
    for data in json_obj:
        new_address = ""
        for part in data["address"].split():
            new_address = new_address + " " + part
            if new_address[-1] == ";" or new_address[-2:] == ".,":
                data["address"] = new_address[:-1]
                break
        comments = "N/A"
        if "comments" in data:
            comments = data["comments"]
        locations = []
        locations.append((float(data["longitude"]), float(data["latitude"])))
        geojson_obj.append(
            geojson.Feature(
                geometry=geojson.Point(locations),
                properties={
                    "center_name": data["center_name"],
                    "borough": data["borough"],
                    "address": data["address"],
                    "postcode": data["postcode"],
                    "comments": comments,
                },
            )
        )
    return geojson_obj


# Create your views here.


@login_required(login_url="/login/")
def main_map(request):
    mapbox_access_token = "pk." + os.environ.get("MAPBOX_KEY")

    # All Personal Donations
    resource_post_model = apps.get_model(
        "donation", "ResourcePost"
    )  # getting model from donation app
    post_context = {
        "resource_posts": resource_post_model.objects.filter(
            status__in=["Available", "AVAILABLE"]
        )
    }

    # Shelter API GET
    drop_in_center_URL = "https://data.cityofnewyork.us/resource/bmxf-3rd4.json"
    drop_in_center_r = requests.get(url=drop_in_center_URL)
    drop_in_centers = drop_in_center_r.json()
    shelter_geojson = shelter_json_geojson(drop_in_centers)

    for center in drop_in_centers:
        new_address = ""
        for part in center["address"].split():
            new_address = new_address + " " + part
            if new_address[-1] == ";" or new_address[-2:] == ".,":
                center["address"] = new_address[:-1]
                break

    # Internet spots API GET
    internet_center_URL = "https://data.cityofnewyork.us/resource/yjub-udmw.json"
    internet_center_r = requests.get(url=internet_center_URL)
    internet_centers = internet_center_r.json()

    # Toilets in Computer centers API GET
    computer_centers_URL = "https://data.cityofnewyork.us/resource/cuzb-dmcd.json"
    computer_centers_r = requests.get(url=computer_centers_URL)
    computer_centers = computer_centers_r.json()

    # Toilets in after school programmes API GET
    after_school_prgms_URL = "https://data.cityofnewyork.us/resource/ujsc-un6m.json"
    after_school_prgms_r = requests.get(url=after_school_prgms_URL)
    after_school_prgms = after_school_prgms_r.json()

    current_time = timezone.now()

    return render(
        request,
        "map/main.html",
        {
            "mapbox_access_token": mapbox_access_token,
            "drop_in_centers": drop_in_centers,
            "post_context": post_context["resource_posts"],
            "internet_centers": internet_centers,
            "computer_centers": computer_centers,
            "after_school_prgms": after_school_prgms,
            "shelter_geojson": shelter_geojson,
            "current_time": current_time,
        },
    )
