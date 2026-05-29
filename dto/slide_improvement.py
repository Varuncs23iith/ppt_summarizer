from pydantic import BaseModel


class SlideImprovement(BaseModel):
    """Simplified slide improvement data transfer object."""

    slide_id: int
    content_clarity_score: float
    visual_design_score: float
    information_density_score: float
    engagement_score: float
    overall_score: float
    improvement_points: str
