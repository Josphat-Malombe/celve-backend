from django.db import models

# Create your models here.

class County(models.Model):
    name=models.CharField(max_length=100, unique=True)


    class Meta:
        verbose_name_plural="Counties"

    def __str__(self):
        return self.name

    
class Constituency(models.Model):
    name=models.CharField(unique=True,max_length=150)
    county=models.ForeignKey(County, on_delete=models.CASCADE,related_name='constituencies')

    class Meta:
        verbose_name_plural="Constituencies"

    def __str__(self):
        return f"{self.name} ({self.county.name})"
    
    



class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)
    

    def __str__(self):
        return self.name

    




class Leader(models.Model):
    name=models.CharField(max_length=150)
    party=models.CharField(max_length=150,blank=True,null=True)
    position=models.ForeignKey(Position, on_delete=models.CASCADE, related_name='leaders')
    constituency=models.ForeignKey(Constituency, blank=True,null=True, on_delete=models.CASCADE,related_name='leaders')
    county=models.ForeignKey(County, on_delete=models.CASCADE,related_name='leaders')


    def __str__(self):
        if self.constituency:
            return f"{self.name} {self.position.name} ({self.constituency.name},{self.county.name})"
        return f"{self.name} - {self.position.name} ({self.county.name})"
    



class Role(models.Model):
    
    position = models.ForeignKey(Position, related_name="roles", on_delete=models.CASCADE)
    description = models.TextField()
    title = models.CharField(max_length=200) 

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.title} ({self.position.name}"
    




class Election(models.Model):
    LOCATION_TYPE_CHOICES = [
        ('ward', 'Ward'),
        ('constituency', 'Constituency'),
        ('county', 'County'),
    ]

    POSITION_CHOICES = [
        ('governor', 'Governor'),
        ('senator', 'Senator'),
        ('mp', 'Member of Parliament'),
        ('women_rep', 'Women Representative'),
        ('mca', 'MCA'),
    ]

    location_name = models.CharField(max_length=100)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    election_date = models.DateField()

    def __str__(self):
        return f"{self.position.title()} Election in {self.location_name} on {self.election_date}"


class Candidate(models.Model):
    election = models.ForeignKey(Election, related_name="candidates", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    party = models.CharField(max_length=100)
   

    def __str__(self):
        return f"{self.name} ({self.party})"
