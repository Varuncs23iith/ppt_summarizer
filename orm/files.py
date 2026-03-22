from tools.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Files(Base):
    """Files ORM"""

    __tablename__ = "files"
    __table_args__ = {"schema": "ppt_summarizer"}

    file_id: Mapped[int] = mapped_column(
                primary_key=True,
                autoincrement=True,
                nullable=False
                )
    file_path: Mapped[str] = mapped_column(
        nullable=False
    )
    file_extension:Mapped[str] = mapped_column(
        nullable=False
    )
    uploaded_at: Mapped[datetime]=mapped_column(
        nullable=False,
        default=datetime.now()
    )