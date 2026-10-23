from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class GameFileBase(BaseModel):
    label: Optional[str] = None
    url: Optional[HttpUrl] = None
    file_type: Optional[str] = None


class GameFileOut(GameFileBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class GameBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    download_url: Optional[str] = None
    direct_file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    file_size: Optional[str] = None
    source_url: Optional[str] = None
    category: Optional[str] = None
    genres: Optional[str] = None
    top_rank: Optional[int] = None
    is_active: bool = True


class GameCreate(GameBase):
    pass


class GameOut(GameBase):
    id: int
    created_at: Optional[datetime] = None
    files: List[GameFileOut] = []
    model_config = ConfigDict(from_attributes=True)


class GameListOut(BaseModel):
    items: List[GameOut]
    total: int
    page: int
    page_size: int
    pages: int