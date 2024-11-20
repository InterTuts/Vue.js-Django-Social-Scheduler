# System Utils
from django.core.management.base import BaseCommand
from django.utils import timezone

# App Utils
from posts.cache import CacheManager
from posts.models import PostsModel
from posts.views import CreatePost
from posts.utils import NetworkObj, PostObj

class Command(BaseCommand):
    """
    Publish the scheduled posts
    """
    help = 'Publish the scheduled posts'

    def handle(self, *args, **kwargs):

        # Get current server time by timezone
        now = timezone.now()

        # Get scheduled posts which should be published
        posts = PostsModel.objects.filter(created_at__lt=now, scheduled=True).prefetch_related(
            'postsnetworksmodel_set__network'
        )

        # Check if posts exists
        if posts.exists():

            # List the posts
            for post in posts:

                # Cancel the scheduled status
                post.scheduled = False

                # Publish count
                publish_count = 0

                # Lists the social accounts
                for posts_network in post.postsnetworksmodel_set.all():

                    # Network data
                    network_obj = NetworkObj(posts_network.network.network_name, posts_network.network.net_id, posts_network.network.name, posts_network.network.token, posts_network.network.secret)

                    # Posts data
                    post_obj = PostObj(post.text, post.image)

                    # Set post and account's data
                    post_create = CreatePost(post_obj, network_obj)

                    # Publish post
                    publish = post_create.create_post()

                    # Check if the post was published
                    if publish['success']:
                        publish_count+=1

                # Check if the post was published at least in one account
                if publish_count > 0:
                    post.published = False

            # Update the scheduled status
            PostsModel.objects.bulk_update(posts, ['published', 'scheduled'])

            # Create a cache manager instance
            cache_manager = CacheManager(user_id=post.user.id)

            # Clear all user's cached pages
            cache_manager.clear_cache()