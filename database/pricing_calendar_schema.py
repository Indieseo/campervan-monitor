"""
Comprehensive Pricing Calendar Schema
Tracks price per night for each vehicle model, each date, each competitor
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Date, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from pathlib import Path

Base = declarative_base()


class VehicleModel(Base):
    """Vehicle models offered by competitors"""
    __tablename__ = 'vehicle_models'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(100), nullable=False, index=True)
    model_name = Column(String(200), nullable=False)
    model_category = Column(String(50))  # 'Class A', 'Class B', 'Class C', 'Van', etc.
    sleeps = Column(Integer)  # Number of people
    features = Column(JSON)  # List of features
    image_url = Column(String(500))
    
    # Make company + model unique
    __table_args__ = (
        UniqueConstraint('company_name', 'model_name', name='uq_company_model'),
        Index('idx_company_category', 'company_name', 'model_category'),
    )


class DailyPrice(Base):
    """Daily pricing for each vehicle model"""
    __tablename__ = 'daily_prices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(100), nullable=False, index=True)
    model_name = Column(String(200), nullable=False, index=True)
    rental_date = Column(Date, nullable=False, index=True)  # The date of rental start
    
    # Pricing
    price_per_night = Column(Float, nullable=False)
    currency = Column(String(3), default='EUR')
    min_nights = Column(Integer, default=1)
    
    # Rental details
    search_location = Column(String(100))  # Where search was performed
    pickup_location = Column(String(100))  # Actual pickup location
    rental_duration_days = Column(Integer, default=7)  # How many days rental
    
    # Additional costs
    insurance_per_day = Column(Float)
    cleaning_fee = Column(Float)
    service_fee = Column(Float)
    total_rental_cost = Column(Float)  # Total for the rental duration
    
    # Availability
    is_available = Column(Boolean, default=True)
    num_available = Column(Integer, default=1)  # How many of this model available
    
    # Metadata
    scraped_at = Column(DateTime, default=datetime.now)
    booking_url = Column(String(500))
    notes = Column(String(500))
    
    # Make company + model + date unique
    __table_args__ = (
        UniqueConstraint('company_name', 'model_name', 'rental_date', name='uq_company_model_date'),
        Index('idx_date_company', 'rental_date', 'company_name'),
        Index('idx_price_date', 'price_per_night', 'rental_date'),
    )


class PriceSnapshot(Base):
    """Aggregated pricing snapshot per company per date"""
    __tablename__ = 'price_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(100), nullable=False, index=True)
    snapshot_date = Column(Date, nullable=False, index=True)
    search_location = Column(String(100))
    
    # Aggregated pricing
    min_price_per_night = Column(Float)
    max_price_per_night = Column(Float)
    avg_price_per_night = Column(Float)
    median_price_per_night = Column(Float)
    
    # Availability
    total_vehicles_available = Column(Integer)
    num_models_available = Column(Integer)
    
    # Metadata
    scraped_at = Column(DateTime, default=datetime.now)
    num_prices_collected = Column(Integer)
    
    __table_args__ = (
        UniqueConstraint('company_name', 'snapshot_date', 'search_location', name='uq_company_date_location'),
        Index('idx_snapshot_date', 'snapshot_date'),
    )


def init_pricing_database():
    """Initialize the pricing calendar database"""
    BASE_DIR = Path(__file__).parent.parent
    db_path = BASE_DIR / "database" / "pricing_calendar.db"
    db_path.parent.mkdir(exist_ok=True)
    
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    print(f"[OK] Pricing Calendar Database initialized: {db_path}")
    return engine


def get_pricing_session():
    """Get database session for pricing calendar"""
    BASE_DIR = Path(__file__).parent.parent
    db_path = BASE_DIR / "database" / "pricing_calendar.db"
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    print("="*80)
    print("PRICING CALENDAR DATABASE SCHEMA")
    print("="*80)
    print("\nTables:")
    print("1. vehicle_models - Vehicle models from each competitor")
    print("2. daily_prices - Price per night for each model, each date")
    print("3. price_snapshots - Aggregated pricing summaries")
    print("\nData Capacity:")
    print("- Companies: Unlimited")
    print("- Models per company: Unlimited")
    print("- Dates: 365+ days")
    print("- Potential data points: 10 companies * 10 models * 365 days = 36,500+")
    print("\nInitializing...")
    
    engine = init_pricing_database()
    
    print("\n✅ Database ready!")
    print("="*80)




