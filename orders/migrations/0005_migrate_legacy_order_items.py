from datetime import timedelta

from django.db import migrations
from django.utils import timezone


def migrate_legacy_orders(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    OrderItem = apps.get_model('orders', 'OrderItem')
    Ticket = apps.get_model('orders', 'Ticket')
    Seat = apps.get_model('seating', 'Seat')

    tickets = Ticket.objects.select_related('order', 'seat', 'ticket_type').all()
    for ticket in tickets.iterator():
        OrderItem.objects.get_or_create(
            order_id=ticket.order_id,
            seat_id=ticket.seat_id,
            defaults={
                'ticket_type_id': ticket.ticket_type_id,
                'unit_price': ticket.ticket_type.price,
            },
        )

    pending_orders = Order.objects.filter(status='PENDING')
    for order in pending_orders.iterator():
        item_seat_ids = list(
            OrderItem.objects.filter(order_id=order.id).values_list('seat_id', flat=True)
        )
        locked_until_values = list(
            Seat.objects.filter(
                id__in=item_seat_ids,
                locked_until__isnull=False,
            ).values_list('locked_until', flat=True)
        )

        expires_at = max(locked_until_values) if locked_until_values else order.created_at + timedelta(minutes=10)
        order.expires_at = expires_at
        order.save(update_fields=['expires_at'])

        Seat.objects.filter(
            id__in=item_seat_ids,
            status='LOCKED',
        ).update(
            locked_by_order_id=order.id,
            locked_until=expires_at,
        )

    Ticket.objects.filter(order__status__in=['PENDING', 'CANCELLED', 'EXPIRED']).delete()

    now = timezone.now()
    Seat.objects.filter(
        status='LOCKED',
        locked_by_order__isnull=True,
        locked_until__lte=now,
    ).update(
        status='AVAILABLE',
        locked_until=None,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_expires_at_order_updated_at_payment_updated_at_and_more'),
        ('seating', '0004_seat_locked_by_order_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_legacy_orders, migrations.RunPython.noop),
    ]
