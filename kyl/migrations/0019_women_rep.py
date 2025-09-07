from django.db import migrations

def seed_women_reps_roles(apps, schema_editor):
    Position = apps.get_model("kyl", "Position")
    Role = apps.get_model("kyl", "Role")

    women_rep, _ = Position.objects.get_or_create(name="Women Rep")

    roles = [
        {
            "title": "Representation of Women Interests",
            "description": "Articulate and champion issues affecting women, children, and other vulnerable groups at the National Assembly level."
        },
        {
            "title": "Legislative Role",
            "description": "Participate in law-making processes by debating and voting on bills and motions in the National Assembly."
        },
        {
            "title": "Oversight",
            "description": "Monitor and oversee the use of public resources by the national government, particularly on matters affecting women and marginalized groups."
        },
        {
            "title": "Promoting Gender Equality",
            "description": "Promote gender equality and inclusion in political, economic, and social development within counties and nationally."
        },
        {
            "title": "Special Interest Representation",
            "description": "Ensure representation of marginalized and special interest groups as mandated by the Constitution."
        },
        {
            "title": "Constituency Engagement",
            "description": "Engage with county residents to bring their views, petitions, and concerns to the National Assembly."
        }
    ]

    for role in roles:
        Role.objects.get_or_create(
            position=women_rep,
            title=role["title"],
            description=role["description"]
        )




class Migration(migrations.Migration):

    dependencies = [
        ('kyl', '0018_mca'),
    ]

    operations = [
        migrations.RunPython(seed_women_reps_roles),
    ]
