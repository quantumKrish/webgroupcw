"""
Quick script to seed test data for auction app.
Run: python seed_test_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Item, Bid, Question, Reply
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def seed():
    print("Seeding test data...")
    
    # Get or create test users
    user1, created = User.objects.get_or_create(
        username='krish',
        defaults={'email': 'krish@example.com', 'is_staff': True, 'is_superuser': True}
    )
    if created:
        user1.set_password('password123')
        user1.save()
        print(f"✓ Created user: {user1.username}")
    else:
        print(f"✓ User exists: {user1.username}")
    
    user2, created = User.objects.get_or_create(
        username='testbuyer',
        defaults={'email': 'buyer@example.com'}
    )
    if created:
        user2.set_password('password123')
        user2.save()
        print(f"✓ Created user: {user2.username}")
    
    # Create test items
    items_data = [
        {
            'title': 'Vintage Camera',
            'description': 'Classic 35mm film camera in excellent condition',
            'starting_price': 50.00,
            'image_url': 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=400',
            'days_until_end': 2,
        },
        {
            'title': 'Gaming Laptop',
            'description': 'High-performance gaming laptop, RTX 3070, 16GB RAM',
            'starting_price': 800.00,
            'image_url': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400',
            'days_until_end': 5,
        },
        {
            'title': 'Antique Watch',
            'description': 'Rare pocket watch from the 1920s',
            'starting_price': 200.00,
            'image_url': 'https://images.unsplash.com/photo-1509048191080-d2984bad6ae5?w=400',
            'days_until_end': 1,
        },
    ]
    
    created_items = []
    for item_data in items_data:
        item, created = Item.objects.get_or_create(
            title=item_data['title'],
            defaults={
                'owner': user1,
                'description': item_data['description'],
                'starting_price': item_data['starting_price'],
                'image_url': item_data['image_url'],
                'ends_at': timezone.now() + timedelta(days=item_data['days_until_end']),
            }
        )
        if created:
            print(f"✓ Created item: {item.title}")
            created_items.append(item)
        else:
            print(f"✓ Item exists: {item.title}")
            created_items.append(item)
    
    # Create some test bids
    if len(created_items) > 0:
        item = created_items[0]
        bid, created = Bid.objects.get_or_create(
            item=item,
            bidder=user2,
            defaults={'amount': item.starting_price + 10}
        )
        if created:
            print(f"✓ Created bid: ${bid.amount} on {item.title}")
    
    # Create a test question
    if len(created_items) > 0:
        item = created_items[0]
        q, created = Question.objects.get_or_create(
            item=item,
            author=user2,
            defaults={'content': 'Is this camera still working?'}
        )
        if created:
            print(f"✓ Created question on {item.title}")
            
            # Reply
            reply, created = Reply.objects.get_or_create(
                question=q,
                author=user1,
                defaults={'content': 'Yes, it works perfectly!'}
            )
            if created:
                print(f"✓ Created reply to question")
    
    print("\nTest data seeded successfully!")
    print(f"Total items: {Item.objects.count()}")
    print(f"Total bids: {Bid.objects.count()}")
    print(f"Total questions: {Question.objects.count()}")

if __name__ == '__main__':
    seed()
