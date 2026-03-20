from fastapi import FastAPI, Query, Response, status,HTTPException
from pydantic import BaseModel, Field
from typing import List

app=FastAPI()

####*******Models Pydantic validate incoming requests data automatic******######
class BookingRequest(BaseModel):
    customer_name:str=Field(...,min_length=2)
    movie_id:int=Field(...,gt=0)
    seats:int=Field(...,gt=0,le=10)
    phone:str=Field(...,min_length=10)
    seat_type:str="standard"
    promo_code:str=""

class NewMovie(BaseModel):
    title:str=Field(...,min_length=2)
    genre:str=Field(...,min_length=2)
    language:str=Field(...,min_length=2)
    duration_mins:int=Field(...,gt=0)
    ticket_price:int=Field(...,gt=0)
    seats_available:int=Field(...,gt=0)

class SeatHold(BaseModel):
    customer_name:str
    movie_id:int
    seats:int

####Data ==Stoes movies, bookings
movies=[
    {"id":1,"title":"Avengers","genre":"Action","Language":"English","duration_mins":150,"ticket_price":300,"seats_available":390},
    {"id":2,"title":"Conjuring","genre":"Horror","Language":"English","duration_mins":180,"ticket_price":380,"seats_available":230},
    {"id":3,"title":"Pushpa","genre":"Action","Language":"Hindi","duration_mins":140,"ticket_price":400,"seats_available":310},
    {"id":4,"title":"Golmaal","genre":"Comedy","Language":"Hindi","duration_mins":160,"ticket_price":320,"seats_available":210},
    {"id":5,"title":"KGF Chapter1","genre":"Action","Language":"Kannada","duration_mins":180,"ticket_price":290,"seats_available":180},
    {"id":6,"title":"Kantara","genre":"Horror","Language":"Hindi","duration_mins":140,"ticket_price":310,"seats_available":100},
    {"id":7,"title":"Dhurandhar","genre":"Action","Language":"Hindi","duration_mins":190,"ticket_price":410,"seats_available":300},
]
bookings=[]
holds=[]

booking_counter=1
hold_counter=1

# Helpers used for reusable business logic fun
def find_movie(movie_id:int):
    for m in movies:
        if m["id"]==movie_id:
            return m
    return None  # FIX: was indented inside for-loop — caused it to always return None

def calculate_ticket_cost(price,seats,seat_type,promo_code):
    multiplier=1
    if seat_type=="premium":
        multiplier=1.5
    elif seat_type=="recliner":
        multiplier=2

    original=price*seats*multiplier

    discount=0
    if promo_code=="SAVE10":
        discount=original*0.1
    elif promo_code=="SAVE20":
        discount=original*0.2
    
    return int(original),int(original-discount)

def filter_movies_logic(genre=None,language=None,max_price=None,min_seats=None):
    result=movies
    if genre is not None:
        result=[m for m in result if m["genre"]==genre]
    if language is not None:
        result=[m for m in result if m["Language"]==language]  # FIX: was m["langauge"]
    if max_price is not None:
        result=[m for m in result if m["ticket_price"]<=max_price]  # FIX: was m["max_price"]==max_price
    if min_seats is not None:
        result=[m for m in result if m["seats_available"]>=min_seats]  # FIX: was m["min_seats"]==min_seats
    return result  # FIX: missing return statement

###Question1 HOME
#API is running or not confirmed

@app.get("/")
def home():
    return{"message":"Welcome to CineStar Booking"}

### Question 2 Get All Movies showing total and seats of total

@app.get("/movies")
def get_movies():
    return{
        "movies":movies,
        "total":len(movies),
        "total_seats_available":sum(m["seats_available"] for m in movies)  # FIX: was mvoies (typo)
    }

# Question 5 Summary is above id

@app.get("/movies/summary")
def summary():
    return{
        "total_movies":len(movies),
        "most_expensive":max(movies,key=lambda x:x["ticket_price"]),
        "cheapest":min(movies,key=lambda x:x["ticket_price"]),
        "total_seats":sum(m["seats_available"] for m in movies),
        "genre_count":{g:len([m for m in movies if m["genre"]==g]) for g in set(m["genre"] for m in movies)}
    }

