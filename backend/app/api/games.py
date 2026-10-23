import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import ColumnElement

from app.database import get_session
from app.models import Game
from app.schemas import GameListOut, GameOut

router = APIRouter()

ALIAS_MAP = {
    "gta": "grand theft auto",
    "cod": "call of duty",
    "mw": "modern warfare",
    "bo": "black ops",
    "rdr": "red dead redemption",
    "ac": "assassins creed",
    "nfs": "need for speed",
    "gow": "god of war",
    "re": "resident evil",
    "bf": "battlefield",
    "ff": "final fantasy",
    "tes": "the elder scrolls",
    "cp2077": "cyberpunk 2077",
    "cyberpunk": "cyberpunk 2077",
}

EXPANSIONS = {
    "gta 5": ["grand theft auto v", "grand theft auto 5", "gta v", "gta 5"],
    "gta5": ["grand theft auto v", "grand theft auto 5", "gta v"],
    "gta v": ["grand theft auto v", "grand theft auto 5", "gta 5"],
    "gtav": ["grand theft auto v", "grand theft auto 5"],
    "gta 4": ["grand theft auto iv", "grand theft auto 4", "gta iv"],
    "gta4": ["grand theft auto iv", "grand theft auto 4"],
    "gta iv": ["grand theft auto iv", "grand theft auto 4"],
    "gtaiv": ["grand theft auto iv", "grand theft auto 4"],
    "gta 3": ["grand theft auto iii", "grand theft auto 3", "gta iii"],
    "gta3": ["grand theft auto iii", "grand theft auto 3"],
    "gta iii": ["grand theft auto iii", "grand theft auto 3"],
    "gta sa": ["grand theft auto san andreas", "gta san andreas"],
    "gta vc": ["grand theft auto vice city", "gta vice city"],
    "rdr 2": ["red dead redemption 2", "red dead redemption ii", "rdr2"],
    "rdr2": ["red dead redemption 2", "red dead redemption ii"],
    "rdr 1": ["red dead redemption", "rdr1"],
    "rdr1": ["red dead redemption"],
    "spiderman": ["spider-man", "spider man"],
    "spider-man": ["spider-man", "spiderman"],
    "tom clancy": [
        "tom clancy", "rainbow six", "splinter cell", "ghost recon", "the division"
    ],
    "tom clancys": [
        "tom clancy", "rainbow six", "splinter cell", "ghost recon", "the division"
    ],
    "tom clancy's": [
        "tom clancy", "rainbow six", "splinter cell", "ghost recon", "the division"
    ],
    "r6": ["rainbow six", "rainbow 6", "tom clancy"],
    "rainbow six": ["rainbow six", "rainbow 6", "tom clancy"],
    "splinter cell": ["splinter cell", "tom clancy"],
    "ghost recon": ["ghost recon", "tom clancy"],
    "the division": ["the division", "division", "tom clancy"],
    "racing": [
        "racing", "need for speed", "forza", "assetto corsa", "dirt",
        "burnout", "wrc", "carx", "wreckfest", "motogp", "flatout", "beamng", "the crew"
    ],
    "ubisoft": [
        "assassin's creed", "far cry", "watch dogs", "tom clancy",
        "rainbow six", "splinter cell", "ghost recon", "the division",
        "prince of persia", "rayman", "the crew", "for honor"
    ],
    "naruto": ["naruto", "ninja storm", "shinobi striker", "boruto"],
    "storm 4": ["storm 4", "ultimate ninja storm 4", "naruto"],
    "storm4": ["storm 4", "ultimate ninja storm 4", "naruto"],
    "dragon ball": ["dragon ball", "sparking! zero", "kakarot", "xenoverse", "fighterz"],
    "dragonball": ["dragon ball", "sparking! zero", "kakarot", "xenoverse", "fighterz"],
    "dbz": ["dragon ball", "kakarot", "xenoverse", "fighterz", "sparking"],
    "one piece": ["one piece", "pirate warriors", "odyssey", "unlimited world red"],
    "demon slayer": ["demon slayer", "kimetsu no yaiba", "hinokami chronicles"],
    "jujutsu kaisen": ["jujutsu kaisen", "cursed clash"],
    "jjk": ["jujutsu kaisen", "cursed clash"],
    "persona": ["persona 5", "persona 4", "persona 3", "persona"],
    "p5": ["persona 5", "persona 5 strikers", "persona 5 royal"],
    "p4": ["persona 4 golden", "persona 4"],
    "p3": ["persona 3 reload", "persona 3"],
    "sword art online": ["sword art online", "sao", "fractured daydream", "last recollection"],
    "sao": ["sword art online", "fractured daydream", "last recollection"],
    "attack on titan": ["attack on titan", "aot", "wings of freedom"],
    "aot": ["attack on titan"],
    "my hero": ["my hero", "my hero academia", "one's justice"],
    "mha": ["my hero academia", "my hero"],
    "bleach": ["bleach", "rebirth of souls"],
    "jojo": ["jojo's bizarre adventure", "all-star battle"],
    "anime": [
        "naruto", "dragon ball", "one piece", "demon slayer", "persona",
        "jujutsu kaisen", "bleach", "attack on titan", "sword art online", "granblue"
    ],
}

