from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    def __str__(self) -> str:
        return f"Profile of {self.user.username}"


class PageView(models.Model):
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"Page view count: {self.count}"


class Item(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=12, decimal_places=2)
    image_url = models.URLField(blank=True)  # Legacy field, keeping for compatibility
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} (owner={self.owner_id})"

    @property
    def current_price(self):
        top = self.bids.order_by("-amount").first()
        return top.amount if top else self.starting_price


class Bid(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Bid {self.amount} on {self.item_id} by {self.bidder_id}"


class Question(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="questions")
    asker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    content = models.TextField()  # Changed from 'text' to match API
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Question on {self.item_id} by {self.asker_id}"


class Reply(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")  # Changed from 'responder' to match API
    content = models.TextField()  # Changed from 'text' to match API
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Reply to question {self.question_id} by {self.responder_id}"