# Question 10- Filter movies
# FIX: moved above /movies/{movie_id} — fixed routes must come before variable routes

@app.get("/movies/filter")
def filter_movies(
    genre:str=Query(None),
    language:str=Query(None),
    max_price:int=Query(None),
    min_seats:int=Query(None)
):
    return{"results":filter_movies_logic(genre,language,max_price,min_seats)}

# Question 16 Search
# FIX: moved above /movies/{movie_id} — fixed routes must come before variable routes

@app.get("/movies/search")
def search_movies(keyword:str):
    result=[m for m in movies if keyword.lower() in (m["title"]+m["genre"]+m["Language"]).lower()]  # FIX: was m["language"] (lowercase)
    if not result:  # FIX: added friendly message when no results found (Q16 requirement)
        return{"results":[],"total_found":0,"message":"No movies found matching your search"}
    return {"results":result,"total_found":len(result)}

# Question 17 Sort
# FIX: moved above /movies/{movie_id} — fixed routes must come before variable routes

# Valid sort fields allowed
VALID_SORT_FIELDS=["ticket_price","title","duration_mins","seats_available"]

@app.get("/movies/sort")
def sort_movies(sort_by:str="ticket_price", order:str="asc"):
    if sort_by not in VALID_SORT_FIELDS:  # FIX: added validation for sort_by (Q17 requirement)
        raise HTTPException(400,f"Invalid sort_by. Choose from: {VALID_SORT_FIELDS}")
    if order not in ["asc","desc"]:  # FIX: added validation for order param (Q17 requirement)
        raise HTTPException(400,"Invalid order. Use 'asc' or 'desc'")
    reverse = order=="desc"
    return sorted(movies,key=lambda x:x[sort_by],reverse=reverse)

# question 18 Pagination
# FIX: moved above /movies/{movie_id} — fixed routes must come before variable routes