ROMAN_NUMERALS = {
    "1": "i",
    "2": "ii",
    "3": "iii",
    "4": "iv",
    "5": "v",
    "6": "vi",
    "7": "vii",
    "8": "viii",
    "i": "1",
    "ii": "2",
    "iii": "3",
    "iv": "4",
    "v": "5",
    "vi": "6",
}


def _clean_alphanumeric(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "", text).lower()


def _get_search_terms(query: str) -> list[str]:
    raw = query.strip().lower()
    norm = _clean_alphanumeric(raw)
    terms = set()
    terms.add(raw)
    if norm:
        terms.add(norm)

    if raw in EXPANSIONS:
        for exp in EXPANSIONS[raw]:
            terms.add(exp)
            terms.add(_clean_alphanumeric(exp))
    if norm in EXPANSIONS:
        for exp in EXPANSIONS[norm]:
            terms.add(exp)
            terms.add(_clean_alphanumeric(exp))

    tokens = raw.split()
    expanded_tokens = []
    has_replacement = False
    for t in tokens:
        if t in ALIAS_MAP:
            expanded_tokens.append(ALIAS_MAP[t])
            has_replacement = True
        else:
            expanded_tokens.append(t)
    if has_replacement:
        joined = " ".join(expanded_tokens)
        terms.add(joined)
        terms.add(_clean_alphanumeric(joined))

    swapped_tokens = []
    has_num_swap = False
    for t in tokens:
        if t in ROMAN_NUMERALS:
            swapped_tokens.append(ROMAN_NUMERALS[t])
            has_num_swap = True
        elif t in ALIAS_MAP:
            swapped_tokens.append(ALIAS_MAP[t])
            has_num_swap = True
        else:
            swapped_tokens.append(t)
    if has_num_swap:
        joined_swap = " ".join(swapped_tokens)
        terms.add(joined_swap)
        terms.add(_clean_alphanumeric(joined_swap))

    return [t for t in terms if t]


def _build_search_filter(search: str) -> ColumnElement[bool]:
    terms = _get_search_terms(search)
    conds = []

    # Stripped title for punctuation-free LIKE comparison
    stripped_title = Game.title
    for char in ("-", "_", " ", ".", ":", "'", "/", "’", "‘", ",", "!", "(", ")", "[", "]"):
        stripped_title = func.replace(stripped_title, char, "")

    for term in terms:
        conds.append(Game.title.ilike(f"%{term}%"))
        conds.append(Game.category.ilike(f"%{term}%"))
        conds.append(Game.genres.ilike(f"%{term}%"))
        clean = _clean_alphanumeric(term)
        if clean and len(clean) >= 2:
            conds.append(stripped_title.ilike(f"%{clean}%"))

    return or_(*conds)


CATEGORY_SYNONYMS = {
    "fps": "First-person Shooter",
    "shooting": "Shooters",
    "vr": "Virtual Reality",
    "rpg": "Role-playing Game",
    "open-world": "Open World",
    "sci-fi": "Sci-fi",
    "scifi": "Sci-fi",
}


