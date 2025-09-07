from django.db import migrations

def seed_counties(apps, schema_editor):
    County = apps.get_model("kyl", "County")

    counties = [
        "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita Taveta",
        "Garissa", "Wajir", "Mandera", "Marsabit", "Isiolo", "Meru",
        "Tharaka-Nithi", "Embu", "Kitui", "Machakos", "Makueni", "Nyandarua",
        "Nyeri", "Kirinyaga", "Murang'a", "Kiambu", "Turkana", "West Pokot",
        "Samburu", "Trans Nzoia", "Uasin Gishu", "Elgeyo-Marakwet", "Nandi",
        "Baringo", "Laikipia", "Nakuru", "Narok", "Kajiado", "Kericho",
        "Bomet", "Kakamega", "Vihiga", "Bungoma", "Busia", "Siaya", "Kisumu",
        "Homa Bay", "Migori", "Kisii", "Nyamira", "Nairobi"
    ]

    for county_name in counties:
        County.objects.get_or_create(name=county_name)

def unseed_counties(apps, schema_editor):
    County = apps.get_model("kyl", "County")
    County.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("kyl", "0001_initial"),  
    ]

    operations = [
        migrations.RunPython(seed_counties, unseed_counties),
    ]
