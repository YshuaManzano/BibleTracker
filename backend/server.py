from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
import bcrypt
import jwt
import uuid
import httpx
import math
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from typing import List, Optional
from bible_data import (
    BIBLE_BOOKS, READING_PLANS, BADGES, MOOD_SUGGESTIONS, DAILY_VERSES,
    get_plan_chapters, get_all_chapters, CATEGORIES
)

# ──── Config ────
JWT_SECRET = os.environ.get("JWT_SECRET", "bible-app-super-secret-key-change-in-prod-2024")
JWT_ALGORITHM = "HS256"
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
BIBLE_API_BASE = "https://cdn.jsdelivr.net/gh/wldeh/bible-api/bibles"
BIBLE_VERSIONS = {"kjv": "en-kjv", "asv": "en-asv", "web": "en-web"}

# ──── MongoDB ────
mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get("DB_NAME", "bible_app")]

# ──── App ────
app = FastAPI(title="VerseTrack Bible App")
api = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════
# MODELS
# ══════════════════════════════════════════════════
class RegisterInput(BaseModel):
    name: str
    email: str
    password: str

class LoginInput(BaseModel):
    email: str
    password: str

class NoteInput(BaseModel):
    book_slug: str
    chapter: int
    text: str

class NoteUpdate(BaseModel):
    text: str

class MarkReadInput(BaseModel):
    plan_id: str
    book_slug: str
    chapter: int

class RecalculateInput(BaseModel):
    plan_id: str

class CreateCircleInput(BaseModel):
    name: str
    description: str = ""
    privacy: str = "public"  # "public" or "private"
    plan_mode: str = "individual"  # "shared" or "individual"
    plan_id: Optional[str] = None  # for shared mode

class JoinCircleInput(BaseModel):
    invite_code: str

