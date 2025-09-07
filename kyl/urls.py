from django.urls import path,include
from .views import SearchViewSet, CountyListView, CountyDetailView,PositionViewSet,CandidateViewSet,ElectionViewSet
from rest_framework.routers import DefaultRouter


search = SearchViewSet.as_view({"get": "search"})

router = DefaultRouter()
router.register(r"positions", PositionViewSet, basename="position")
router.register(r'elections', ElectionViewSet)
router.register(r'candidates', CandidateViewSet)

urlpatterns = [
    path("search/", search, name="search"),
    path("counties/", CountyListView.as_view(), name="county-lists"),
    path("counties/<int:id>/", CountyDetailView.as_view(), name="county-detail"),
 
    path("", include(router.urls)),
]
