"""
Vercel serverless function wrapper for FastAPI application.
This file is required by Vercel to run Python serverless functions.
"""
from mangum import Mangum
from src.api.main import app

# Wrap FastAPI app with Mangum for AWS Lambda/Vercel compatibility
handler = Mangum(app, lifespan="off")

# Export handler for Vercel
__all__ = ["handler"]

