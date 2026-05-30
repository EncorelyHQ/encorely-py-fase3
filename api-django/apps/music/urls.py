from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SongViewSet, SwipeCreateView, MySwipesView

router = DefaultRouter()
router.register(r'songs', SongViewSet, basename='song')

urlpatterns = [
    path('', include(router.urls)),
    path('swipes/', SwipeCreateView.as_view(), name='swipe-create'),
    path('swipes/my/', MySwipesView.as_view(), name='my-swipes'),
]
