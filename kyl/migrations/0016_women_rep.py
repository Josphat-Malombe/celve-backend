from django.db import migrations

def seed_women_rep_roles(apps, schema_editor):
    Role = apps.get_model("kyl", "Role")
    Position = apps.get_model("kyl", "Position")

    women_rep_position, _ = Position.objects.get_or_create(name="Women Rep")

    roles = [
        {
            "title": "Representation of Women Interests",
            "description": "Represents women’s interests from the county in the National Assembly."
        },
        {
            "title": "Promotion of Gender Equality",
            "description": "Advocates for laws and policies that promote gender equality and inclusion."
        },
        {
            "title": "Special Interests Representation",
            "description": "Champions the rights of marginalized groups, youth, persons with disabilities, and other vulnerable groups."
        },
        {
            "title": "Legislative Role",
            "description": "Participates in debating and passing laws in the National Assembly."
        },
        {
            "title": "Oversight Role",
            "description": "Exercises oversight over national revenue allocated to county governments, especially on issues affecting women and marginalized groups."
        },
    ]

    for role in roles:
        Role.objects.get_or_create(
            position=women_rep_position,
            title=role["title"],
            description=role["description"],
        )

class Migration(migrations.Migration):


    dependencies = [
        ('kyl', '0015_senator'),
    ]

    operations = [
    ]
