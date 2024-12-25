from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Extract endpoint ID and construct connection URL with proper parameters
ENDPOINT_ID = "ep-tiny-breeze-a5xyw1ws"
DB_USER = "florida_business_owner"
DB_PASS = "brthgUq59MVG"
DB_NAME = "florida_business"

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASS}@"
    f"{ENDPOINT_ID}.us-east-2.aws.neon.tech/{DB_NAME}"
    f"?sslmode=require"
    f"&options=endpoint%3D{ENDPOINT_ID}"
)

# Create engine with SSL requirement for Neon.tech
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    connect_args={
        "connect_timeout": 10
    },
    echo=True  # Enable SQL logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    try:
        # Import models here to avoid circular imports
        from .models import Business
        
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        
        logger.info("Creating database tables...")
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Verify table exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'businesses'
                )
            """))
            exists = result.scalar()
            
            if exists:
                logger.info("Table 'businesses' exists")
                # Log table structure
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'businesses'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                logger.info(f"Table structure: {columns}")
            else:
                logger.error("Table 'businesses' was not created")
                raise Exception("Table creation verification failed")
                
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during initialization: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        raise

# Don't initialize on import - let FastAPI handle it
