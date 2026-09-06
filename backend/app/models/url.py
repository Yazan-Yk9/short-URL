from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, Index
from sqlalchemy.sql import func

from app.db.base import Base

class URL(Base):
    __tablename__ = "urls"
    id = Column(BigInteger, primary_key=True, index=True)

    short_code = Column(String(10), unique=True, index=True, nullable=False)

    original_url = Column(Text, nullable=False)

    custom_alias = Column(String(20), unique=True, nullable=True, default=None)

    clicks = Column(BigInteger, default=0, nullable=False)

    user_id = Column(Integer, nullable=True, index=True)

    expires_at = Column(DateTime(timezone=True), nullable=True, default=None)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Composite index for efficient filtering of active short codes
    __table_args__ = (
        Index('ix_urls_is_active_short_code', 'is_active', 'short_code'),
    )

    def __repr__(self):
        return f"<URL {self.short_code}>"
