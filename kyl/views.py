from rest_framework import viewsets,generics,filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Leader, County, Constituency,Position,Role,Election,Candidate
from .serializers import (
    LeaderSerializer, 
    CountySerializer, 
    ConstituencySerializer
    ,CountyListSerializer,
    PositionSerializer,ElectionSerializer, CandidateSerializer)





class PositionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows positions and their roles to be viewed/edited.
    """
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    lookup_field="name"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "roles__title", "roles__description"]
    ordering_fields = ["name", "id"]
    ordering = ["name"]




class SearchViewSet(viewsets.ViewSet):
    """
    A single entry point for searching leaders, counties, or constituencies.
    """

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response({"error": "Please provide a search query."}, status=400)

        county = County.objects.filter(name__icontains=query).first()
        if county:
            county_data = CountySerializer(county).data
            return Response({"type": "county", "data": county_data})

        constituency = Constituency.objects.filter(name__icontains=query).first()
        if constituency:
            constituency_data = ConstituencySerializer(constituency).data
            return Response({"type": "constituency", "data": constituency_data})

        leader = Leader.objects.filter(
            Q(name__icontains=query) | Q(party__icontains=query)
        ).first()
        if leader:
            leader_data = LeaderSerializer(leader).data
            return Response({"type": "leader", "data": leader_data})

     
        return Response({"message": "No results found for your query."}, status=404)
    

class CountyListView(generics.ListAPIView):
    queryset = County.objects.all()
    serializer_class = CountyListSerializer


class CountyDetailView(generics.RetrieveAPIView):
    queryset = County.objects.all()
    serializer_class = CountySerializer
    lookup_field = "id"  



class ElectionViewSet(viewsets.ModelViewSet):
    queryset = Election.objects.all().order_by('-election_date')
    serializer_class = ElectionSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
