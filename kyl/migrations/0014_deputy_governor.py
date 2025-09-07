from django.db import migrations

def seed_deputy_governor_roles(apps, schema_editor):
    Position = apps.get_model("kyl", "Position")
    Role = apps.get_model("kyl", "Role")

    deputy_governor, _ = Position.objects.get_or_create(name="Deputy Governor")

    roles = [
        {
            "title": "Principal Assistant to the Governor",
            "description": "The Deputy Governor is the principal assistant of the Governor in executing county functions and may represent the Governor when delegated."
        },
        {
            "title": "Assumption of Office of Governor",
            "description": "If the Governor dies, resigns, is impeached, or is otherwise permanently incapacitated, the Deputy Governor assumes the office of Governor for the remainder of the term."
        },
        {
            "title": "Acting Governor",
            "description": "When the Governor is temporarily absent, incapacitated, or otherwise unable to act, the Deputy Governor serves as the Acting Governor."
        },
        {
            "title": "Collaboration with County Executive",
            "description": "Supports the Governor in coordinating and supervising county executive functions, ensuring smooth running of county government."
        },
    ]

    for role in roles:
        Role.objects.get_or_create(
            position=deputy_governor,
            title=role["title"],
            description=role["description"]
        )

def unseed_deputy_governor_roles(apps, schema_editor):
    Role = apps.get_model("kyl", "Role")
    Position = apps.get_model("kyl", "Position")

    try:
        deputy_governor = Position.objects.get(name="Deputy Governor")
        Role.objects.filter(position=deputy_governor).delete()
    except Position.DoesNotExist:
        pass




class Migration(migrations.Migration):

    dependencies = [
        ('kyl', '0013_governor'),
    ]

    operations = [
        migrations.RunPython(seed_deputy_governor_roles, unseed_deputy_governor_roles),
    ]
