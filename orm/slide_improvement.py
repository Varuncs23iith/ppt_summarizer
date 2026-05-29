from tools.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey, Text

class SlideImprovement(Base):
    """Slide Improvement Suggestions ORM - Simplified"""

    __tablename__ = "slide_improvement"
    __table_args__ = {"schema": "ppt_summarizer"}

    improvement_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    slide_id: Mapped[int] = mapped_column(
        ForeignKey("ppt_summarizer.slide.slide_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Simplified scores (only 4)
    content_clarity_score: Mapped[float] = mapped_column(nullable=False)
    visual_design_score: Mapped[float] = mapped_column(nullable=False)
    information_density_score: Mapped[float] = mapped_column(nullable=False)
    engagement_score: Mapped[float] = mapped_column(nullable=False)
    overall_score: Mapped[float] = mapped_column(nullable=False)
    
    # Full improvement text
    improvement_points: Mapped[str] = mapped_column(Text, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.now()
    )
