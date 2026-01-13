from django.core.management.base import BaseCommand
from django.utils import timezone

from api.views import send_winner_email
from api.models import Item


class Command(BaseCommand):
    help = "Check ended auctions and notify winners"

    def handle(self, *args, **options) -> None:
        # Get auctions that have ended
        ended_items = Item.objects.filter(
            ends_at__lte=timezone.now(),
            winner_email_sent=False
        )

        # Iterate through ended auctions
        for item in ended_items:
            # Get the highest bid for the item
            winning_bid = item.bids.order_by("-amount").first()

            # If there is a winning bid, send the winner an email
            if winning_bid:
                send_winner_email(
                    winning_bid.bidder.email,
                    item.title,
                )

            # Mark the item as closed
            item.winner_email_sent = True
            item.save()

            # Optional: Log that an auction was closed
            self.stdout.write(self.style.SUCCESS(f"Closed auction: {item.title}"))
