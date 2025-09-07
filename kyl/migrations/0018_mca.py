from django.db import migrations

def seed_mca_roles(apps, schema_editor):
    Position = apps.get_model("kyl", "Position")
    Role = apps.get_model("kyl", "Role")

    # Ensure MCA position exists
    mca_position, _ = Position.objects.get_or_create(name="MCA")

    roles = [
        {
            "title": "Representation of the Ward",
            "description": "Represent the residents of their electoral ward in the county assembly."
        },
        {
            "title": "Legislation",
            "description": "Participate in making laws at the county level, particularly those that affect the county and ward residents."
        },
        {
            "title": "Oversight",
            "description": "Provide oversight over the County Executive Committee and ensure county resources are used responsibly."
        },
        {
            "title": "Budget Approval",
            "description": "Approve budgets and development plans of the county government, ensuring that local priorities are addressed."
        },
        {
            "title": "Development Representation",
            "description": "Push for development initiatives and allocation of county resources in their respective wards."
        },
        {
            "title": "Accountability to the People",
            "description": "Remain accountable to the electorate by holding regular consultative meetings and maintaining transparency."
        }
    ]

    for role in roles:
        Role.objects.get_or_create(position=mca_position, **role)



class Migration(migrations.Migration):

    dependencies = [
        ('kyl', '0017_mp'),
    ]

    operations = [
        migrations.RunPython(seed_mca_roles),
    ]
