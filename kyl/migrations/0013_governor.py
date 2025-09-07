from django.db import migrations

def seed_governor_roles(apps, schema_editor):
    Position = apps.get_model("kyl", "Position")
    Role = apps.get_model("kyl", "Role")

    # Ensure Governor position exists
    governor_position, _ = Position.objects.get_or_create(name="Governor")

    roles = [
        {
            "title": "Chief Executive of the County",
            "description": "The Governor is the chief executive of the county, responsible for implementing county laws and policies."
        },
        {
            "title": "Head of County Executive Committee",
            "description": "Chairs the County Executive Committee, appoints members (with assembly approval), and provides leadership in county administration."
        },
        {
            "title": "County Legislation Implementation",
            "description": "Ensures implementation of national and county legislation as provided under the Constitution."
        },
        {
            "title": "Management of County Resources",
            "description": "Oversees the management and use of county resources for the benefit of residents."
        },
        {
            "title": "Promotion of Governance",
            "description": "Promotes democracy, good governance, unity, and peace within the county."
        },
        {
            "title": "Representation of the County",
            "description": "Represents the county in national and international functions as required."
        },
        {
            "title": "Accountability",
            "description": "Provides regular reports to the county assembly on matters of county governance."
        },
    ]

    for role in roles:
        Role.objects.get_or_create(
            position=governor_position,
            title=role["title"],
            description=role["description"]
        )



class Migration(migrations.Migration):

    dependencies = [
        ('kyl', '0012_deputy_president_roles'),
    ]

    operations = [
        migrations.RunPython(seed_governor_roles),
    ]
