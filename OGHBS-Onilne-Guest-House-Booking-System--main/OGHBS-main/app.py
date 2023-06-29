from flask import Flask, render_template, Response, jsonify, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oghbs.db'
db = SQLAlchemy(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Global Variables

curUserId = -1
checkInDate = datetime.now()
checkOutDate = datetime.now()
srt = '0'
foodId = '0'
availableOnly = '0'
roomId = 0
rooms = []
avail = []
days = []
urls = []
roomAvail = []
emptystatus = ""
for i in range(40):
    emptystatus+="0"

# Database

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    email = db.Column(db.String(50))
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    address = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    rollStd = db.Column(db.String(20), nullable=True)
    def __repr__(self):
        return '<Name %r>' % self.id


class GuestHouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(60))
    description = db.Column(db.String(60))


class Rooms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    floor = db.Column(db.Integer)
    type = db.Column(db.String(40))
    description = db.Column(db.String(60))  # Room type, no of beds
    status = db.Column(db.String(100))
    ghId = db.Column(db.Integer)
    pricePerDay = db.Column(db.Integer)
    occupancy = db.Column(db.Integer)
    ac = db.Column(db.Integer)


class FoodOptions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pricePerDay = db.Column(db.Integer)
    type = db.Column(db.String(40))


class BookingQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookingIds = db.Column(db.String(40))


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer)
    roomId = db.Column(db.Integer)
    foodId = db.Column(db.Integer)
    checkInDate = db.Column(db.DateTime)
    checkOutDate = db.Column(db.DateTime)
    dateOfBooking = db.Column(db.DateTime)
    confirmation = db.Column(db.Integer)
    feedback = db.Column(db.String(100))

class Authentication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    val = db.Column(db.Integer)

# Functions 

def checkAvailable(room):
    global checkInDate
    temp = checkInDate.day - datetime.now().day
    checkInIndex = temp
    global checkOutDate
    temp = checkOutDate.day - datetime.now().day
    checkOutIndex = temp
    if checkInIndex < 0 or checkOutIndex < 0:
        return False
    for i in room.status[checkInIndex:checkOutIndex+1]:
        if i == '1':
            return False
    return True

def TotalBookingCost(booked):
    room = Rooms.query.filter_by(id=booked.roomId).first()
    food = FoodOptions.query.filter_by(id=booked.foodId).first()
    days = ((booked.checkOutDate.day-booked.checkInDate.day)+1)
    cost = room.pricePerDay*days
    if food is not None:
        cost += food.pricePerDay*days
    return 0.2*cost

def updateStatus(roomId, checkInDate, checkOutDate, val):
    temp = checkInDate.day - datetime.now().day
    checkInInd = max(0, temp)
    temp = checkOutDate.day - datetime.now().day
    checkOutInd = temp
    room = Rooms.query.filter_by(id=roomId).first()
    newstat = room.status[0:checkInInd] + val*(checkOutInd-checkInInd+1) + room.status[checkOutInd+1:]
    room.status = newstat
    db.session.commit()

def checkBooking(bookingId):
    booking = Booking.query.filter_by(id=bookingId).first()
    if booking is None:
        return False
    room = Rooms.query.filter_by(id=booking.roomId).first()
    checkInDate = booking.checkInDate
    checkOutDate = booking.checkOutDate   
    temp = checkInDate.day - datetime.now().day
    checkInInd = temp
    temp = checkOutDate.day - datetime.now().day
    checkOutInd = temp
    for i in room.status[checkInInd:checkOutInd+1]:
        if i == '1':
            return False
    if checkInInd < 0 or checkOutInd < 0:
        return False
    booking.confirmation = 1
    db.session.commit()
    updateStatus(booking.roomId, checkInDate, checkOutDate, '1')
    return True

# prevent cached responses

if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Routes

@app.route('/details', methods=['POST'])
def details():
    json = request.get_json()
    print(json)

    return jsonify(result="done")


@app.route('/', methods=["POST", "GET"])
def hello_world():
    if request.method == "POST":
        print(request.form['username'])
        user = User.query.filter_by(username=request.form['username']).first()
        print(request.form['password'])
        if user is not None and user.password == request.form['password']:
            global currentuserid
            currentuserid = user.id
            if user.id == 0:
                return admin()
            else:
                auth = Authentication.query.filter_by(id=user.id).first()
                print(auth.val)
                if auth.val != 1:
                    return render_template('index.html', flag=auth.val)
                return render_template('calender.html')
        else:
            return render_template('index.html', flag=1)
    return render_template('index.html', flag=3)


