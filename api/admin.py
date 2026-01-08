from django.contrib import admin
from .forms import ItemAdminForm, BidAdminForm
from .models import Item, Bid, Question, Reply


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
	form = ItemAdminForm
	list_display = ("id", "title", "owner", "starting_price", "ends_at", "created_at")
	search_fields = ("title", "description")
	list_filter = ("ends_at", "created_at")


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
	form = BidAdminForm
	list_display = ("id", "item", "bidder", "amount", "created_at")
	list_filter = ("created_at",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ("id", "item", "author", "created_at")
	search_fields = ("content",)


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
	list_display = ("id", "question", "author", "created_at")
	search_fields = ("content",)
