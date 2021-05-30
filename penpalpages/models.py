from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    first = models.CharField(max_length=200, blank=True, null=True)
    last = models.CharField(max_length=200, null=True, blank=True)
    photo = models.ImageField(default="user.png", upload_to="photos/%Y/%m", blank=True, null=True)
    friends = models.ManyToManyField("self", blank=True)
    speaks = models.CharField(max_length=200, blank=True, null=True)
    is_learning = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse("penpalpages:profile", kwargs={"profile_id": self.pk})

    class Meta:
        ordering = ["-id"]


# Creating signals
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        print("Profile Created Successfully")


post_save.connect(receiver=create_profile, sender=User)


class FriendRequest(models.Model):
    to_profile = models.ForeignKey(Profile, related_name="to_profile", on_delete=models.CASCADE)
    from_profile = models.ForeignKey(Profile, related_name="coming_from_profile", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    # String representation of this class
    def __str__(self):
        return f'From {self.from_profile.user.username} to {self.to_profile.user.username}'