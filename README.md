# Harmony Tours (Django)

Django build of [harmonytours.in](https://travellersharmony.com/Home) with an admin section to add tours and departure dates.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_tours
python manage.py runserver
```

- Site: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

Demo admin login created by `seed_tours`: **admin** / **admin123**. Change this before any public deployment.

## Admin: tours and dates

1. Open **Tours** in Django admin.
2. Add a tour (category, title, destination, duration, itinerary, image, featured flags).
3. On the same form, use the **Tour dates** inline table to add start dates, optional end date, price and seats.
4. Featured tours appear on the homepage **Available Tours** carousel/grid. Mark **Latest excursion** to show in that homepage block.

You can also add dates from **Tour dates** as a standalone list.

## Pages

- Home, About Us, Contact
- Group / Individual / Specialised tour categories
- Tour detail (itinerary, dates, includes/excludes, enquiry form)
- Educational Tours and Inspirational Tourism

Enquiries submitted on contact or tour pages appear under **Enquiries** in admin.
