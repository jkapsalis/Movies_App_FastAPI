from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# SQLite database setup
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()


# SQLAlchemy Models
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)


class MovieDB(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)


class ReviewDB(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    review = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))

    user = relationship("UserDB")
    movie = relationship("MovieDB")


class BookingDB(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    status = Column(String)  # e.g., "booked", "canceled", etc.

    user = relationship("UserDB")
    movie = relationship("MovieDB")


# Create tables in the database
Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models for validation
class User(BaseModel):
    name: str
    email: str


class Movie(BaseModel):
    name: str
    description: str


class Review(BaseModel):
    review: str
    user_id: int
    movie_id: int


class Booking(BaseModel):
    user_id: int
    movie_id: int
    status: str


# 1. Get all users
@app.get("/users/", response_model=List[User])
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserDB).all()
    return users


# 2. Create a new user
@app.post("/users/", response_model=User)
async def create_user(user: User, db: Session = Depends(get_db)):
    db_user = UserDB(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 3. Get a user by ID
@app.get("/users/{user_id}", response_model=User)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# 4. Create a new movie
@app.post("/movies/", response_model=Movie)
async def create_movie(movie: Movie, db: Session = Depends(get_db)):
    db_movie = MovieDB(name=movie.name, description=movie.description)
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


# 5. Get all movies
@app.get("/movies/", response_model=List[Movie])
async def get_all_movies(db: Session = Depends(get_db)):
    movies = db.query(MovieDB).all()
    return movies


# 6. Get a movie by ID
@app.get("/movies/{movie_id}", response_model=Movie)
async def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(MovieDB).filter(MovieDB.id == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie


# 7. Create a new booking or review
@app.post("/reviews/", response_model=Review)
async def create_review(review: Review, db: Session = Depends(get_db)):
    db_review = ReviewDB(review=review.review, user_id=review.user_id, movie_id=review.movie_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@app.post("/bookings/", response_model=Booking)
async def create_booking(booking: Booking, db: Session = Depends(get_db)):
    db_booking = BookingDB(user_id=booking.user_id, movie_id=booking.movie_id, status=booking.status)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


# 8. Get all bookings or reviews
@app.get("/reviews/", response_model=List[Review])
async def get_all_reviews(db: Session = Depends(get_db)):
    reviews = db.query(ReviewDB).all()
    return reviews


@app.get("/bookings/", response_model=List[Booking])
async def get_all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(BookingDB).all()
    return bookings
