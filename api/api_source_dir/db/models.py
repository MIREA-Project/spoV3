from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Statistic(Base):
    __tablename__ = "statistic"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    steps: Mapped[int] = mapped_column()
