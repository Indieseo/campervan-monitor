"""
Deep Data Collection Database Models
Focused on quality insights - 20+ data points per competitor
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core_config import config
    DATABASE_PATH = config.database.DATABASE_PATH
    DATABASE_URL = config.database.DATABASE_URL
except ImportError:
    # Fallback for backwards compatibility
    BASE_DIR = Path(__file__).parent.parent.resolve()
    DATABASE_PATH = BASE_DIR / "database" / "campervan_intelligence.db"
    DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

Base = declarative_base()


class CompetitorPrice(Base):
    """Deep pricing intelligence - 20+ fields"""
    __tablename__ = 'competitor_prices'
    
    # Core identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(100), nullable=False, index=True)
    scrape_timestamp = Column(DateTime, default=datetime.now, index=True)
    tier = Column(Integer)  # 1=Daily, 2=Weekly, 3=Monthly
    
    # Pricing - Base
    base_nightly_rate = Column(Float)
    weekend_premium_pct = Column(Float)  # % increase for weekends
    seasonal_multiplier = Column(Float)  # Summer vs winter pricing
    currency = Column(String(3), default='EUR')
    
    # Pricing - Discounts & Fees
    early_bird_discount_pct = Column(Float)
    weekly_discount_pct = Column(Float)
    monthly_discount_pct = Column(Float)
    last_minute_discount_pct = Column(Float)
    insurance_cost_per_day = Column(Float)
    cleaning_fee = Column(Float)
    booking_fee = Column(Float)
    
    # Inventory & Availability
    mileage_limit_km = Column(Integer)
    mileage_cost_per_km = Column(Float)
    fuel_policy = Column(String(50))  # 'full-to-full', 'prepaid', etc.
    min_rental_days = Column(Integer)
    fleet_size_estimate = Column(Integer)
    vehicles_available = Column(Integer)  # Current availability
    
    # Vehicle Details
    vehicle_types = Column(JSON)  # List of van types offered
    vehicle_features = Column(JSON)  # Features list
    popular_vehicle_type = Column(String(100))
    
    # Geographic & Operational
    locations_available = Column(JSON)  # List of pickup locations
    popular_routes = Column(JSON)  # Top rental routes
    one_way_rental_allowed = Column(Boolean)
    one_way_fee = Column(Float)
    
    # Promotions & Marketing
    active_promotions = Column(JSON)  # Current deals
    promotion_text = Column(Text)  # Exact promo copy
    discount_code_available = Column(Boolean)
    referral_program = Column(Boolean)
    
    # Customer Experience
    booking_process_steps = Column(Integer)  # Number of steps to book
    payment_options = Column(JSON)  # Payment methods
    cancellation_policy = Column(String(200))
    customer_review_avg = Column(Float)  # Average rating
    review_count = Column(Integer)
    
    # Metadata
    data_source_url = Column(String(500))
    scraping_strategy_used = Column(String(100))
    extraction_method = Column(String(100))  # How price was extracted: api_interception, booking_simulation, text_extraction, industry_estimates
    data_completeness_pct = Column(Float)  # % of fields filled
    is_estimated = Column(Boolean, default=False)  # If some data is estimated
    notes = Column(Text)
    

class CompetitorIntelligence(Base):
    """Strategic intelligence - qualitative insights"""
    __tablename__ = 'competitor_intelligence'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(100), nullable=False, index=True)
    date_observed = Column(DateTime, default=datetime.now)
    
    # Strategic Insights
    business_model = Column(String(100))  # P2P, Traditional, Aggregator
    target_market = Column(String(200))  # Budget, Premium, Family, etc.
    competitive_advantage = Column(Text)  # What makes them different
    
    # Recent Changes
    website_changes_detected = Column(JSON)  # UX/design updates
    new_features_launched = Column(JSON)  # New services
    pricing_strategy_change = Column(Text)  # Strategy shifts detected
    marketing_campaign_active = Column(Boolean)
    
    # Market Position
    estimated_market_share_pct = Column(Float)
    geographic_expansion = Column(JSON)  # New markets entered
    partnership_announcements = Column(JSON)
    
    # Technology
    mobile_app_available = Column(Boolean)
    mobile_app_rating = Column(Float)
    website_ux_score = Column(Float)  # 1-10 subjective score
    tech_stack_detected = Column(JSON)  # Technologies used
    
    # Social & Reviews
    social_media_sentiment = Column(String(20))  # Positive, Negative, Neutral
    recent_reviews_summary = Column(Text)
    seo_ranking_position = Column(Integer)  # Google ranking for key terms
    
    # Competitive Threats
    threat_level = Column(String(20))  # Low, Medium, High, Critical
    threat_description = Column(Text)
    recommended_response = Column(Text)


class MarketIntelligence(Base):
    """Aggregate market insights"""
    __tablename__ = 'market_intelligence'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_date = Column(DateTime, default=datetime.now)
    
    # Market Metrics
    market_avg_price = Column(Float)
    market_median_price = Column(Float)
    price_range_min = Column(Float)
    price_range_max = Column(Float)
    market_volatility = Column(Float)  # Price standard deviation
    
    # Competitive Position
    indie_campers_rank = Column(Integer)  # Position in market
    indie_campers_price = Column(Float)
    price_gap_to_leader = Column(Float)  # How far from cheapest
    price_gap_to_follower = Column(Float)  # How far ahead of next
    
    # Trends
    avg_price_change_pct = Column(Float)  # Week-over-week change
    trend_direction = Column(String(20))  # 'increasing', 'decreasing', 'stable'
    seasonal_factor = Column(Float)  # Current season multiplier
    
    # Opportunities
    pricing_opportunities = Column(JSON)  # List of opportunities
    threat_alerts = Column(JSON)  # Active threats
    recommended_actions = Column(JSON)  # What to do
    
    # Summary
    market_summary = Column(Text)
    executive_insight = Column(Text)  # One-liner for C-suite


class PriceAlert(Base):
    """Price monitoring alerts"""
    __tablename__ = 'price_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_timestamp = Column(DateTime, default=datetime.now)
    
    # Alert Details
    alert_type = Column(String(50))  # 'price_drop', 'price_spike', 'new_promo', etc.
    severity = Column(String(20))  # 'low', 'medium', 'high', 'critical'
    company_name = Column(String(100))
    
    # What Changed
    old_value = Column(Float)
    new_value = Column(Float)
    change_pct = Column(Float)
    
    # Context
    alert_message = Column(Text)
    recommended_action = Column(Text)
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    action_taken = Column(Text)
    resolved_at = Column(DateTime)


# Database utilities
def init_database() -> Engine:
    """
    Initialize database with deep schema.

    Returns:
        SQLAlchemy Engine instance
    """
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine: Engine = create_engine(f'sqlite:///{DATABASE_PATH}')
    Base.metadata.create_all(engine)
    print(f"[OK] Database initialized: {DATABASE_PATH}")
    return engine


def get_session() -> Session:
    """
    Get database session.

    Returns:
        SQLAlchemy Session instance
    """
    engine: Engine = create_engine(f'sqlite:///{DATABASE_PATH}')
    SessionMaker = sessionmaker(bind=engine)
    return SessionMaker()


def add_price_record(data: Dict[str, Any]) -> int:
    """
    Add deep price record.

    Args:
        data: Dictionary containing price record fields

    Returns:
        ID of newly created record
    """
    session: Session = get_session()
    price = CompetitorPrice(**data)
    session.add(price)
    session.commit()
    record_id: int = price.id
    session.close()
    return record_id


def get_latest_prices(limit: int = 10) -> List[CompetitorPrice]:
    """
    Get most recent price records.

    Args:
        limit: Maximum number of records to return

    Returns:
        List of CompetitorPrice records
    """
    session: Session = get_session()
    prices: List[CompetitorPrice] = session.query(CompetitorPrice)\
        .order_by(CompetitorPrice.scrape_timestamp.desc())\
        .limit(limit)\
        .all()
    session.close()
    return prices


def get_market_summary() -> Optional[MarketIntelligence]:
    """
    Get latest market intelligence.

    Returns:
        MarketIntelligence record or None if not found
    """
    session: Session = get_session()
    summary: Optional[MarketIntelligence] = session.query(MarketIntelligence)\
        .order_by(MarketIntelligence.analysis_date.desc())\
        .first()
    session.close()
    return summary


def get_active_alerts() -> List[PriceAlert]:
    """
    Get unresolved alerts.

    Returns:
        List of unacknowledged PriceAlert records
    """
    session: Session = get_session()
    alerts: List[PriceAlert] = session.query(PriceAlert)\
        .filter(PriceAlert.is_acknowledged == False)\
        .order_by(PriceAlert.alert_timestamp.desc())\
        .all()
    session.close()
    return alerts


def calculate_data_completeness(price_record: CompetitorPrice) -> float:
    """
    Calculate how complete the data is.

    Args:
        price_record: CompetitorPrice instance

    Returns:
        Percentage of filled fields (0-100)
    """
    total_fields: int = 35  # Total number of data fields
    filled_fields: int = 0

    for column in price_record.__table__.columns:
        value: Any = getattr(price_record, column.name)
        if value is not None:
            filled_fields += 1

    return (filled_fields / total_fields) * 100


if __name__ == "__main__":
    print("Initializing Deep Intelligence Database")
    print("=" * 50)

    engine = init_database()

    print("\nDatabase Schema:")
    print(f"  - CompetitorPrice: {len(CompetitorPrice.__table__.columns)} fields")
    print(f"  - CompetitorIntelligence: {len(CompetitorIntelligence.__table__.columns)} fields")
    print(f"  - MarketIntelligence: {len(MarketIntelligence.__table__.columns)} fields")
    print(f"  - PriceAlert: {len(PriceAlert.__table__.columns)} fields")

    print("\n[OK] Database ready for deep data collection!")
