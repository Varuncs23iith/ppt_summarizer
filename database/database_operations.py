from tools.database import AsyncSessionLocal
from orm.files import Files
from orm.slide import Slides
from orm.summary import Summary
from dto.file import File
from dto.slide import Slide
from sqlalchemy import select


async def insert_to_file_table(
        data: File
) -> int:
    """Insert file record and return the file_id."""
    data_to_persist = Files(
        file_path = data.file_path,
        file_extension = data.file_extension
    )
    async with AsyncSessionLocal() as session:
        async with session.begin():
            session.add(data_to_persist)
            await session.flush()
            file_id = data_to_persist.file_id
        return file_id


async def insert_to_slide_table(
        data: Slide
):
    """Insert slide record to database."""
    data_to_persist = Slides(
        file_id = data.file_id,
        slide_path = data.slide_path,
        slide_transcription = data.slide_transcription,
        slide_summary = data.slide_summary,
        running_summary = data.running_summary,
    )
    async with AsyncSessionLocal() as session:
        async with session.begin():
            session.add(data_to_persist)


async def get_slides_by_file_id(file_id: int) -> list[Slides]:
    """Get all slides for a given file_id ordered by slide_id."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Slides)
            .where(Slides.file_id == file_id)
            .order_by(Slides.slide_id)
        )
        return list(result.scalars().all())


async def insert_to_improvement_table(data):
    """Insert slide improvement record to database."""
    from orm.slide_improvement import SlideImprovement as SlideImprovementORM
    
    data_to_persist = SlideImprovementORM(
        slide_id = data.slide_id,
        content_clarity_score = data.content_clarity_score,
        visual_design_score = data.visual_design_score,
        information_density_score = data.information_density_score,
        engagement_score = data.engagement_score,
        overall_score = data.overall_score,
        improvement_points = data.improvement_points
    )
    async with AsyncSessionLocal() as session:
        async with session.begin():
            session.add(data_to_persist)


async def get_improvement_by_slide_id(slide_id: int):
    """Get improvement suggestion for a given slide_id."""
    from orm.slide_improvement import SlideImprovement as SlideImprovementORM
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SlideImprovementORM)
            .where(SlideImprovementORM.slide_id == slide_id)
        )
        return result.scalar_one_or_none()
