from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Position, Leader, Constituency, County,Role,Election,Candidate





class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "title", "description"]

class PositionSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    class Meta:
        model = Position
        fields = ["id", "name","roles"]


class CountySerializer(serializers.ModelSerializer):
  
    constituencies = serializers.StringRelatedField(many=True, read_only=True)
    leaders = serializers.SerializerMethodField()

    class Meta:
        model = County
        fields = ["id", "name", "constituencies", "leaders"]

    def get_leaders(self, obj):
        allowed_positions = {"Governor", "Deputy Governor", "Senator", "Women Rep"}
        leaders = Leader.objects.filter(
            county=obj,
            position__name__in=allowed_positions
        )
        return LeaderSerializer(leaders, many=True).data


class ConstituencySerializer(serializers.ModelSerializer):
    mp=serializers.SerializerMethodField()
    county = serializers.StringRelatedField(read_only=True)
    county_id = serializers.PrimaryKeyRelatedField(
        queryset=County.objects.all(),  
        source="county",
        write_only=True,
    )

    class Meta:
        model = Constituency
        fields = ["id", "name", "county", "mp","county_id"]
    def get_mp(self, obj):
        mp_positions = {"MP", "Member of Parliament", "member of the national assembly"}
        mp = Leader.objects.filter(
            constituency=obj,
            position__name__in=mp_positions
        ).first()
        return LeaderSerializer(mp).data if mp else None





    



class LeaderSerializer(serializers.ModelSerializer):
    position = serializers.StringRelatedField(read_only=True)
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        source="position",              
        write_only=True,
    )

    county = serializers.StringRelatedField(read_only=True)
    county_id = serializers.PrimaryKeyRelatedField(
        queryset=County.objects.all(),
        source="county",
        write_only=True,
    )

    constituency = serializers.StringRelatedField(read_only=True)
    constituency_id = serializers.PrimaryKeyRelatedField(
        queryset=Constituency.objects.all(),
        source="constituency",
        write_only=True,
        required=False,
        allow_null=True,               #
    )

    class Meta:
        model = Leader
        fields = [
            "id", "name", "party",
            "position", "position_id",
            "county", "county_id",
            "constituency", "constituency_id",
          
        ]

    def validate(self, attrs):
        
        position = attrs.get("position") or getattr(self.instance, "position", None)
        county = attrs.get("county") or getattr(self.instance, "county", None)
        constituency = (
            attrs.get("constituency")
            if "constituency" in attrs
            else getattr(self.instance, "constituency", None)
        )

        if not position or not county:
            return attrs

        pos = (position.name or "").strip().lower()
        is_mp = pos in {"mp", "member of parliament", "member of the national assembly"}

   
        if is_mp and not constituency:
            raise ValidationError({"constituency_id": "MP must have a constituency."})
        if not is_mp and constituency:
            raise ValidationError({"constituency_id": "Only MPs may be linked to a constituency."})

       
        if constituency and constituency.county_id != county.id:
            raise ValidationError({"constituency_id": "Constituency belongs to a different county."})

       
        unique_roles = {"governor", "deputy governor", "senator", "woman rep"}
        if pos in unique_roles:
            qs = Leader.objects.filter(position=position, county=county)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError({"position_id": f"{position.name} already exists for {county.name}."})

        return attrs



class CountyListSerializer(serializers.ModelSerializer):
    class Meta:
        model=County
        fields=['id','name']
        



class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'party']


class ElectionSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)

    class Meta:
        model = Election
        fields = ['id', 'location_name', 'location_type', 'position', 'election_date', 'candidates']