@app.get("/movies/page")
def paginate_movies(page:int=1,limit:int=3):
    start=(page-1)*limit
    end=start+limit
    return {
        "page":page,
        "total_pages":-(-len(movies)//limit),
        "data":movies[start:end]
    }

# Question 20 Browse bookings
# FIX: moved above /movies/{movie_id} — fixed routes must come before variable routes

@app.get("/movies/browse")
def browse(keyword:str=None,genre:str=None,language:str=None,
           sort_by:str="ticket_price",order:str="asc",
           page:int=1,limit:int=3):

    result = movies

    if keyword:
        result = [m for m in result if keyword.lower() in m["title"].lower()]
    if genre:
        result = [m for m in result if m["genre"]==genre]
    if language:
        result = [m for m in result if m["Language"]==language]

    valid = ["ticket_price","title","duration_mins","seats_available"]
    if sort_by not in valid:
        raise HTTPException(400,"Invalid sort field")

    start=(page-1)*limit
    end=start+limit

    return {
        "total":len(result),
        "data":result[start:end]
    }

# Question 3 Get Movies by id

@app.get("/movies/{movie_id}")
def get_movie_id(movie_id:int):
    movie=find_movie(movie_id)
    if not movie:
        raise HTTPException(404,"Movie not found")
    return movie

# Question 4 Get Booking List

@app.get("/bookings")
def get_bookings():
    return{
        "bookings":bookings,
        "total":len(bookings),
        "total_revenue":sum(b["final_cost"] for b in bookings)
    }

# question 19 Booking Search, sort, page
# FIX: moved above /bookings — sort/search/page fixed routes before variable routes

@app.get("/bookings/search")
def search_booking(name:str):
    result = [b for b in bookings if name.lower() in b["customer"].lower()]
    if not result:
        return {"results":[], "message":"No bookings found"}
    return {"results":result}

@app.get("/bookings/sort")
def sort_booking(sort_by:str="final_cost", order:str="asc"):
    reverse = order=="desc"
    return sorted(bookings,key=lambda x:x[sort_by],reverse=reverse) 
    valid=["final_cost","seats"]
    if sort_by not in valid:
        raise HTTPException(400,f"Invalid sort_by. Choose from: {valid}")
    return sorted(bookings,key=lambda x:x[sort_by])

@app.get("/bookings/page")
def page_booking(page:int=1,limit:int=2):
    start=(page-1)*limit
    end=start+limit
    return {
    "page":page,
    "total_pages":-(-len(bookings)//limit),
    "data":bookings[start:end]
}

# _______Question 6 to Question 9 Book Ticket_____________

@app.post("/bookings")
def book_ticket(data:BookingRequest):
    global booking_counter

    movie = find_movie(data.movie_id)
    if not movie:
        raise HTTPException(404,"Movie not found")

    if movie["seats_available"] < data.seats:
        raise HTTPException(400,"Not enough seats")

    original, final = calculate_ticket_cost(
        movie["ticket_price"], data.seats, data.seat_type, data.promo_code
    )

    movie["seats_available"] -= data.seats

    booking = {
        "booking_id":booking_counter,
        "customer":data.customer_name,
        "movie":movie["title"],
        "seats":data.seats,
        "seat_type":data.seat_type,
        "original_cost":original,
        "final_cost":final
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

# Question 11 Add Movie

@app.post("/movies")
def add_movie(data:NewMovie, response:Response):
    if any(m["title"].lower()==data.title.lower() for m in movies):
        response.status_code = 400
        return {"error":"Movie already exists"}

    new = data.dict()
    new["id"] = max(m["id"] for m in movies)+1
    # Align Language key to match existing data format
    new["Language"] = new.pop("language")
    movies.append(new)

    response.status_code = 201
    return new

# Question 12 Update Movies

@app.put("/movies/{movie_id}")
def update_movie(movie_id:int, ticket_price:int=Query(None), seats_available:int=Query(None)):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(404,"Movie not found")

    if ticket_price is not None:
        movie["ticket_price"] = ticket_price
    if seats_available is not None:
        movie["seats_available"] = seats_available

    return movie

# Question 13 Delete Movie

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id:int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(404,"Movie not found")

    if any(b["movie"]==movie["title"] for b in bookings):
        return {"error":"Cannot delete movie with bookings"}

    movies.remove(movie)
    return {"message":"Deleted"}


# Question 14 Seat HOLD

@app.post("/seat-hold")
def hold_seat(data:SeatHold):
    global hold_counter

    movie = find_movie(data.movie_id)
    if not movie:
        raise HTTPException(404,"Movie not found")

    if movie["seats_available"] < data.seats:
        raise HTTPException(400,"Not enough seats")

    movie["seats_available"] -= data.seats

    hold = {
        "hold_id":hold_counter,
        "customer":data.customer_name,
        "movie_id":data.movie_id,
        "seats":data.seats
    }

    holds.append(hold)
    hold_counter += 1
    return hold

@app.get("/seat-hold")
def get_holds():
    return holds

# Question 15 Confirm release Hold

@app.post("/seat-confirm/{hold_id}")
def confirm_hold(hold_id:int):
    global booking_counter

    for hold in holds:
        if hold["hold_id"] == hold_id:
            movie = find_movie(hold["movie_id"])

            booking = {
                "booking_id":booking_counter,
                "customer":hold["customer"],
                "movie":movie["title"],
                "seats":hold["seats"],
                "final_cost":movie["ticket_price"] * hold["seats"]
            }

            bookings.append(booking)
            holds.remove(hold)
            booking_counter += 1
            return booking

    raise HTTPException(404,"Hold not found")

@app.delete("/seat-release/{hold_id}")
def release_hold(hold_id:int):
    for hold in holds:
        if hold["hold_id"] == hold_id:
            movie = find_movie(hold["movie_id"])
            movie["seats_available"] += hold["seats"]
            holds.remove(hold)
            return {"message":"Hold released"}
    raise HTTPException(404,"Hold not found")