from tools.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey

class Summary(Base):
    """Files ORM"""

    __tablename__ = "summary"
    __table_args__ = {"schema": "ppt_summarizer"}

    summary_id: Mapped[int] = mapped_column(
                primary_key=True,
                autoincrement=True,
                nullable=False
                )
    file_id: Mapped[int] = mapped_column(
        ForeignKey("ppt_summarizer.files.file_id", ondelete="CASCADE"),
        nullable=False
    )
    summary_text:Mapped[str] = mapped_column(
        nullable=False
    )
    created_at: Mapped[datetime]=mapped_column(
        nullable=False,
        default=datetime.now()
    )