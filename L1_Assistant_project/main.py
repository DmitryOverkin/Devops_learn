from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select

# Should be in .env file!
DATABASE_USERNAME = ""
PASSWORD = ""
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432
DATABASE_NAME = "buildings"

DATABASE_URL = f"postgresql+psycopg://{DATABASE_USERNAME}:{PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
)

def get_session():
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise

# Наследуемся от SQLModel с table=True, чтобы связать класс с таблицей buildings
class Building(SQLModel, table=True):
    __tablename__ = "buildings"  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    price: float


app = FastAPI()

@app.get("/", response_model=List[Building])
async def read_buildings(session: Session = Depends(get_session)):
    statement = select(Building)
    buildings = session.exec(statement).all()
    return buildings

@app.get("/building/{building_id}", response_model=Building)
async def read_building(building_id: int, session: Session = Depends(get_session)):
    building = session.get(Building, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building

@app.post("/building/", response_model=Building)
async def create_building(building: Building, session: Session = Depends(get_session)):
    session.add(building)
    session.commit()
    session.refresh(building)
    return building