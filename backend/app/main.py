from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import logging

from .database import get_db, init_db
from .models import Business
from .crawler import FloridaBusinessCrawler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

@app.get("/api/search/{business_name}")
async def search_business(business_name: str, db: Session = Depends(get_db)):
    # Check if business exists in database
    existing_business = db.query(Business).filter(Business.name.ilike(f"%{business_name}%")).first()
    
    if existing_business:
        return existing_business
    
    # If not found, crawl the website
    async with FloridaBusinessCrawler() as crawler:
        business_data = await crawler.search_business(business_name)
    
    if not business_data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Save to database
    new_business = Business(**business_data)
    db.add(new_business)
    db.commit()
    db.refresh(new_business)
    
    return new_business

@app.get("/api/business/{business_id}")
def get_business(business_id: int, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business
