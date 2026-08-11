import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from authentication.models import User, Organizer, UserType
from events.models import Event, TicketType, EventCategoryEnum, EventStatusEnum
from seating.models import Seat, SeatStatusEnum

def run_seed():
    print("🧹 Đang tiến hành dọn dẹp dữ liệu cũ...")
    deleted_events_count, _ = Event.objects.all().delete()
    print(f"🗑️ Đã xóa thành công {deleted_events_count} sự kiện cũ (bao gồm toàn bộ loại vé và ghế liên quan).")

    print("\n🚀 Bắt đầu quá trình nạp dữ liệu mẫu mới...")

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

    thumbnails = [
        'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800&auto=format&fit=crop',
        'https://res.cloudinary.com/dmhnfoc9i/image/upload/v1774104712/2_lupigx.jpg',
        'https://res.cloudinary.com/dmhnfoc9i/image/upload/v1774104712/1_lnmafr.jpg',
        'https://res.cloudinary.com/dmhnfoc9i/image/upload/v1786006162/photo-1587825140708-dfaf72ae4b04_mxmqrx.avif'
    ]

    venues = [
        'Nhà hát Hòa Bình, Quận 10, TP.HCM',
        'GEM Center, Quận 1, TP.HCM',
        'Sân vận động Quân khu 7, Tân Bình, TP.HCM',
        'Nhà thi đấu Phú Thọ, Quận 11, TP.HCM',
        'Công viên Tao Đàn, Quận 1, TP.HCM',
        'Sân khấu kịch IDECAF, Quận 1, TP.HCM',
        'Trung tâm Hội chợ và Triển lãm Sài Gòn (SECC), Quận 7, TP.HCM',
        'Nhà hát Thành phố (Saigon Opera House), Quận 1, TP.HCM',
        'Sân vận động Thống Nhất, Quận 10, TP.HCM',
        'Sân khấu Ca nhạc Trống Đồng, Quận 1, TP.HCM'
    ]

    events_raw = [
        # MUSIC
        (EventCategoryEnum.MUSIC, 'Đêm Nhạc Acoustic - Giai Điệu Mưa Sài Gòn', 'Đêm nhạc sống mộc mạc lắng đọng với những bản bản acoustic nhẹ nhàng trong không gian lãng mạn.'),
        (EventCategoryEnum.MUSIC, 'Sài Gòn Sunset Session - Vũ Điệu Hoàng Hôn', 'Hòa mình vào không khí âm nhạc hoàng hôn rực rỡ quy tụ dàn nghệ sĩ trẻ tài năng.'),
        (EventCategoryEnum.MUSIC, 'Đại Hội Âm Nhạc Underground - Bùng Nổ Sức Trẻ', 'Đêm nhạc Rock & Hip-hop cực sung với hệ thống âm thanh ánh sáng chuẩn quốc tế.'),
        (EventCategoryEnum.MUSIC, 'Sài Gòn Jazz Night - Giai Điệu Bất Tận', 'Thưởng thức những bản Jazz cổ điển quyến rũ được thể hiện bởi các ban nhạc hàng đầu.'),
        (EventCategoryEnum.MUSIC, 'Đêm Hòa Tấu Cổ Điển - Ánh Sáng & Khúc Ca', 'Chương trình hòa tấu nhạc cổ điển sang trọng mang lại trải nghiệm nghệ thuật đẳng cấp.'),
        (EventCategoryEnum.MUSIC, 'Indie Melody - Những Câu Chuyện Mùa Thu', 'Sân khấu âm nhạc Indie quy tụ những ca khúc tự sáng tác ngọt ngào và mộc mạc.'),
        (EventCategoryEnum.MUSIC, 'Đêm Ca Trù & Dân Ca Đương Đại - Hồn Việt', 'Sự kết hợp tinh tế giữa âm nhạc dân gian truyền thống và phối khí hiện đại.'),
        (EventCategoryEnum.MUSIC, 'Pop Ballad Concert - Lời Yêu Thương Gửi Lại', 'Đêm nhạc ballad nhẹ nhàng chạm đến cảm xúc với những tình khúc vượt thời gian.'),

        # WORKSHOP
        (EventCategoryEnum.WORKSHOP, 'Workshop Pha Chế Coffee Specialty & Latte Art', 'Trải nghiệm tự tay thực hành nghệ thuật pha chế cà phê thủ công và tạo hình Latte Art.'),
        (EventCategoryEnum.WORKSHOP, 'AI & Future Tech Summit 2026 - Kỷ Nguyên Mới', 'Hội thảo công nghệ AI lớn nhất năm với sự tham gia của các chuyên gia hàng đầu.'),
        (EventCategoryEnum.WORKSHOP, 'Hội Thảo Thiết Kế UI/UX - Xây Dựng Sản Phẩm Chuẩn', 'Chia sẻ tư duy thiết kế trải nghiệm người dùng hiện đại và thực hành dự án thực tế.'),
        (EventCategoryEnum.WORKSHOP, 'Workshop Làm Nến Thơm & Tinh Dầu Thiên Nhiên', 'Tự tay sáng tạo những hũ nến thơm mang hương vị cá nhân độc đáo để thư giãn.'),
        (EventCategoryEnum.WORKSHOP, 'Diễn Đàn Khởi Nghiệp Đổi Mới Sáng Tạo 2026', 'Nơi kết nối các Founder trẻ với nhà đầu tư và các quỹ hỗ trợ khởi nghiệp.'),
        (EventCategoryEnum.WORKSHOP, 'Hội Thảo Quản Lý Tài Chính Cá Nhân Cho Giới Trẻ', 'Tư duy tích lũy, đầu tư an toàn và lập kế hoạch tài chính tự chủ cho tuổi 20+.'),
        (EventCategoryEnum.WORKSHOP, 'Workshop Nghệ Thuật Cắm Hoa Nghệ Thuật Hiện Đại', 'Học kỹ thuật phối màu hoa và trang trí không gian sống phong cách Minimalist.'),
        (EventCategoryEnum.WORKSHOP, 'Hội Thảo Security & Cloud Computing Trends', 'Cập nhật xu hướng bảo mật điện toán đám mây và phòng chống lỗ hổng ứng dụng Web.'),

        # SPORTS
        (EventCategoryEnum.SPORTS, 'Giải Chạy Đêm Sài Gòn Midnight Marathon 2026', 'Trải nghiệm cung đường chạy đêm rực rỡ ánh đèn qua các biểu tượng lớn của thành phố.'),
        (EventCategoryEnum.SPORTS, 'Giải Đấu Cầu Lông Mở Rộng Saigon Badminton Cup', 'Tranh tài gay cấn giữa các tay vợt phong trào và bán chuyên nghiệp toàn khu vực.'),
        (EventCategoryEnum.SPORTS, 'Đại Hội Thể Thao Đường Phố & Skateboard Fest', 'Sân chơi bùng nổ năng lượng cho cộng đồng trượt ván và thể thao mạo hiểm.'),
        (EventCategoryEnum.SPORTS, 'Giải Bóng Rổ 3x3 Thành Phố Hồ Chí Minh 2026', 'Các trận đấu bóng rổ đường phố 3x3 tốc độ cao, kỹ thuật mắt mắt và sôi động.'),
        (EventCategoryEnum.SPORTS, 'Ngày Hội Yoga & Health Fest Sài Gòn', 'Chuỗi hoạt động tập luyện Yoga tập thể ngoài trời kết hợp tư vấn dinh dưỡng sạch.'),
        (EventCategoryEnum.SPORTS, 'Giải Quần Vợt Phong Trào Mở Rộng 2026', 'Giải đấu giao lưu nâng cao sức khỏe và kết nối cộng đồng doanh nhân mê Tennis.'),
        (EventCategoryEnum.SPORTS, 'Giải Đấu Esports Cúp Vô Địch Tốc Chiến 2026', 'Vòng chung kết rực lửa giữa 8 đội tuyển thể thao điện tử xuất sắc nhất.'),
        (EventCategoryEnum.SPORTS, 'Giải Đua Xe Đạp Địa Hình Sài Gòn Trail Cup', 'Thử thách sức bền và kỹ thuật điều khiển xe đạp qua các địa hình tự nhiên.'),

        # ENTERTAINMENT
        (EventCategoryEnum.ENTERTAINMENT, 'Đêm Hài Kịch - Cười Xả Stress Bờm Comedy', 'Show kịch độc thoại cực sung mang lại những phút giây thư giãn sảng khoái.'),
        (EventCategoryEnum.ENTERTAINMENT, 'Triển Lãm Nghệ Thuật Đương Đại - Khoảng Lặng', 'Không gian trưng bày các tác phẩm hội họa và mô hình sắp đặt đa giác quan.'),
        (EventCategoryEnum.ENTERTAINMENT, 'Show Diễn Xiếc Nghệ Thuật - Vũ Điệu Mặt Trời', 'Màn trình diễn xiếc uốn dẻo, đu dây và ảo thuật xiêu lòng khán giả mọi lứa tuổi.'),
        (EventCategoryEnum.ENTERTAINMENT, 'Show Nhạc Hài Độc Thoại - Góc Nhìn Đô Thị', 'Những câu chuyện đời thường góc nhìn hài hước được kể qua âm nhạc và tấu hài.'),
        (EventCategoryEnum.ENTERTAINMENT, 'Lễ Hội Ẩm Thực & Văn Hóa Đường Phố Sài Gòn', 'Quy tụ hơn 100 gian hàng ẩm thực đặc sắc cùng các hoạt động âm nhạc đường phố.'),
        (EventCategoryEnum.ENTERTAINMENT, 'Ngày Hội Cosplay & Pop Culture Expo 2026', 'Điểm hẹn giao lưu lớn nhất dành cho cộng đồng yêu thích Manga, Anime và Game.'),
        (EventCategoryEnum.ENTERTAINMENT, 'Show Kịch Tâm Lý Hồi Hộp - Dấu Vết Mơ Hồ', 'Vở kịch trinh thám kịch tính với kịch bản lôi cuốn và diễn xuất xuất sắc.'),
        (EventCategoryEnum.ENTERTAINMENT, 'Lễ Hội Phim Ngắn Độc Lập Sài Gòn 2026', 'Trình chiếu các tác phẩm điện ảnh ngắn sáng tạo từ các đạo diễn trẻ triển vọng.')
    ]

    now = timezone.now()
    created_count = 0

    for idx, (cat, title, desc) in enumerate(events_raw):
        thumb = thumbnails[idx % len(thumbnails)]
        venue = venues[idx % len(venues)]
        start_time = now + timedelta(days=(idx + 1) * 2, hours=(idx % 10) + 9)

        event = Event.objects.create(
            organizer=organizer,
            title=title,
            thumbnail=thumb,
            description=desc,
            location=venue,
            start_time=start_time,
            category=cat,
            status=EventStatusEnum.PUBLISHED
        )

        vip_price = 450000 + (idx * 25000)
        std_price = 200000 + (idx * 15000)

        tt_vip = TicketType.objects.create(
            event=event,
            name='Hạng VIP',
            price=vip_price,
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

        created_count += 1
        print(f"  + [{created_count:02d}/32] Đã tạo thành công: {title} ({venue})")

    print(f"\n✅ TỔNG KẾT: Đã xóa {deleted_events_count} sự kiện cũ và khởi tạo mới thành công {created_count} sự kiện đa dạng!")

if __name__ == '__main__':
    run_seed()