import os
import sys
import logging

logger = logging.getLogger(__name__)

REQUIRED_VARS = [
    "DATABASE_URL",
    "SECRET_KEY",
    "STRIPE_SECRET_KEY",
    # Add other critical variables here
]

def validate_environment():
    """
    Validate that all required environment variables are set.
    """
    missing_vars = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.critical(error_msg)
        # In production, we might want to exit. In dev/test, maybe just log.
        # For strict correctness, we raise an error.
        raise EnvironmentError(error_msg)

    logger.info("Environment variables validated successfully.")
