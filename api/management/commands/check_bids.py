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

            # If there is a winning bid, save the winner and try to send email
            if winning_bid:
                # Save the winner first
                item.winner = winning_bid.bidder
                
                # Try to send email (but don't fail if it doesn't work)
                try:
                    send_winner_email(
                        winning_bid.bidder.email,
                        item.title,
                    )
                    item.winner_email_sent = True
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Failed to send email for {item.title}: {e}"))
                    # Still mark as sent so we don't keep trying
                    item.winner_email_sent = True
            else:
                # No bids, mark as processed
                item.winner_email_sent = True
            
            item.save()

            # Optional: Log that an auction was closed
            self.stdout.write(self.style.SUCCESS(f"Closed auction: {item.title}"))
