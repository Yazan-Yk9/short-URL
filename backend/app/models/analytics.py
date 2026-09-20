from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ClickAnalytics(Base):
    __tablename__ = "clicks_analytics"

    id = Column(BigInteger, primary_key=True, index=True)

    # Link to the URL (CASCADE: deleting URL removes its clicks)
    url_id = Column(
        BigInteger,
        ForeignKey("urls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Denormalized for faster queries
    short_code = Column(String(20), nullable=False, index=True)

    # Raw request data
    ip_address = Column(String(45), nullable=True)  # IPv6-compatible
    user_agent = Column(Text, nullable=True)
    referer = Column(Text, nullable=True)

    # Parsed from user_agent
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)
    device_type = Column(String(20), nullable=True)  # desktop / mobile / tablet / bot
    country = Column(String(2), nullable=True)  # ISO code

    # Timestamp
    clicked_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship back to URL
    url = relationship("URL", backref="clicks_analytics")

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("ix_clicks_url_clicked_at", "url_id", "clicked_at"),
        Index("ix_clicks_short_code_clicked_at", "short_code", "clicked_at"),
    )

    def __repr__(self):
        return f"<Click {self.short_code} from {self.device_type} at {self.clicked_at}>"