@router.get("/categories", summary="List categories and game counts")
async def list_categories(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(Game.category, func.count(Game.id))
        .where(Game.is_active == True, Game.category.isnot(None))
        .group_by(Game.category)
        .order_by(func.count(Game.id).desc())
    )
    result = await session.execute(stmt)
    rows = result.all()
    return [{"category": r[0], "count": r[1]} for r in rows if r[0]]


@router.get("/random", response_model=GameOut, summary="Get a random game")
async def get_random_game(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(Game)
        .where(Game.is_active == True)
        .options(selectinload(Game.files))
        .order_by(func.random())
        .limit(1)
    )
    result = await session.execute(stmt)
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="No games available")
    return game


@router.get("", response_model=GameListOut, summary="List games (paginated + search + category)")
async def list_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by title, category, or genre"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort: Optional[str] = Query("latest", description="Sort order: latest, top, title, updated"),
    session: AsyncSession = Depends(get_session),
):
    base = select(Game).where(Game.is_active == True).options(selectinload(Game.files))

    # Apply category filter
    if category:
        cat_clean = category.strip().lower()
        cat_resolved = CATEGORY_SYNONYMS.get(cat_clean, cat_clean)
        cat_pattern = f"%{cat_resolved}%"
        cat_raw_pattern = f"%{cat_clean}%"
        base = base.where(
            Game.category.ilike(cat_pattern)
            | Game.genres.ilike(cat_raw_pattern)
            | Game.genres.ilike(cat_pattern)
            | Game.title.ilike(cat_pattern)
        )

    # Apply search filter
    if search:
        search_clean = search.strip()
        search_filter = _build_search_filter(search_clean)
        base = base.where(search_filter)

    # Count total matching
    count_stmt = select(func.count(Game.id)).where(Game.is_active == True)
    if category:
        cat_clean = category.strip().lower()
        cat_resolved = CATEGORY_SYNONYMS.get(cat_clean, cat_clean)
        cat_pattern = f"%{cat_resolved}%"
        cat_raw_pattern = f"%{cat_clean}%"
        count_stmt = count_stmt.where(
            Game.category.ilike(cat_pattern)
            | Game.genres.ilike(cat_raw_pattern)
            | Game.genres.ilike(cat_pattern)
            | Game.title.ilike(cat_pattern)
        )
    if search:
        search_clean = search.strip()
        search_filter = _build_search_filter(search_clean)
        count_stmt = count_stmt.where(search_filter)

    total = (await session.execute(count_stmt)).scalar() or 0

    # Sorting
    if sort == "title":
        stmt = base.order_by(Game.title.asc())
    elif sort == "updated":
        stmt = base.order_by(Game.updated_at.desc().nullslast(), Game.created_at.desc())
    elif sort == "top":
        stmt = base.order_by(Game.top_rank.asc().nullslast(), Game.created_at.desc(), Game.id.desc())
    else:  # latest
        stmt = base.order_by(Game.created_at.desc(), Game.id.desc())

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(stmt)
    games = result.scalars().unique().all()

    pages = (total + page_size - 1) // page_size if total else 0
    return GameListOut(
        items=[GameOut.model_validate(g) for g in games],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{game_id}", response_model=GameOut, summary="Get a single game by id")
async def get_game(game_id: int, session: AsyncSession = Depends(get_session)):
    stmt = select(Game).where(Game.id == game_id).options(selectinload(Game.files))
    result = await session.execute(stmt)
    game = result.scalar_one_or_none()
    if not game or not game.is_active:
        raise HTTPException(status_code=404, detail="Game not found")
    # Clean files: remove internal steamrip website URLs and Buzzheavier (bzzhr.to)
    clean_files = [
        f for f in game.files
        if "://steamrip.com" not in str(f.url).lower()
        and "//steamrip.com" not in str(f.url).lower()
        and "buzzheavier" not in str(f.label or "").lower()
        and "bzzhr.to" not in str(f.url).lower()
        and "buzzheavier" not in str(f.url).lower()
    ]

    # If GoFile mirror is present, show ONLY GoFile as requested
    gofile_files = [
        f for f in clean_files
        if "gofile" in str(f.label or "").lower() or "gofile.io" in str(f.url).lower()
    ]
    if gofile_files:
        game.files = gofile_files
    else:
        game.files = clean_files
    return game