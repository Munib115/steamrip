from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    download_url = Column(Text, nullable=True)
    direct_file_url = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    file_size = Column(String(64), nullable=True)
    source_url = Column(Text, nullable=True)
    category = Column(String(64), nullable=True, index=True)
    genres = Column(String(255), nullable=True)
    top_rank = Column(Integer, nullable=True, default=None, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    files = relationship("GameFile", back_populates="game", cascade="all, delete-orphan")


class GameFile(Base):
    __tablename__ = "game_files"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(
        Integer,
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label = Column(String(128), nullable=True)
    url = Column(Text, nullable=False)
    file_type = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    game = relationship("Game", back_populates="files")