# ══════════════════════════════════════════════════
# AUTH UTILITIES
# ══════════════════════════════════════════════════
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "access"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=30), "type": "refresh"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ══════════════════════════════════════════════════
# AUTH ENDPOINTS
# ══════════════════════════════════════════════════
@api.post("/auth/register")
async def register(data: RegisterInput):
    email = data.email.strip().lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_doc = {
        "name": data.name.strip(),
        "email": email,
        "password_hash": hash_password(data.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "grace_days_used": {},
        "theme": "auto",
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    token = create_access_token(user_id, email)
    return {"token": token, "user": {"id": user_id, "name": user_doc["name"], "email": email}}

@api.post("/auth/login")
async def login(data: LoginInput):
    email = data.email.strip().lower()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user_id = str(user["_id"])
    token = create_access_token(user_id, email)
    return {"token": token, "user": {"id": user_id, "name": user["name"], "email": email}}

@api.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {"id": user["_id"], "name": user["name"], "email": user["email"]}

# ══════════════════════════════════════════════════
# BIBLE DATA ENDPOINTS
# ══════════════════════════════════════════════════
@api.get("/bible/books")
async def get_books():
    return {"books": BIBLE_BOOKS, "categories": CATEGORIES}

@api.get("/bible/chapter/{version}/{book_slug}/{chapter}")
async def get_chapter(version: str, book_slug: str, chapter: int):
    if version not in BIBLE_VERSIONS:
        raise HTTPException(status_code=400, detail=f"Version must be one of: {list(BIBLE_VERSIONS.keys())}")
    book = next((b for b in BIBLE_BOOKS if b["slug"] == book_slug), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if chapter < 1 or chapter > book["chapters"]:
        raise HTTPException(status_code=400, detail=f"Chapter must be between 1 and {book['chapters']}")
    # Check cache
    cache_key = f"{version}:{book_slug}:{chapter}"
    cached = await db.bible_cache.find_one({"key": cache_key}, {"_id": 0})
    if cached:
        return {"book": book["name"], "chapter": chapter, "version": version, "verses": cached.get("verses", []), "text": cached.get("text", "")}
    # Fetch from API
    api_version = BIBLE_VERSIONS[version]
    url = f"{BIBLE_API_BASE}/{api_version}/books/{book_slug}/chapters/{chapter}.json"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client_http:
            resp = await client_http.get(url)
            if resp.status_code == 200:
                raw = resp.json()
                # API returns {data: [{book, chapter, verse, text}]} format
                raw_verses = raw.get("data") or raw.get("verses") or []
                # Deduplicate (API sometimes returns duplicates)
                seen = set()
                verses = []
                for v in raw_verses:
                    vnum = int(v.get("verse", 0))
                    if vnum not in seen:
                        seen.add(vnum)
                        verses.append({"verse": vnum, "text": v.get("text", "")})
                verses.sort(key=lambda x: x["verse"])
                full_text = " ".join(v["text"] for v in verses)
                await db.bible_cache.insert_one({"key": cache_key, "verses": verses, "text": full_text, "fetched_at": datetime.now(timezone.utc).isoformat()})
                return {"book": book["name"], "chapter": chapter, "version": version, "verses": verses, "text": full_text}
            else:
                raise HTTPException(status_code=404, detail="Chapter text not available from API")
    except httpx.RequestError as e:
        logger.error(f"Bible API error: {e}")
        raise HTTPException(status_code=502, detail="Failed to fetch Bible text")

@api.get("/bible/daily-verse")
async def get_daily_verse():
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    verse = DAILY_VERSES[day_of_year % len(DAILY_VERSES)]
    return verse

# ══════════════════════════════════════════════════
# READING PLANS
# ══════════════════════════════════════════════════
@api.get("/plans")
async def list_plans():
    return {"plans": READING_PLANS}

@api.post("/plans/activate/{plan_id}")
async def activate_plan(plan_id: str, user: dict = Depends(get_current_user)):
    plan = next((p for p in READING_PLANS if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    # Check if already active
    existing = await db.user_plans.find_one({"user_id": user["_id"], "plan_id": plan_id, "status": "active"})
    if existing:
        raise HTTPException(status_code=400, detail="Plan already active")
    chapters = get_plan_chapters(plan_id)
    total = len(chapters)
    per_day = math.ceil(total / plan["duration_days"])
    # Create daily assignments
    daily_assignments = []
    for day in range(plan["duration_days"]):
        start_idx = day * per_day
        end_idx = min((day + 1) * per_day, total)
        if start_idx < total:
            daily_assignments.append({
                "day": day + 1,
                "chapters": chapters[start_idx:end_idx],
                "completed": False,
                "completed_chapters": [],
            })
    user_plan = {
        "user_id": user["_id"],
        "plan_id": plan_id,
        "plan_name": plan["name"],
        "status": "active",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "duration_days": plan["duration_days"],
        "total_chapters": total,
        "completed_chapters": 0,
        "daily_assignments": daily_assignments,
        "current_day": 1,
    }
    result = await db.user_plans.insert_one(user_plan)
    user_plan.pop("_id", None)
    user_plan["id"] = str(result.inserted_id)
    return user_plan

@api.get("/plans/active")
async def get_active_plans(user: dict = Depends(get_current_user)):
    plans = await db.user_plans.find({"user_id": user["_id"], "status": "active"}).to_list(20)
    result = []
    for p in plans:
        p["id"] = str(p["_id"])
        del p["_id"]
        result.append(p)
    return {"plans": result}

@api.get("/plans/user/{plan_doc_id}")
async def get_user_plan(plan_doc_id: str, user: dict = Depends(get_current_user)):
    try:
        plan = await db.user_plans.find_one({"_id": ObjectId(plan_doc_id), "user_id": user["_id"]})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid plan ID")
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan["id"] = str(plan["_id"])
    del plan["_id"]
    return plan

# ══════════════════════════════════════════════════
# PROGRESS TRACKING
# ══════════════════════════════════════════════════
@api.post("/progress/mark-read")
async def mark_chapter_read(data: MarkReadInput, user: dict = Depends(get_current_user)):
    user_id = user["_id"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Log the reading
    await db.reading_log.insert_one({
        "user_id": user_id,
        "book_slug": data.book_slug,
        "chapter": data.chapter,
        "date": today,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    # Update user plan
    try:
        plan = await db.user_plans.find_one({"_id": ObjectId(data.plan_id), "user_id": user_id})
    except Exception:
        plan = None
    if plan:
        chapter_key = f"{data.book_slug}:{data.chapter}"
        updated = False
        for day_data in plan.get("daily_assignments", []):
            for ch in day_data.get("chapters", []):
                if ch["book_slug"] == data.book_slug and ch["chapter"] == data.chapter:
                    if chapter_key not in day_data.get("completed_chapters", []):
                        day_data.setdefault("completed_chapters", []).append(chapter_key)
                        all_keys = [f"{c['book_slug']}:{c['chapter']}" for c in day_data["chapters"]]
                        if all(k in day_data["completed_chapters"] for k in all_keys):
                            day_data["completed"] = True
                        updated = True
                        break
            if updated:
                break
        completed_count = sum(len(d.get("completed_chapters", [])) for d in plan.get("daily_assignments", []))
        await db.user_plans.update_one(
            {"_id": plan["_id"]},
            {"$set": {"daily_assignments": plan["daily_assignments"], "completed_chapters": completed_count}}
        )
    # Check and award badges
    await check_badges(user_id)
    return {"status": "ok", "date": today}

@api.get("/progress/heatmap")
async def get_heatmap(user: dict = Depends(get_current_user)):
    # Get reading logs for last 365 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")
    logs = await db.reading_log.find(
        {"user_id": user["_id"], "date": {"$gte": cutoff}}, {"_id": 0, "date": 1}
    ).to_list(10000)
    # Count chapters per day
    day_counts = {}
    for log in logs:
        d = log["date"]
        day_counts[d] = day_counts.get(d, 0) + 1
    return {"heatmap": day_counts}

@api.get("/progress/streak")
async def get_streak(user: dict = Depends(get_current_user)):
    user_id = user["_id"]
    today = datetime.now(timezone.utc).date()
    # Get all unique reading dates, sorted desc
    logs = await db.reading_log.find({"user_id": user_id}, {"_id": 0, "date": 1}).to_list(10000)
    read_dates = sorted(set(log["date"] for log in logs), reverse=True)
    if not read_dates:
        return {"current_streak": 0, "longest_streak": 0, "grace_day_available": True, "total_days_read": 0}
    # Calculate streak with grace day logic
    user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    grace_days_used = user_doc.get("grace_days_used", {})
    current_month = today.strftime("%Y-%m")
    grace_available = grace_days_used.get(current_month, 0) < 1
    streak = 0
    grace_used_in_streak = False
    check_date = today
    for _ in range(400):
        date_str = check_date.strftime("%Y-%m-%d")
        if date_str in read_dates:
            streak += 1
        elif not grace_used_in_streak and grace_available:
            streak += 1
            grace_used_in_streak = True
        else:
            break
        check_date -= timedelta(days=1)
    # Longest streak (simple)
    longest = 0
    current = 0
    for i, d in enumerate(sorted(read_dates)):
        dt = datetime.strptime(d, "%Y-%m-%d").date()
        if i == 0:
            current = 1
        else:
            prev = datetime.strptime(sorted(read_dates)[i-1], "%Y-%m-%d").date()
            if (dt - prev).days == 1:
                current += 1
            elif (dt - prev).days == 2:
                current += 1  # grace
            else:
                current = 1
        longest = max(longest, current)
    return {
        "current_streak": streak,
        "longest_streak": max(longest, streak),
        "grace_day_available": grace_available and not grace_used_in_streak,
        "total_days_read": len(read_dates),
    }

@api.post("/progress/use-grace-day")
async def use_grace_day(user: dict = Depends(get_current_user)):
    user_id = user["_id"]
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    grace_days_used = user_doc.get("grace_days_used", {})
    if grace_days_used.get(current_month, 0) >= 1:
        raise HTTPException(status_code=400, detail="Grace day already used this month")
    grace_days_used[current_month] = 1
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"grace_days_used": grace_days_used}})
    return {"status": "ok", "message": "Grace day used successfully"}

@api.post("/plans/recalculate")
async def recalculate_plan(data: RecalculateInput, user: dict = Depends(get_current_user)):
    """Smart catch-up: redistribute remaining chapters over remaining days."""
    try:
        plan = await db.user_plans.find_one({"_id": ObjectId(data.plan_id), "user_id": user["_id"]})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid plan ID")
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    # Gather all completed chapter keys
    completed_keys = set()
    for d in plan.get("daily_assignments", []):
        completed_keys.update(d.get("completed_chapters", []))
    # Get remaining chapters
    plan_def = next((p for p in READING_PLANS if p["id"] == plan["plan_id"]), None)
    if not plan_def:
        raise HTTPException(status_code=404, detail="Plan definition not found")
    all_chapters = get_plan_chapters(plan["plan_id"])
    remaining = [ch for ch in all_chapters if f"{ch['book_slug']}:{ch['chapter']}" not in completed_keys]
    if not remaining:
        return {"message": "All chapters completed!"}
    # Spread over next 7 days or remaining plan days
    remaining_days = max(7, plan["duration_days"] - len(completed_keys) // max(1, math.ceil(len(all_chapters) / plan["duration_days"])))
    remaining_days = min(remaining_days, 60)
    per_day = math.ceil(len(remaining) / remaining_days)
    new_assignments = []
    for day in range(remaining_days):
        start_idx = day * per_day
        end_idx = min((day + 1) * per_day, len(remaining))
        if start_idx < len(remaining):
            new_assignments.append({
                "day": day + 1,
                "chapters": remaining[start_idx:end_idx],
                "completed": False,
                "completed_chapters": [],
            })
    # Add back completed days
    completed_assignments = [d for d in plan["daily_assignments"] if d.get("completed")]
    all_assignments = completed_assignments + new_assignments
    # Renumber
    for i, a in enumerate(all_assignments):
        a["day"] = i + 1
    await db.user_plans.update_one(
        {"_id": plan["_id"]},
        {"$set": {"daily_assignments": all_assignments, "duration_days": len(all_assignments)}}
    )
    return {"message": f"Plan recalculated! {len(remaining)} chapters spread over {len(new_assignments)} days.", "new_per_day": per_day}

# ══════════════════════════════════════════════════
# BOOKS COMPLETION STATUS
# ══════════════════════════════════════════════════
@api.get("/progress/books-status")
async def get_books_status(user: dict = Depends(get_current_user)):
    """Get completion status for each Bible book."""
    logs = await db.reading_log.find({"user_id": user["_id"]}, {"_id": 0, "book_slug": 1, "chapter": 1}).to_list(50000)
    completed = {}
    for log in logs:
        key = log["book_slug"]
        completed.setdefault(key, set()).add(log["chapter"])
    result = []
    for book in BIBLE_BOOKS:
        read_chapters = completed.get(book["slug"], set())
        result.append({
            "slug": book["slug"],
            "name": book["name"],
            "abbr": book["abbr"],
            "chapters": book["chapters"],
            "read": len(read_chapters),
            "testament": book["testament"],
            "category": book["category"],
            "status": "completed" if len(read_chapters) >= book["chapters"] else ("in_progress" if len(read_chapters) > 0 else "unread"),
        })
    return {"books": result}

# ══════════════════════════════════════════════════
# NOTES
# ══════════════════════════════════════════════════
@api.post("/notes")
async def create_note(data: NoteInput, user: dict = Depends(get_current_user)):
    note = {
        "user_id": user["_id"],
        "book_slug": data.book_slug,
        "chapter": data.chapter,
        "text": data.text,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await db.notes.insert_one(note)
    note["id"] = str(result.inserted_id)
    note.pop("_id", None)
    return note

@api.get("/notes")
async def list_notes(user: dict = Depends(get_current_user), book_slug: Optional[str] = None, chapter: Optional[int] = None):
    query = {"user_id": user["_id"]}
    if book_slug:
        query["book_slug"] = book_slug
    if chapter is not None:
        query["chapter"] = chapter
    notes = await db.notes.find(query).sort("created_at", -1).to_list(200)
    result = []
    for n in notes:
        n["id"] = str(n["_id"])
        del n["_id"]
        result.append(n)
    return {"notes": result}

@api.put("/notes/{note_id}")
async def update_note(note_id: str, data: NoteUpdate, user: dict = Depends(get_current_user)):
    try:
        result = await db.notes.update_one(
            {"_id": ObjectId(note_id), "user_id": user["_id"]},
            {"$set": {"text": data.text, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid note ID")
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"status": "updated"}

@api.delete("/notes/{note_id}")
async def delete_note(note_id: str, user: dict = Depends(get_current_user)):
    try:
        result = await db.notes.delete_one({"_id": ObjectId(note_id), "user_id": user["_id"]})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid note ID")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"status": "deleted"}

# ══════════════════════════════════════════════════
# AI SUMMARIES & MOOD
# ══════════════════════════════════════════════════
@api.get("/ai/summary/{book_slug}/{chapter}")
async def get_ai_summary(book_slug: str, chapter: int, user: dict = Depends(get_current_user)):
    book = next((b for b in BIBLE_BOOKS if b["slug"] == book_slug), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    # Check cache
    cache_key = f"summary:{book_slug}:{chapter}"
    cached = await db.ai_cache.find_one({"key": cache_key}, {"_id": 0})
    if cached:
        return {"summary": cached["summary"], "cached": True}
    if not EMERGENT_LLM_KEY:
        return {"summary": f"AI summaries require API configuration. This is {book['name']} chapter {chapter}.", "cached": False}
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"summary-{cache_key}-{uuid.uuid4().hex[:8]}",
            system_message="You are a Bible study assistant. Provide concise, insightful chapter summaries in 2-3 sentences. Focus on key themes, events, and spiritual significance. Be respectful and scholarly."
        ).with_model("openai", "gpt-5.2")
        msg = UserMessage(text=f"Provide a brief TL;DR summary of {book['name']} chapter {chapter} from the Bible. Include the main events/themes and why this chapter matters in the broader narrative.")
        summary = await chat.send_message(msg)
        # Cache it
        await db.ai_cache.insert_one({"key": cache_key, "summary": summary, "created_at": datetime.now(timezone.utc).isoformat()})
        return {"summary": summary, "cached": False}
    except Exception as e:
        logger.error(f"AI summary error: {e}")
        return {"summary": f"Unable to generate summary for {book['name']} {chapter}. Please try again later.", "cached": False}

@api.get("/ai/mood-suggestions")
async def get_mood_suggestions():
    return {"moods": MOOD_SUGGESTIONS}

# ══════════════════════════════════════════════════
# BADGES
# ══════════════════════════════════════════════════
async def check_badges(user_id: str):
    """Check and award any new badges."""
    logs = await db.reading_log.find({"user_id": user_id}, {"_id": 0, "book_slug": 1, "chapter": 1}).to_list(50000)
    completed_books = {}
    for log in logs:
        completed_books.setdefault(log["book_slug"], set()).add(log["chapter"])
    fully_completed = set()
    for book in BIBLE_BOOKS:
        if len(completed_books.get(book["slug"], set())) >= book["chapters"]:
            fully_completed.add(book["slug"])
    # Check category badges
    for badge in BADGES:
        if badge["category"] == "streak":
            continue  # Handled separately
        if badge["category"] == "all":
            earned = len(fully_completed) >= len(BIBLE_BOOKS)
        elif badge["category"] == "all_nt":
            nt_slugs = {b["slug"] for b in BIBLE_BOOKS if b["testament"] == "NT"}
            earned = nt_slugs.issubset(fully_completed)
        else:
            cat_slugs = {b["slug"] for b in BIBLE_BOOKS if b["category"] == badge["category"]}
            earned = cat_slugs.issubset(fully_completed)
        if earned:
            existing = await db.badges.find_one({"user_id": user_id, "badge_id": badge["id"]})
            if not existing:
                await db.badges.insert_one({
                    "user_id": user_id,
                    "badge_id": badge["id"],
                    "earned_at": datetime.now(timezone.utc).isoformat(),
                })
    # Check streak badges
    streak_data = await _calc_streak(user_id)
    streak = streak_data["current_streak"]
    for badge in BADGES:
        if badge["category"] == "streak":
            threshold = int(badge["id"].split("-")[1])
            if streak >= threshold:
                existing = await db.badges.find_one({"user_id": user_id, "badge_id": badge["id"]})
                if not existing:
                    await db.badges.insert_one({
                        "user_id": user_id,
                        "badge_id": badge["id"],
                        "earned_at": datetime.now(timezone.utc).isoformat(),
                    })

async def _calc_streak(user_id: str) -> dict:
    logs = await db.reading_log.find({"user_id": user_id}, {"_id": 0, "date": 1}).to_list(10000)
    read_dates = sorted(set(log["date"] for log in logs), reverse=True)
    if not read_dates:
        return {"current_streak": 0}
    today = datetime.now(timezone.utc).date()
    streak = 0
    check_date = today
    for _ in range(400):
        date_str = check_date.strftime("%Y-%m-%d")
        if date_str in read_dates:
            streak += 1
        else:
            break
        check_date -= timedelta(days=1)
    return {"current_streak": streak}

@api.get("/badges")
async def get_badges(user: dict = Depends(get_current_user)):
    earned = await db.badges.find({"user_id": user["_id"]}, {"_id": 0}).to_list(100)
    earned_ids = {b["badge_id"] for b in earned}
    result = []
    for badge in BADGES:
        result.append({
            **badge,
            "earned": badge["id"] in earned_ids,
            "earned_at": next((b["earned_at"] for b in earned if b["badge_id"] == badge["id"]), None),
        })
    return {"badges": result}

# ══════════════════════════════════════════════════
# READING CIRCLES
# ══════════════════════════════════════════════════
import secrets
import string

def generate_invite_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

@api.post("/circles")
async def create_circle(data: CreateCircleInput, user: dict = Depends(get_current_user)):
    invite_code = generate_invite_code()
    # Ensure unique
    while await db.circles.find_one({"invite_code": invite_code}):
        invite_code = generate_invite_code()
    circle = {
        "name": data.name.strip(),
        "description": data.description.strip(),
        "privacy": data.privacy if data.privacy in ("public", "private") else "public",
        "plan_mode": data.plan_mode if data.plan_mode in ("shared", "individual") else "individual",
        "plan_id": data.plan_id,
        "creator_id": user["_id"],
        "creator_name": user["name"],
        "invite_code": invite_code,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "members": [{
            "user_id": user["_id"],
            "name": user["name"],
            "status": "active",
            "role": "creator",
            "joined_at": datetime.now(timezone.utc).isoformat(),
        }],
    }
    result = await db.circles.insert_one(circle)
    circle["id"] = str(result.inserted_id)
    circle.pop("_id", None)
    return circle

@api.get("/circles")
async def list_my_circles(user: dict = Depends(get_current_user)):
    circles = await db.circles.find({"members.user_id": user["_id"]}).to_list(50)
    result = []
    for c in circles:
        c["id"] = str(c["_id"])
        del c["_id"]
        active_members = [m for m in c.get("members", []) if m["status"] == "active"]
        c["member_count"] = len(active_members)
        result.append(c)
    return {"circles": result}

@api.get("/circles/invite/{invite_code}")
async def get_circle_by_invite(invite_code: str):
    circle = await db.circles.find_one({"invite_code": invite_code})
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    active_members = [m for m in circle.get("members", []) if m["status"] == "active"]
    return {
        "id": str(circle["_id"]),
        "name": circle["name"],
        "description": circle["description"],
        "privacy": circle["privacy"],
        "plan_mode": circle["plan_mode"],
        "creator_name": circle.get("creator_name", "Unknown"),
        "member_count": len(active_members),
        "invite_code": invite_code,
    }

@api.post("/circles/join")
async def join_circle(data: JoinCircleInput, user: dict = Depends(get_current_user)):
    circle = await db.circles.find_one({"invite_code": data.invite_code})
    if not circle:
        raise HTTPException(status_code=404, detail="Invalid invite code")
    # Check if already a member
    for m in circle.get("members", []):
        if m["user_id"] == user["_id"]:
            if m["status"] == "active":
                raise HTTPException(status_code=400, detail="Already a member")
            if m["status"] == "pending":
                raise HTTPException(status_code=400, detail="Join request already pending")
    status = "active" if circle["privacy"] == "public" else "pending"
    new_member = {
        "user_id": user["_id"],
        "name": user["name"],
        "status": status,
        "role": "member",
        "joined_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.circles.update_one({"_id": circle["_id"]}, {"$push": {"members": new_member}})
    return {"status": status, "message": "Joined successfully!" if status == "active" else "Join request sent. Waiting for approval."}

@api.post("/circles/{circle_id}/approve/{member_user_id}")
async def approve_member(circle_id: str, member_user_id: str, user: dict = Depends(get_current_user)):
    try:
        circle = await db.circles.find_one({"_id": ObjectId(circle_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid circle ID")
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    if circle["creator_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Only the creator can approve members")
    result = await db.circles.update_one(
        {"_id": ObjectId(circle_id), "members.user_id": member_user_id},
        {"$set": {"members.$.status": "active"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"status": "approved"}

@api.post("/circles/{circle_id}/reject/{member_user_id}")
async def reject_member(circle_id: str, member_user_id: str, user: dict = Depends(get_current_user)):
    try:
        circle = await db.circles.find_one({"_id": ObjectId(circle_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid circle ID")
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    if circle["creator_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Only the creator can reject members")
    await db.circles.update_one(
        {"_id": ObjectId(circle_id)},
        {"$pull": {"members": {"user_id": member_user_id, "status": "pending"}}}
    )
    return {"status": "rejected"}

@api.delete("/circles/{circle_id}/leave")
async def leave_circle(circle_id: str, user: dict = Depends(get_current_user)):
    try:
        circle = await db.circles.find_one({"_id": ObjectId(circle_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid circle ID")
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    if circle["creator_id"] == user["_id"]:
        raise HTTPException(status_code=400, detail="Creator cannot leave. Delete the circle instead.")
    await db.circles.update_one(
        {"_id": ObjectId(circle_id)},
        {"$pull": {"members": {"user_id": user["_id"]}}}
    )
    return {"status": "left"}

@api.get("/circles/{circle_id}")
async def get_circle_detail(circle_id: str, user: dict = Depends(get_current_user)):
    try:
        circle = await db.circles.find_one({"_id": ObjectId(circle_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid circle ID")
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    # Check membership
    is_member = any(m["user_id"] == user["_id"] and m["status"] == "active" for m in circle.get("members", []))
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this circle")
    # Build member progress
    members_progress = []
    for m in circle.get("members", []):
        if m["status"] != "active":
            continue
        # Get total chapters read by this member
        total_read = await db.reading_log.count_documents({"user_id": m["user_id"]})
        # Get streak
        logs = await db.reading_log.find({"user_id": m["user_id"]}, {"_id": 0, "date": 1}).to_list(10000)
        read_dates = sorted(set(log["date"] for log in logs), reverse=True)
        streak = 0
        if read_dates:
            today = datetime.now(timezone.utc).date()
            check_date = today
            for _ in range(400):
                if check_date.strftime("%Y-%m-%d") in read_dates:
                    streak += 1
                else:
                    break
                check_date -= timedelta(days=1)
        # If shared plan mode, get plan progress
        plan_progress = None
        if circle.get("plan_mode") == "shared" and circle.get("plan_id"):
            user_plan = await db.user_plans.find_one({"user_id": m["user_id"], "plan_id": circle["plan_id"], "status": "active"})
            if user_plan:
                plan_progress = {
                    "completed": user_plan.get("completed_chapters", 0),
                    "total": user_plan.get("total_chapters", 1),
                    "percent": round((user_plan.get("completed_chapters", 0) / max(user_plan.get("total_chapters", 1), 1)) * 100),
                }
        members_progress.append({
            "user_id": m["user_id"],
            "name": m["name"],
            "role": m["role"],
            "joined_at": m["joined_at"],
            "total_chapters_read": total_read,
            "current_streak": streak,
            "plan_progress": plan_progress,
        })
    # Get pending members if creator
    pending = []
    if circle["creator_id"] == user["_id"]:
        pending = [m for m in circle.get("members", []) if m["status"] == "pending"]
    circle["id"] = str(circle["_id"])
    del circle["_id"]
    circle["members_progress"] = members_progress
    circle["pending_members"] = pending
    circle["is_creator"] = circle["creator_id"] == user["_id"]
    return circle

@api.delete("/circles/{circle_id}")
async def delete_circle(circle_id: str, user: dict = Depends(get_current_user)):
    try:
        circle = await db.circles.find_one({"_id": ObjectId(circle_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid circle ID")
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    if circle["creator_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Only the creator can delete the circle")
    await db.circles.delete_one({"_id": ObjectId(circle_id)})
    return {"status": "deleted"}

# ══════════════════════════════════════════════════
# DASHBOARD STATS
# ══════════════════════════════════════════════════
@api.get("/dashboard")
async def get_dashboard(user: dict = Depends(get_current_user)):
    user_id = user["_id"]
    # Active plans count
    active_plans = await db.user_plans.count_documents({"user_id": user_id, "status": "active"})
    # Total chapters read
    total_read = await db.reading_log.count_documents({"user_id": user_id})
    # Notes count
    notes_count = await db.notes.count_documents({"user_id": user_id})
    # Badges earned
    badges_earned = await db.badges.count_documents({"user_id": user_id})
    return {
        "active_plans": active_plans,
        "total_chapters_read": total_read,
        "notes_count": notes_count,
        "badges_earned": badges_earned,
    }

# ══════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════
@api.put("/settings/theme")
async def update_theme(request: Request, user: dict = Depends(get_current_user)):
    body = await request.json()
    theme = body.get("theme", "auto")
    if theme not in ("light", "dark", "auto"):
        raise HTTPException(status_code=400, detail="Theme must be 'light', 'dark', or 'auto'")
    await db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": {"theme": theme}})
    return {"theme": theme}

@api.get("/settings")
async def get_settings(user: dict = Depends(get_current_user)):
    user_doc = await db.users.find_one({"_id": ObjectId(user["_id"])})
    return {"theme": user_doc.get("theme", "auto")}

# ══════════════════════════════════════════════════
# STARTUP
# ══════════════════════════════════════════════════
@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.reading_log.create_index([("user_id", 1), ("date", 1)])
    await db.bible_cache.create_index("key", unique=True)
    await db.ai_cache.create_index("key", unique=True)
    await db.notes.create_index([("user_id", 1), ("book_slug", 1), ("chapter", 1)])
    await db.badges.create_index([("user_id", 1), ("badge_id", 1)], unique=True)
    await db.user_plans.create_index([("user_id", 1), ("plan_id", 1)])
    await db.circles.create_index("invite_code", unique=True)
    await db.circles.create_index([("members.user_id", 1)])
    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@bibleapp.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({
            "name": "Admin",
            "email": admin_email,
            "password_hash": hash_password(admin_password),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "grace_days_used": {},
            "theme": "auto",
            "role": "admin",
        })
        logger.info(f"Admin user created: {admin_email}")
    logger.info("Bible App API started successfully")

@app.on_event("shutdown")
async def shutdown():
    client.close()

# Include router
app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
