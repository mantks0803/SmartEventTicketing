import os
import django
from datetime import timedelta
from django.utils import timezone

# 1. Cấu hình môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from authentication.models import User, Organizer, UserType
from events.models import Event, TicketType, EventCategoryEnum, EventStatusEnum
from seating.models import Seat, SeatStatusEnum

def run_seed():
    print("🚀 Bắt đầu quá trình nạp 30 dữ liệu mẫu...")

    # 2. Khởi tạo / Cập nhật tài khoản Organizer
    user, created = User.objects.get_or_create(
        username='demo_organizer',
        defaults={
            'email': 'organizer@smartevent.vn',
            'name': 'Nguyễn Thanh Mẫn',
            'phone_number': '0909123456',
            'type': UserType.ORGANIZER,
            'status': True,
            'avatar': 'https://res.cloudinary.com/dmhnfoc9i/image/upload/v1777361181/tickethub_avatars/btsrovtumjgqlaharj2r.jpg'
        }
    )
    if created or not user.check_password('123456'):
        user.set_password('123456')
        user.save()

    organizer, _ = Organizer.objects.get_or_create(
        user=user,
        defaults={
            'company_name': 'Công ty TNHH Truyền thông & Sự kiện SmartTicket',
            'bank_account': '1903123456789 - Techcombank - NGUYEN THANH MAN'
        }
    )

    # 3. Danh sách 10 thumbnail Unsplash
    unsplash_images = [
        'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800&auto=format&fit=crop'
    ]

    # 4. Danh sách 4 thumbnail Cloudinary
    cloudinary_images = [
        'https://res.cloudinary.com/dmhnfoc9i/image/upload/v1777361181/tickethub_avatars/btsrovtumjgqlaharj2r.jpg',
        'https://res.cloudinary.com/dmhnfoc9i/image/upload/v1774104712/2_lupigx.jpg',
        'https://res.cloudinary.com/dmhnfoc9i/image/upload/v1774104712/1_lnmafr.jpg',
        'https://res.cloudinary.com/dmhnfoc9i/image/upload/v1786006162/photo-1587825140708-dfaf72ae4b04_mxmqrx.avif'
    ]

    # 5. Danh sách 30 dữ liệu sự kiện
    locations = [
        'Nhà hát Hòa Bình, Quận 10, TP.HCM',
        'GEM Center, Quận 1, TP.HCM',
        'Sân vận động Quân khu 7, Tân Bình, TP.HCM',
        'Nhà thi đấu Phú Thọ, Quận 11, TP.HCM',
        'Công viên Tao Đàn, Quận 1, TP.HCM',
        'Sân khấu kịch IDECAF, Quận 1, TP.HCM'
    ]

    categories = [
        EventCategoryEnum.MUSIC,
        EventCategoryEnum.WORKSHOP,
        EventCategoryEnum.SPORTS,
        EventCategoryEnum.ENTERTAINMENT
    ]

    now = timezone.now()

    for i in range(1, 31):
        # 10 sự kiện đầu lấy Unsplash, 20 sự kiện sau lặp lại 4 link Cloudinary
        if i <= 10:
            thumb = unsplash_images[i - 1]
        else:
            thumb = cloudinary_images[(i - 11) % len(cloudinary_images)]

        cat = categories[(i - 1) % len(categories)]
        loc = locations[(i - 1) % len(locations)]

        title = f"Sự kiện #{i:02d}: {cat.label} - Trải nghiệm Đặc biệt 2026"
        description = f"Mô tả chi tiết cho sự kiện số {i}. Quy tụ dàn khách mời hấp dẫn, không gian chuyên nghiệp và trải nghiệm tuyệt vời dành cho người tham dự tại {loc}."
        start_time = now + timedelta(days=i * 2, hours=(i % 12) + 8)

        event, created = Event.objects.get_or_create(
            title=title,
            defaults={
                'organizer': organizer,
                'thumbnail': thumb,
                'description': description,
                'location': loc,
                'start_time': start_time,
                'category': cat,
                'status': EventStatusEnum.PUBLISHED
            }
        )

        if created:
            # Tạo 2 loại vé cho mỗi sự kiện
            vips_price = 500000 + (i * 20000)
            std_price = 200000 + (i * 10000)

            # Hạng VIP (2 hàng x 5 ghế = 10 ghế)
            tt_vip = TicketType.objects.create(
                event=event,
                name='Hạng VIP',
                price=vips_price,
                quantity=10
            )
            seats_vip = [
                Seat(
                    event=event,
                    ticket_type=tt_vip,
                    row=f"VIP{r+1}",
                    number=n,
                    seat_name=f"VIP{r+1}-{n}",
                    status=SeatStatusEnum.AVAILABLE
                )
                for r in range(2) for n in range(1, 6)
            ]
            Seat.objects.bulk_create(seats_vip)

            # Hạng Standard (3 hàng x 5 ghế = 15 ghế)
            tt_std = TicketType.objects.create(
                event=event,
                name='Hạng Phổ Thông',
                price=std_price,
                quantity=15
            )
            seats_std = [
                Seat(
                    event=event,
                    ticket_type=tt_std,
                    row=f"STD{r+1}",
                    number=n,
                    seat_name=f"STD{r+1}-{n}",
                    status=SeatStatusEnum.AVAILABLE
                )
                for r in range(3) for n in range(1, 6)
            ]
            Seat.objects.bulk_create(seats_std)

            print(f"  + [{i:02d}/30] Đã tạo thành công: {title}")

    print("\n✅ TẤT CẢ 30 SỰ KIỆN VÀ TÀI KHOẢN ORGANIZER ĐÃ ĐƯỢC KHỞI TẠO XONG!")


if __name__ == '__main__':
    run_seed()