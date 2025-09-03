#!/usr/bin/env python3
"""
Database initialization script for LLM Text Processor.

This script creates the database tables and can be used for:
- Initial setup
- Testing
- Development environment setup
"""

import sys
import asyncio
from pathlib import Path
from app.core import get_settings, get_logger, init_db, close_db, setup_logging

settings = get_settings()
setup_logging(settings)
logger = get_logger(__name__)

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def main():
    """Main function to initialize the database."""
    try:
        logger.info("Starting database initialization...")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        
        # Initialize database tables
        await init_db()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)
    finally:
        # Close database connections
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
