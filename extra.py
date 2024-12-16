from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel


# PYDANTIC MODELS
class MovieInput(BaseModel):
    name:str

class MovieOutput(BaseModel):
    id:int
    name:str

#########################
# sqlModel

class Movie(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)



sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/heroes/")
def create_hero(movie: Movie, session: SessionDep) -> Movie:
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie


@app.get("/heroes/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,) -> list[Movie]:

    movies = session.exec(select(Movie).offset(offset).limit(limit)).all()

    return movies


@app.get("/heroes/{hero_id}")
def read_hero(movie_id: int, session: SessionDep) -> Movie:
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Hero not found")
    return movie


@app.delete("/heroes/{hero_id}")
def delete_hero(movie_id: int, session: SessionDep):
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(movie)
    session.commit()
    return {"ok": True}