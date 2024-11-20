# System Utils
from django.test import TestCase

# App Utils
from authentication.models import CustomUser
from .models import PostsModel

class UserListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        # Create the administrator for data access
        user = CustomUser.objects.create_user(
            email='admin@example.com', password='password', is_staff=True
        )

    def test_create_post_creation(self):

        # New post's data
        new_post = PostsModel(
            user="17",
            text="Just Example",
            image=None
        )

        # Save the post to the database
        new_post.save()

        self.assertEqual(new_post.index, 1)