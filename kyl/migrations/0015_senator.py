from django.db import migrations

def seed_senator_roles(apps, schema_editor):
    Role = apps.get_model("kyl", "Role")
    Position = apps.get_model("kyl", "Position")

    senator_position, _ = Position.objects.get_or_create(name="Senator")

    roles = [
        {
            "title": "Representation of Counties",
            "description": "Senators represent and protect the interests of the counties and their governments in the national arena."
        },
        {
            "title": "Participation in Law-making",
            "description": "Senators participate in the passing of laws, especially those affecting counties."
        },
        {
            "title": "Allocation of National Revenue",
            "description": "Senators determine how national revenue is shared among the 47 counties."
        },
        {
            "title": "Oversight of Revenue Allocation",
            "description": "Senators oversee how county governments utilize national revenue allocated to them."
        },
        {
            "title": "Impeachment Role",
            "description": "Senators determine the outcome of impeachment proceedings against Governors."
        },
    ]

    for role in roles:
        Role.objects.get_or_create(
            position=senator_position,
            title=role["title"],
            description=role["description"],
        )



class Migration(migrations.Migration):

    dependencies = [
        ('kyl', '0014_deputy_governor'),
    ]

    operations = [
        migrations.RunPython(seed_senator_roles),
    ]
