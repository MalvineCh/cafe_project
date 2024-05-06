from .models import LoyaltyCard
from django.contrib.auth.models import User

def give_base_points_to_users():
    users = User.objects.all()
    for user in users:
        loyalty_card, created = LoyaltyCard.objects.get_or_create(user=user)
        if created:
            loyalty_card.points = 100
            loyalty_card.save()
