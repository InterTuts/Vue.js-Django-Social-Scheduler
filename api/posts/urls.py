# System Utils
from django.urls import path

# App Utils
from .views import CreatePostView, SchedulePostView, PostsListView, PostDetailsView, PostCancelView

# Namespace for the posts app
app_name='posts'

urlpatterns = [
    path('create', CreatePostView.as_view(), name='create_post'),
    path('schedule', SchedulePostView.as_view(), name='schedule_post'),
    path('list', PostsListView.as_view(), name='list_posts'),
    path('<int:id>', PostDetailsView.as_view(), name='read_post'),
    path('cancel/<int:id>', PostCancelView.as_view(), name='cancel_post')
]