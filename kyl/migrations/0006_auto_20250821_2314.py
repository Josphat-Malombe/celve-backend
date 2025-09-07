from django.db import migrations

def seed_deputy_governors(apps, schema_editor):
    County = apps.get_model("kyl", "County")
    Leader = apps.get_model("kyl", "Leader")

    deputy_governors_data = [
        ("Mombasa", "Deputy Governor", "Francis Thoya"),
        ("Kwale", "Deputy Governor", "Fatuma Achani"),
        ("Kilifi", "Deputy Governor", "Gideon Saburi"),
        ("Tana River", "Deputy Governor", "Mahmud Mohamed"),
        ("Lamu", "Deputy Governor", "Abdulhakim Aboud Bwana"),
        ("Taita Taveta", "Deputy Governor", "Majala Mlagui"),
        ("Garissa", "Deputy Governor", "Abdi Dagane"),
        ("Wajir", "Deputy Governor", "Ahmed Muhumed"),
        ("Mandera", "Deputy Governor", "Ali Maalim"),
        ("Marsabit", "Deputy Governor", "Solomon Gubo Riwe"),
        ("Isiolo", "Deputy Governor", "Dr. James Lowasa"),
        ("Meru", "Deputy Governor", "Titus Ntuchiu"),
        ("Tharaka-Nithi", "Deputy Governor", "Nyamu Kagwima"),
        ("Embu", "Deputy Governor", "David Kariuki"),
        ("Kitui", "Deputy Governor", "Dr. Wathe Nzau"),
        ("Machakos", "Deputy Governor", "Francis Maliti"),
        ("Makueni", "Deputy Governor", "Adelina Mwau"),
        ("Nyandarua", "Deputy Governor", "Cecilia Mbuthia"),
        ("Nyeri", "Deputy Governor", "Dr. Caroline Karugu"),
        ("Kirinyaga", "Deputy Governor", "Peter Ndambiri"),
        ("Murang’a", "Deputy Governor", "Maina Kamau"),
        ("Kiambu", "Deputy Governor", "Joyce Ngugi"),
        ("Turkana", "Deputy Governor", "Peter Emuria Lotethiro"),
        ("West Pokot", "Deputy Governor", "Dr. Nicholas Atudonyang"),
        ("Samburu", "Deputy Governor", "Julius Leseeto"),
        ("Trans Nzoia", "Deputy Governor", "Dr. Stanley Kenei Tarus"),
        ("Uasin Gishu", "Deputy Governor", "Daniel Chemno"),
        ("Elgeyo-Marakwet", "Deputy Governor", "Wesley Rotich"),
        ("Nandi", "Deputy Governor", "Yulita Mitei"),
        ("Baringo", "Deputy Governor", "Jacob Chepkwony"),
        ("Laikipia", "Deputy Governor", "John Mwaniki"),
        ("Nakuru", "Deputy Governor", "Eric Korir"),
        ("Narok", "Deputy Governor", "Evalyn Aruasa"),
        ("Kajiado", "Deputy Governor", "Martin Moshisho"),
        ("Kericho", "Deputy Governor", "Lily Ngok"),
        ("Bomet", "Deputy Governor", "Dr. Hillary Barchok"),
        ("Kakamega", "Deputy Governor", "Prof. Philip Kutima"),
        ("Vihiga", "Deputy Governor", "Patrick Saisi"),
        ("Bungoma", "Deputy Governor", "Prof. Charles Ngome"),
        ("Busia", "Deputy Governor", "Moses Mulomi"),
        ("Siaya", "Deputy Governor", "James Okumbe"),
        ("Kisumu", "Deputy Governor", "Dr. Mathew Owili"),
        ("Homa Bay", "Deputy Governor", "Hamilton Orata"),
        ("Migori", "Deputy Governor", "Nelson Mahanga Mwita"),
        ("Kisii", "Deputy Governor", "Joash Maangi"),
        ("Nyamira", "Deputy Governor", "Amos Nyaribo"),
        ("Nairobi", "Deputy Governor", "Polycarp Igathe"),
    ]

    for county_name, position, name in deputy_governors_data:
        county = County.objects.get(name=county_name)

        # find governor of this county
        governor = Leader.objects.filter(county=county, position="Governor").first()
        party = governor.party if governor else None  # inherit governor’s party

        Leader.objects.update_or_create(
            county=county,
            position=position,
            defaults={
                "name": name,
                "party": party,
            }
        )


def unseed_deputy_governors(apps, schema_editor):
    Leader = apps.get_model("kyl", "Leader")
    Leader.objects.filter(position="Deputy Governor").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('kyl', '0004_merge_0002_auto_20250821_2135_0003_auto_20250821_2251'),
    ]

    operations = [
        migrations.RunPython(seed_deputy_governors, unseed_deputy_governors),
    ]
