from tools.database import AsyncSessionLocal
from orm.files import Files
from orm.slide import Slides
from orm.summary import Summary
from dto.file import File
from dto.slide import Slide



async def insert_to_file_table(
        data: File
):
    data_to_persist = Files(
        file_path = data.file_path,
        file_extension = data.file_extension
    )
    async with AsyncSessionLocal() as session, session.begin():
        session.add(data_to_persist)
        await session.commit()


async def insert_to_slide_table(
        data: Slide
):
    data_to_persist = Slides(
        file_id = data.file_id,
        slide_path = data.slide_path,
        slide_summary = data.slide_summary,
        running_summary = data.running_summary,

    )
    async with AsyncSessionLocal() as session, session.begin():
        session.add(data_to_persist)
        await session.commit()