@app.route('/signup', methods=["POST", "GET"])
def sign_up():
    if request.method == "POST":
        newid = User.query.count()+1
        username = request.form['username']
        password = request.form['password']
        name = request.form['first_name'] + request.form['last_name']
        email = request.form['email']
        address = request.form['address1']+", "+request.form['address2']+", City "+request.form['city']+", State "+request.form['state']        
        gender = request.form['gender']
        age = request.form['age']     
        rollStd = request.form['roll']
        role = request.form['role']
        
        checkusername = User.query.filter_by(username=request.form['username']).first()
        checkemail = User.query.filter_by(username=request.form['email']).first()
        if checkusername is None and checkemail is None:
            newUser = User(id=newid, name=name, email=email, username=username, password=password, address=address, age=age, gender=gender, rollStd=rollStd)
            newAuthReq = Authentication(id=newid, val=0)
            db.session.add(newAuthReq)
            db.session.commit()
        elif checkemail is not None:
            return render_template('regform.html', flag=2)
        else:
            return render_template('regform.html', flag=0)
        # push to db
        try:
            db.session.add(newUser)
            db.session.commit()
            print("User added successfully")
            return redirect('/')
        except:
            print("Could not add new user to the database")
    return render_template('regform.html', flag=1)


@app.route('/admin', methods=["POST", "GET"])
def admin():
    authRequests = []
    requests = Authentication.query.filter_by(val=0)
    for req in requests:
        authRequests.append(User.query.filter_by(id=req.id).first())
    return render_template('admin.html', users=authRequests)


@app.route('/adminDates', methods=["POST", "GET"])
def adminDates():
    return render_template('adminCalendar.html')


@app.route('/adminHistory', methods=["POST", "GET"])
def adminHistory():
    bookings = Booking.query.all()
    rooms = [Rooms.query.filter_by(id=i.roomId).first() for i in bookings]
    user = [User.query.filter_by(id=i.userId).first() for i in bookings]
    cost = [TotalBookingCost(i) for i in bookings]
    return render_template('adminPrevBooking.html', bookings=bookings, user=user, rooms=rooms, prices=cost)


@app.route('/authorize/<userId>/<desc>', methods=["POST", "GET"])
def authorize(userId, desc):
    userId = int(userId)
    desc = int(desc)
    userVal = Authentication.query.filter_by(id=userId).first()
    userVal.val = desc
    db.session.commit()
    return admin()

@app.route('/rooms', methods=["POST", "GET"])
def show_rooms():
    global checkInDate
    global checkOutDate
    global srt
    global foodId
    global availableOnly
    global rooms
    global avail
    global days
    global urls
    global roomAvail

    if 'availableOnly' in request.form:
        print("checking availability")
        if request.form['availableOnly'] == '1':
            availableOnly = '1'
            rooms = [i for i in rooms if checkAvailable(i)]
        else:
            availableOnly = '0'
            rooms = Rooms.query.all()

    elif 'srt' in request.form:
        print("sorting")
        if request.form['srt'] == '0':
            srt = '0'
            rooms.sort(key=lambda x: x.pricePerDay)
        else:
            srt = '1'
            rooms.sort(key=lambda x: x.pricePerDay, reverse=True)

    if 'foodId' in request.form:
        print("addind food")

        for i in rooms:
            temp = Rooms.query.filter_by(id=i.id).first()
            i.pricePerDay = temp.pricePerDay
        foodId = request.form['foodId']

        idx = int(foodId)
        foodItem = FoodOptions.query.filter_by(id=idx).first()
        if foodItem is not None:
            for i in rooms:
                i.pricePerDay += foodItem.pricePerDay
    else:
        print("called")
        if 'checkintime' in request.form:
            checkindate = datetime.strptime(request.form['checkintime'], '%Y-%m-%d')
            checkoutdate = datetime.strptime(request.form['checkouttime'], '%Y-%m-%d')
            checkInDate = checkindate
            checkOutDate = checkoutdate
            if datetime.now() <= checkInDate <= checkOutDate and (checkOutDate-datetime.now()).days < 100:
                pass
            else:
                if curUserId == 0:
                    return render_template('adminCalendar.html', flag=0)
                return render_template('calender.html', flag=0)
        print("called")
        print(checkInDate)
        print(checkOutDate)
        if availableOnly == '1':
            rooms = [i for i in rooms if checkAvailable(i)]
        else:
            rooms = Rooms.query.all()
        if srt == '0':
            rooms.sort(key=lambda x: x.pricePerDay)
        else:
            rooms.sort(key=lambda x: x.pricePerDay, reverse=True)
        if foodId != '0':
            for i in rooms:
                temp = Rooms.query.filter_by(id=i.id).first()
                i.pricePerDay = temp.pricePerDay
            idx = int(foodId)
            foodItem = FoodOptions.query.filter_by(id=idx).first()
            if foodItem is not None:
                for i in rooms:
                    i.pricePerDay += foodItem.pricePerDay
        curdate = datetime.now()
        startDay = max(curdate, checkInDate-timedelta(days=3)).day - curdate.day
        startIdx = startDay
        startdate = max(curdate, checkInDate-timedelta(days=3))
        for i in range(7):
            temp = startdate + timedelta(days=i)
            days.append(temp.day)
        avail = []
        for room in rooms:
            temp = []
            urls.append("/room/"+str(room.id))
            print(room.status)
            for j in range(7):
                temp.append(int(room.status[startIdx+j]))
            avail.append(temp)

    print(avail)
    print(len(rooms))
    roomAvail = [0]*len(rooms)
    for i, room in enumerate(rooms):
        roomAvail[i] = 1 if checkAvailable(room) else 0
    print(roomAvail)
    return render_template('Booking.html', rooms=rooms, avail=avail, days=days, urls=urls, availableOnly=availableOnly, srt=srt, foodId=foodId, roomAvail=roomAvail)


