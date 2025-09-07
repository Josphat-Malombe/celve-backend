from django.db import migrations

def seed_mps(apps, schema_editor):
    Role = apps.get_model("kyl", "Role")
    Position = apps.get_model("kyl", "Position")

    mp_position, _ = Position.objects.get_or_create(name="MP")

    roles = [
        {
            "title": "Representation",
            "description": "MPs represent the people of their constituencies in the National Assembly, ensuring that their interests are considered in national debates and decisions."
        },
        {
            "title": "Legislation",
            "description": "MPs participate in law-making by debating, amending, and passing Bills that affect the country."
        },
        {
            "title": "Oversight",
            "description": "MPs oversee the actions of the Executive by scrutinizing policies, budgets, and government operations to ensure accountability and transparency."
        },
        {
            "title": "Budget Approval",
            "description": "MPs play a key role in discussing, amending, and approving the national budget and allocation of public resources."
        },
        {
            "title": "Constituency Development",
            "description": "MPs manage the Constituency Development Fund (CDF) and initiate projects that directly benefit their constituents."
        },
    ]

    for role in roles:
        Role.objects.get_or_create(position=mp_position, title=role["title"], description=role["description"])




class Migration(migrations.Migration):

    dependencies = [
        ('kyl', '0016_women_rep'),
    ]

    operations = [
        migrations.RunPython(seed_mps),
    ]
