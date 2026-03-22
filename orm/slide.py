from tools.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey

class Slides(Base):
    """Files ORM"""

    __tablename__ = "slide"
    __table_args__ = {"schema": "ppt_summarizer"}

    slide_id: Mapped[int] = mapped_column(
                primary_key=True,
                autoincrement=True,
                nullable=False
                )
    file_id: Mapped[int] = mapped_column(
        ForeignKey("ppt_summarizer.files.file_id", ondelete="CASCADE"),
        nullable=False
    )
    slide_path:Mapped[str] = mapped_column(
        nullable=False
    )
    slide_summary:Mapped[str] = mapped_column(
        nullable=False
    )
    running_summary:Mapped[str] = mapped_column(
        nullable=False
    )
    created_at: Mapped[datetime]=mapped_column(
        nullable=False,
        default=datetime.now()
    )