@app.route('/room/<roomid>', methods=["POST", "GET"])
def room(roomid):
    global roomId
    roomId = int(roomid)
    # print("Room ID is : " + roomId)
    roomBook = Rooms.query.filter_by(id=roomId).first()
    foodBook = FoodOptions.query.filter_by(id=foodId).first()
    roomCost = roomBook.pricePerDay*((checkOutDate.day-checkInDate.day)+1)
    foodCost = 0
    if foodBook is not None:
        foodCost = foodBook.pricePerDay*((checkOutDate.day-checkInDate.day)+1)

    payable = 0.2*(roomCost+foodCost)
    return render_template('Payment.html', roomPrice=roomCost, foodPrice=foodCost, payable=payable)


@app.route('/dates', methods=["POST", "GET"])
def dates():
    return render_template('calender.html')


@app.route('/history', methods=["POST", "GET"])
def history():
    currentDate = datetime.now()
    userBookings = Booking.query.filter_by(userId=curUserId).all()
    for i in userBookings:
        if currentDate > i.checkInDate and i.confirmation == 1:
            i.confirmation = 4
            db.session.commit()    
    rooms = [Rooms.query.filter_by(id=i.roomId).first() for i in userBookings]
    costs = [TotalBookingCost(i) for i in userBookings]
    user = User.query.filter_by(id=curUserId).first()
    return render_template('prevBooking.html', bookings=userBookings, user=user, rooms=rooms, prices=costs)

@app.route('/paymentComplete', methods=["POST", "GET"])
def paymentComplete():
    print("Payment Completed")
    id = Booking.query.count() + 1
    curRoom = Rooms.query.filter_by(id=roomId).first()
    if checkAvailable(curRoom):
        conf = 1
    else:
        conf = 0
    queueIds = BookingQueue.query.filter_by(id=roomId).first()
    if conf == 1:
        updateStatus(roomId, checkInDate, checkOutDate, '1')
        print(curRoom.status)
    else:
        if queueIds is None:
            print("first")
            newId = str(id)
            newId = newId.rjust(4, '0')
            stat = newId
            stat = stat.ljust(40, '0')
            temp = BookingQueue(id=roomId, bookingIds=stat)
            print(stat)
            db.session.add(temp)
            db.session.commit()
        else:
            print("second")
            addhere = 36
            newId = str(id)
            newId = newId.rjust(4, '0')
            for idx in range(0, 40, 4):
                checker = queueIds.bookingIds[idx:idx+4]
                print(checker)
                if int(checker) == 0:
                    addhere = idx
                    break
            newstat = queueIds.bookingIds[:addhere] + newId + (queueIds.bookingIds[addhere+4:] if addhere+4 < 39 else "")
            queueIds.bookingIds = newstat
            db.session.commit()

    newBooking = Booking(id=id, userId=curUserId, roomId=roomId, foodId=foodId, checkInDate=checkInDate, checkOutDate=checkOutDate, dateOfBooking=datetime.now().date(), confirmation=conf, feedback="")
    try:
        db.session.add(newBooking)
        db.session.commit()
        print("Booking added successfully")
    except:
        print("Could not add new Booking to db")
    return history()

@app.route('/cancelBooking<bookingId>', methods=["POST", "GET"])
def cancelBooking(bookingId):
    print("Cancelling")
    booking = Booking.query.filter_by(id=bookingId).first()
    roomId = booking.roomId
    queueIds = BookingQueue.query.filter_by(id=roomId).first()
    if booking.confirmation == 0:
        tempIds = ""
        for idx in range(0, 40, 4):
            test = queueIds.bookingIds[idx:idx + 4]
            if int(test) != booking.id:
                tempIds += test
        tempIds = tempIds.ljust(40, '0')
        queueIds.bookingIds = tempIds
        db.session.commit()
    else:
        updateStatus(roomId, booking.checkInDate, booking.checkOutDate, '0')
        if queueIds is not None:
            tempIds = ""
            for idx in range(0, 40, 4):
                test = queueIds.bookingIds[idx:idx + 4]
                if checkBooking(int(test)):
                    pass
                else:
                    tempiDs += test
            tempIds = tempIds.ljust(40, '0')
            queueIds.bookingIds = tempIds
            db.session.commit()

    booking.confirmation = 3
    db.session.commit()
    if curUserId == 0:
        return adminHistory()
    return history()

@app.route('/feedback/<bookingId>', methods=["POST", "GET"])
def feedback(bookingId):
    return render_template('feedback.html', bookingId=bookingId)

@app.route('/setfeedback/<bookingId>', methods=["POST", "GET"])
def setfeedback(bookingId):
    getfeedback = request.form['text']
    booking = Booking.query.filter_by(id=bookingId).first()
    booking.feedback = getfeedback
    booking.confirmation = 5
    db.session.commit()
    return history()

if __name__ == '__main__':
    app.run(debug = True)