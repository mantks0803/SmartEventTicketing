from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint


class UserType(models.TextChoices):
    CUSTOMER = 'CUSTOMER', 'Customer'
    ORGANIZER = 'ORGANIZER', 'Organizer'
    ADMIN = 'ADMIN', 'Admin'

class CustomerTierEnum(models.TextChoices):
    MEMBER = 'MEMBER', 'Member'
    VIP = 'VIP', 'VIP'
    VVIP = 'VVIP', 'VVIP'

class EventStatusEnum(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PUBLISHED = 'PUBLISHED', 'Published'
    CANCELLED = 'CANCELLED', 'Cancelled'

class EventCategoryEnum(models.TextChoices):
    MUSIC = 'MUSIC', 'Music'
    WORKSHOP = 'WORKSHOP', 'Workshop'
    ENTERTAINMENT = 'ENTERTAINMENT', 'Entertainment'

class SeatStatusEnum(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    LOCKED = 'LOCKED', 'Locked'
    SOLD = 'SOLD', 'Sold'

class OrderStatusEnum(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PAID = 'PAID', 'Paid'
    FAILED = 'FAILED', 'Failed'



class User(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    status = models.BooleanField(default=True) # Ràng buộc default True
    avatar = models.URLField(max_length=500, default="https://default-avatar.com/user.png") # Ràng buộc default ảnh
    dob = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=50, choices=UserType.choices)

    def __str__(self):
        return f"{self.username} ({self.type})"

class Customer(models.Model):
    # Dùng OneToOneField và primary_key=True để triển khai cơ chế kế thừa đa hình kế thừa từ bảng User
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='customer_profile')
    tier = models.CharField(max_length=20, choices=CustomerTierEnum.choices, default=CustomerTierEnum.MEMBER)

class Organizer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='organizer_profile')
    company_name = models.CharField(max_length=250)
    bank_account = models.CharField(max_length=100)

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='admin_profile')
    access_level = models.IntegerField(default=1)



class Event(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    thumbnail = models.URLField(max_length=500)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    category = models.CharField(max_length=50, choices=EventCategoryEnum.choices, default=EventCategoryEnum.MUSIC)
    status = models.CharField(max_length=50, choices=EventStatusEnum.choices, default=EventStatusEnum.PENDING)
    is_payout_completed = models.BooleanField(default=False)

class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=50) # VIP, Standard, Early Bird
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = models.IntegerField()

    class Meta:
        constraints = [
            CheckConstraint(condition=Q(price__gte=0), name='tickettype_price_gte_0'),
            CheckConstraint(condition=Q(total_quantity__gte=0), name='tickettype_total_quantity_gte_0'),
        ]

class Seat(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='seats')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='seats')
    seat_name = models.CharField(max_length=100) # Tên ghế: ví dụ A1, B5
    status = models.CharField(max_length=50, choices=SeatStatusEnum.choices, default=SeatStatusEnum.AVAILABLE)
    locked_until = models.DateTimeField(null=True, blank=True) # Phục vụ nghiệp vụ khóa ghế 10 phút thanh toán

    class Meta:
        constraints = [
            UniqueConstraint(fields=['event', 'seat_name'], name='unique_seat_per_event')
        ]



class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=OrderStatusEnum.choices, default=OrderStatusEnum.PENDING)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)     
class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets')
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE, related_name='ticket')
    ticket_code = models.CharField(max_length=100, unique=True)
    is_checked_in = models.BooleanField(default=False)


class KnowledgeBase(models.Model):
    content = models.TextField() 
  
    embedding = models.TextField(null=True, blank=True) 

class ChatSession(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='chat_sessions')
    summary = models.TextField(null=True, blank=True) # Lưu trữ bản tóm tắt hội thoại để AI nhớ ngữ cảnh
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=[('USER', 'User'), ('AI', 'AI')])
    raw_input = models.TextField()   
    clean_input = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)