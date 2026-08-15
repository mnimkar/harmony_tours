from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import date

from tours.models import Banner, Category, Tour, TourDate

STATIC_IMG = settings.BASE_DIR / "static" / "img"


def attach_image(instance, field_name, filename):
    path = STATIC_IMG / filename
    if not path.exists():
        return
    with path.open("rb") as fh:
        getattr(instance, field_name).save(filename, File(fh), save=True)


class Command(BaseCommand):
    help = "Load sample categories, tours, dates, banners, and a demo admin user."

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123")
            self.stdout.write(self.style.SUCCESS("Created admin user admin / admin123"))

        cats = {}
        cat_defs = [
            ("group-domestic", "Domestic Tours", Category.KIND_GROUP, 1),
            ("group-international", "International Tours", Category.KIND_GROUP, 2),
            ("individual-domestic", "Domestic Tours", Category.KIND_INDIVIDUAL, 1),
            ("individual-international", "International Tours", Category.KIND_INDIVIDUAL, 2),
            ("honeymoon-tours", "Honeymoon Tours", Category.KIND_SPECIALISED, 1),
            ("jungle-camp", "Jungle Camp", Category.KIND_SPECIALISED, 2),
            ("off-beat-tours", "Off Beat Tours", Category.KIND_SPECIALISED, 3),
            ("patriotic-tours", "Patriotic Tours", Category.KIND_SPECIALISED, 4),
            ("safari", "Safari", Category.KIND_SPECIALISED, 5),
            ("spiritual-tours", "Spiritual Tours", Category.KIND_SPECIALISED, 6),
        ]
        for slug, name, kind, order in cat_defs:
            cats[slug], _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "kind": kind, "sort_order": order},
            )

        sou_itinerary = """<p><strong>Day 1: Vadodara – Garudeshwar – Neelkanthdham and stay near to Statue</strong></p>
<p>Today early in the morning proceed to Vadodara by train. After arrival at Vadodara by private coach / tempo travellers proceed to hotel near the Statue of Unity. Check in at the hotel. On the way have your lunch. After rest, visit Garudeshwar and Neelkanthdham Temple. Return back to hotel.</p>
<p><strong>Day 2: Statue of Unity sightseeing and return to Vadodara</strong></p>
<p>After breakfast check out from hotel and enjoy various activities at Statue of Unity premises. In the afternoon visit the statue and in the evening enjoy the laser show. After dinner proceed to Vadodara and check in at the hotel.</p>
<p><strong>Day 3: Vadodara local sightseeing and return to Mumbai</strong></p>
<p>After breakfast visit local sightseeing of Vadodara. After lunch, time is given for shopping. Around 03:30 we drop you at the railway station for the return journey to Mumbai.</p>
<p>Tour concludes at Vadodara Station with best memorable experience.</p>"""

        sou_includes = """<ul>
<li>2N stay in hotel at Vadodara in A/C room on double occupancy (standard package)</li>
<li>All transfers and sightseeing at Vadodara on seat-in-coach basis for the group</li>
<li>All sightseeings as mentioned in the itinerary with their entry fees</li>
<li>Breakfast, lunch and dinner during the tour (from Day 01 lunch to last day lunch)</li>
<li>Daily 1 litre sealed drinking water</li>
<li>Express entry for luxury package and normal entry for standard package</li>
</ul>"""

        sou_excludes = """<ul>
<li>Anything not mentioned in inclusions</li>
<li>Travel from Mumbai to Vadodara by railway / bus / air</li>
<li>GST 5% on the total package cost</li>
<li>Personal expenses, additional sightseeing, extra meals and water</li>
<li>Travel insurance and last-minute changes due to weather or government norms</li>
</ul>"""

        tours_data = [
            {
                "slug": "flag-hoisting-tour-3n",
                "title": "Flag Hoisting Tour 3N",
                "category": "patriotic-tours",
                "destination": "Delhi",
                "duration_label": "3N",
                "nights": 3,
                "short_description": "Flag Hoisting Tour 3N — patriotic Delhi experience.",
                "image": "republic.jpg",
                "featured": True,
                "sort": 1,
            },
            {
                "slug": "swatantryaveer-vandan-yatra-andaman-6n",
                "title": "Swatantryaveer Vandan Yatra, Andaman (6N)",
                "category": "group-domestic",
                "destination": "Andaman",
                "duration_label": "6N",
                "nights": 6,
                "short_description": "स्वातंत्र्यवीर वंदन यात्रा, अंदमान (6N)",
                "image": "andaman.jpg",
                "featured": True,
                "sort": 2,
            },
            {
                "slug": "statue-of-unity-2n",
                "title": "Statue Of Unity (2N)",
                "category": "group-domestic",
                "destination": "Gujarat",
                "duration_label": "2N",
                "nights": 2,
                "short_description": "Statue Of Unity (2N) group tour from Vadodara.",
                "image": "sou.jpg",
                "featured": True,
                "sort": 3,
                "itinerary": sou_itinerary,
                "includes": sou_includes,
                "excludes": sou_excludes,
                "notes": "We also provide luxury packages with tent city stay. For details contact 9820692614.",
                "offers": "<p>Group booking discount is available for more than 08 adults on double sharing. Repeated guests get additional benefit. Only one offer can be availed.</p>",
                "dates": [date(2026, 10, 2), date(2026, 11, 14), date(2027, 1, 26)],
            },
            {
                "slug": "rann-of-kutch-2n",
                "title": "Rann Of Kutch (2N)",
                "category": "group-domestic",
                "destination": "Gujarat",
                "duration_label": "2N",
                "nights": 2,
                "short_description": "Rann Of Kutch (2N) white desert experience.",
                "image": "rann.jpg",
                "featured": True,
                "sort": 4,
                "dates": [date(2026, 12, 20), date(2027, 1, 10)],
            },
            {
                "slug": "bhutan-07n-08d",
                "title": "Bhutan (07 N / 08 D)",
                "category": "group-international",
                "destination": "Bhutan",
                "duration_label": "07 N / 08 D",
                "nights": 7,
                "short_description": "Bhutan group tour — 07 nights / 08 days.",
                "image": "bhutan.jpg",
                "featured": True,
                "sort": 5,
                "dates": [date(2026, 9, 15), date(2026, 10, 12)],
            },
            {
                "slug": "kashmir-07n-08d",
                "title": "Kashmir (07 N / 08 D)",
                "category": "group-domestic",
                "destination": "Kashmir",
                "duration_label": "07 N / 08 D",
                "nights": 7,
                "short_description": "Kashmir (07 N / 08 D) group holiday.",
                "image": "kashmir.jpg",
                "featured": True,
                "sort": 6,
                "dates": [date(2026, 9, 20)],
            },
            {
                "slug": "rustic-ladakh-08n-9d",
                "title": "Rustic Ladakh (08 N / 9 D)",
                "category": "group-domestic",
                "destination": "Leh-Ladakh",
                "duration_label": "08 N / 9 D",
                "nights": 8,
                "short_description": "Rustic Ladakh (08N / 9D).",
                "image": "ladakh.jpg",
                "featured": True,
                "sort": 7,
                "dates": [date(2026, 8, 25), date(2026, 9, 8)],
            },
            {
                "slug": "kanha-wilderness",
                "title": "Kanha Wilderness",
                "category": "safari",
                "destination": "Madhya Pradesh",
                "duration_label": "Safari",
                "short_description": "Kanha jungle safari excursion.",
                "image": "kanha.jpg",
                "latest": True,
                "sort": 8,
            },
        ]

        extra_tours = [
            ("andaman-tour-5n", "Andaman Tour (5N)", "group-domestic", "Andaman", "5N", 5),
            ("essence-of-sikkim-07", "Essence of Sikkim (07)", "group-domestic", "Sikkim", "07 N", 7),
            ("best-of-sikkim-05n", "Best of Sikkim (05 N)", "group-domestic", "Sikkim", "05 N", 5),
            ("kaas-plateau-of-flowers", "Kaas: Plateau of flowers", "group-domestic", "Maharashtra", "Day trip", 0),
            ("kaas-plateau-1n", "Kaas: Plateau of flowers (1N)", "group-domestic", "Maharashtra", "1N", 1),
            ("lonar-crater", "Lonar Crater", "group-domestic", "Maharashtra", "2N", 2),
            ("mix-match-rajasthan-10n", "Mix Match Rajasthan (10N)", "group-domestic", "Rajasthan", "10N", 10),
            ("saurashtra-05n", "Saurashtra (05N)", "group-domestic", "Saurashtra", "05N", 5),
            ("highlights-of-sikkim-06n", "Highlights of Sikkim (06 N)", "group-domestic", "Sikkim", "06 N", 6),
            ("north-east-wonderer-7n", "North East Wonderer (7N)", "group-domestic", "Assam", "7N", 7),
            ("dubai-tour-4n-group", "Dubai Tour (4N)", "group-international", "Dubai", "4N", 4),
            ("sri-lanka-tour-7n", "Sri Lanka Tour (7N)", "group-international", "Sri Lanka", "7N", 7),
            ("highlights-of-indonesia", "Highlights of Indonesia", "group-international", "Indonesia", "5N", 5),
            ("himachal-the-snow-gateway", "Himachal the snow gateway", "individual-domestic", "Himachal Pradesh", "", None),
            ("karnataka-outlook-9n", "Karnataka Outlook (9N)", "individual-domestic", "Karnataka", "9N", 9),
            ("le-tour-de-coffee-capital", "Le tour de Coffee Capital", "individual-domestic", "Karnataka", "", None),
            ("full-of-kashmir", "Full of Kashmir", "individual-domestic", "Kashmir", "", None),
            ("saffron-valley-kashmir", "Saffron Valley Kashmir", "individual-domestic", "Kashmir", "", None),
            ("splendid-kerala-5n", "Splendid Kerala (5N)", "individual-domestic", "Kerala", "5N", 5),
            ("offbeat-kerala", "Offbeat Kerala", "individual-domestic", "Kerala", "", None),
            ("glimpse-of-uttarakhand-5n", "Glimpse of Uttarakhand (5N)", "individual-domestic", "Uttarakhand", "5N", 5),
            ("hills-of-uttarakhand", "Hills of Uttarakhand", "individual-domestic", "Uttarakhand", "", None),
            ("splendours-of-north", "Splendours of North", "individual-domestic", "Himachal Pradesh", "", None),
            ("andaman-explorers", "Andaman Explorers", "individual-domestic", "Andaman", "", None),
            ("royal-mewad-7n", "Royal Mewad (7N)", "individual-domestic", "Rajasthan", "7N", 7),
            ("sikkim-delight", "Sikkim Delight", "individual-domestic", "Sikkim", "", None),
            ("dubai-tour-4n", "Dubai Tour 4N", "individual-international", "Dubai", "4N", 4),
            ("indonesia-5n", "Indonesia 5N", "individual-international", "Indonesia", "5N", 5),
            ("lankan-image", "Lankan Image", "individual-international", "Sri Lanka", "", None),
            ("lankan-leisure-7n", "Lankan Leisure 7N", "individual-international", "Sri Lanka", "7N", 7),
            ("rustic-bhutan-tour-6n", "Rustic Bhutan Tour 6N", "individual-international", "Bhutan", "6N", 6),
            ("singapore-delights-4n", "Singapore Delights 4N", "individual-international", "Singapore", "4N", 4),
            ("himachal-beat-the-routine-package", "Himachal Beat The Routine Package", "honeymoon-tours", "Himachal Pradesh", "", None),
            ("himachal-shimla-kullu-manali-chandigarh", "Himachal – Shimla Kullu Manali Chandigarh", "honeymoon-tours", "Himachal Pradesh", "", None),
            ("indonesia-honeymoon-package", "Indonesia Honeymoon Package", "honeymoon-tours", "Indonesia", "", None),
            ("kodai-honeymoon-tour", "Kodai Honeymoon Tour", "honeymoon-tours", "Kodai", "", None),
            ("diwali-vacation-camp", "Diwali Vacation Camp", "jungle-camp", "", "", None),
            ("himachal-beat-the-routine", "Himachal Beat The Routine", "off-beat-tours", "Himachal Pradesh", "", None),
            ("offbeat-andaman", "Offbeat Andaman", "off-beat-tours", "Andaman", "", None),
            ("offbeat-kerala-5n", "Offbeat Kerala 5N", "off-beat-tours", "Kerala", "5N", 5),
            ("marwar-with-border-tourism-6n", "Marwar with Border Tourism 6N", "patriotic-tours", "Rajasthan", "6N", 6),
            ("rajasthan-wilderness-4n", "Rajasthan Wilderness 4N", "safari", "Rajasthan", "4N", 4),
            ("konkan-turtle-festival", "Konkan Turtle Festival", "safari", "Maharashtra", "", None),
            ("sri-lanka-tour-8n-9d", "Sri Lanka Tour (8N/9D)", "spiritual-tours", "Sri Lanka", "8N / 9D", 8),
            ("bhagwat-saptah-at-dwarika-12n", "Bhagwat Saptah at Dwarika 12N", "spiritual-tours", "Gujarat", "12N", 12),
        ]

        created = 0
        for item in tours_data:
            tour, was_created = Tour.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "category": cats[item["category"]],
                    "title": item["title"],
                    "destination": item.get("destination", ""),
                    "duration_label": item.get("duration_label", ""),
                    "nights": item.get("nights"),
                    "short_description": item.get("short_description", ""),
                    "itinerary": item.get("itinerary", ""),
                    "cost_includes": item.get("includes", ""),
                    "cost_excludes": item.get("excludes", ""),
                    "offers": item.get("offers", ""),
                    "notes": item.get("notes", ""),
                    "is_featured": item.get("featured", False),
                    "is_latest_excursion": item.get("latest", False),
                    "is_published": True,
                    "sort_order": item.get("sort", 0),
                },
            )
            if item.get("image") and (was_created or not tour.image):
                attach_image(tour, "image", item["image"])
            if item.get("dates"):
                for d in item["dates"]:
                    TourDate.objects.get_or_create(
                        tour=tour, start_date=d, defaults={"is_active": True}
                    )
            created += 1

        for slug, title, cat, dest, dur, nights in extra_tours:
            Tour.objects.update_or_create(
                slug=slug,
                defaults={
                    "category": cats[cat],
                    "title": title,
                    "destination": dest,
                    "duration_label": dur,
                    "nights": nights if nights else None,
                    "short_description": title,
                    "is_published": True,
                    "sort_order": 50,
                },
            )
            created += 1

        banners = [
            ("Republic Day", "banner-republic.jpg"),
            ("Dubai", "banner-dubai.jpg"),
            ("Bhutan", "banner-bhutan.jpg"),
        ]
        for i, (title, filename) in enumerate(banners, start=1):
            banner, made = Banner.objects.update_or_create(
                title=title, defaults={"sort_order": i, "is_active": True}
            )
            if made or not banner.image:
                attach_image(banner, "image", filename)

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} tours, categories, dates and banners."))
