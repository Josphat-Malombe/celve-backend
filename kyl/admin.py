from django.contrib import admin

# Register your models here.
from . models import Constituency,County,Position,Leader,Role,Candidate,Election

admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(Position)
admin.site.register(Leader)
admin.site.register(Role)
admin.site.register(Election)
admin.site.register(Candidate)