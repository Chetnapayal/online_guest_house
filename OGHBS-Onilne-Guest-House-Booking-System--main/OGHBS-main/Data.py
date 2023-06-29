from app import db
from app import User
from app import Rooms
from app import FoodOptions
from app import GuestHouse


st = ""
for i in range(100):
    st += "0"

rooms = [Rooms(id=1, floor=0, type="D/B AC Rooms", description="Double Bed", status=st, ghId=1, pricePerDay=1000, occupancy=2, ac=1),
            Rooms(id=2, floor=0, type="D/B NON AC Rooms", description="Double Bed", status=st, ghId=1, pricePerDay=800, occupancy=2, ac=0),
            Rooms(id=3, floor=1, type="Suite Rooms", description="Single Bed", status=st, ghId=1, pricePerDay=2000, occupancy=2, ac=0),
            Rooms(id=4, floor=2, type="Meeting Room", description="", status=st, ghId=1, pricePerDay=5000, occupancy=10, ac=1),
            Rooms(id=5, floor=0, type="D/B AC Rooms", description="Double Bed", status=st, ghId=2, pricePerDay=600, occupancy=3, ac=1),
            Rooms(id=6, floor=0, type="D/B Non AC Rooms", description="Double Bed", status=st, ghId=2, pricePerDay=400, occupancy=3, ac=0),
            Rooms(id=7, floor=2, type="Dormitory Beds AC", description="Single Bed", status=st, ghId=2, pricePerDay=250, occupancy=1, ac=1)]

for i in rooms:
    db.session.add(i)
    db.session.commit()

houses = [GuestHouse(id=1, address="IIT Kharagpur, Kharagpur 721302", description="Technology Guest House"),
          GuestHouse(id=2, address="IIT Kharagpur, Kharagpur 721302", description="Visveswaraya Guest House"),
          GuestHouse(id=3, address="HC Block, Sector – III Salt Lake City Kolkata – 700106", description="Kolkata Guest House")]

for i in houses:
    db.session.add(i)
    db.session.commit()

foods = [FoodOptions(id=1, pricePerDay=200, type='North Indian Veg'),
         FoodOptions(id=2, pricePerDay=300, type='North Indian Non-Veg'),
         FoodOptions(id=3, pricePerDay=250, type='South Indian Veg'),
         FoodOptions(id=4, pricePerDay=350, type='Chinese'),
         FoodOptions(id=5, pricePerDay=350, type='Italian'),
         FoodOptions(id=6, pricePerDay=300, type='KGP Special')]

for i in foods:
    db.session.add(i)
    db.session.commit()

admin = User(id=0, name="admin", username="admin", password="admin", address="", age=21, gender="Male", rollStd="")
db.session.add(admin)
db.session.commit()

