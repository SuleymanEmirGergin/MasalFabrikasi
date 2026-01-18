from datetime import datetime
from sqlalchemy import delete, or_
from app.core.database import AsyncSessionLocal
from app.models import PasswordResetToken, EmailVerificationToken
import logging
import asyncio

logger = logging.getLogger(__name__)

async def cleanup_expired_tokens():
    """
    Deletes expired or consumed tokens from the database.
    """
    async with AsyncSessionLocal() as session:
        try:
            now = datetime.utcnow()

            # Delete expired or consumed password reset tokens
            result_reset = await session.execute(
                delete(PasswordResetToken).where(
                    or_(
                        PasswordResetToken.expires_at < now,
                        PasswordResetToken.consumed_at.isnot(None)
                    )
                )
            )
            deleted_reset = result_reset.rowcount

            # Delete expired or consumed email verification tokens
            result_email = await session.execute(
                delete(EmailVerificationToken).where(
                    or_(
                        EmailVerificationToken.expires_at < now,
                        EmailVerificationToken.consumed_at.isnot(None)
                    )
                )
            )
            deleted_email = result_email.rowcount

            await session.commit()

            logger.info(f"Cleanup complete. Deleted {deleted_reset} reset tokens and {deleted_email} verification tokens.")
            return deleted_reset + deleted_email

        except Exception as e:
            logger.error(f"Error cleaning up tokens: {e}")
            await session.rollback()
            return 0

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Run cleanup
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cleanup_expired_tokens())
