from sqlalchemy.orm import Session

from app.models.analytics_event import AnalyticsEvent
from app.models.user import User
from app.schemas.analytics import AnalyticsEventCreate, AnalyticsEventResponse


class AnalyticsService:

    @staticmethod
    async def log_event(
        db: Session,
        user: User,
        data: AnalyticsEventCreate,
    ) -> AnalyticsEventResponse:
        event = AnalyticsEvent(
            user_id=user.id,
            game_id=data.game_id,
            screen_time=data.screen_time,
            duration=data.duration,
            city=data.city,
            state=data.state,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return AnalyticsEventResponse.model_validate(event)
