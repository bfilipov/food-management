import json
import os
import logging
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

AI_ENDPOINT = os.getenv("AI_ENDPOINT", "http://0.0.0.0:8081/v1/chat")
AI_TIMEOUT = httpx.Timeout(connect=10.0, read=500.0, write=500.0, pool=5.0)

SYSTEM_PROMPT = '''You are FoodChef AI, a smart meal recommendation assistant for a food waste reduction app.

### Your Goal
Analyze the user's food inventory and suggest practical, delicious meals they can cook TODAY using ingredients that are expiring soon.

### Rules
1. **Prioritize urgency**: Always favor recipes using items expiring within 0-2 days.
2. **Be realistic**: Only suggest meals where the user has ≥80% of required ingredients. List missing items clearly.
3. **Keep it simple**: Prefer recipes with ≤10 ingredients and ≤45 min prep time for weekday meals.
4. **Minimize waste**: Suggest ways to use partial quantities (e.g., "use 2 of 3 bell peppers").
5. **Be creative but practical**: Offer 1-2 "use what you have" hacks alongside standard recipes.
6. **Output STRICT JSON only** — no markdown, no extra text.

### Output Schema
{
  "recommendations": [
    {
      "meal_name": "String",
      "meal_type": "breakfast|lunch|dinner|snack",
      "uses_expiring_items": ["item1", "item2"],
      "ingredients_needed": [
        {"name": "String", "have": true|false, "quantity_needed": "String"}
      ],
      "prep_time_minutes": Number,
      "difficulty": "easy|medium|hard",
      "instructions_summary": "2-3 sentence overview",
      "waste_reduction_tip": "String"
    }
  ],
  "summary": {
    "items_expiring_today": Number,
    "items_expiring_soon": Number,
    "total_meals_possible": Number
  },
  "fallback_suggestion": "One-line idea if user can't cook now (e.g., 'Freeze the chicken for later')"
}'''


def _build_user_prompt(inventory: list[dict], user_prefs: dict = None) -> str:
    """Build the plain-text prompt string to send to the LLM."""
    today = datetime.now().date()

    # Enrich inventory with urgency metadata
    enriched = []
    for item in inventory:
        expires = datetime.strptime(item["expires"], "%Y-%m-%d").date()
        days_left = (expires - today).days
        urgency = (
            "critical" if days_left <= 0 else
            "high" if days_left <= 2 else
            "medium" if days_left <= 4 else
            "low"
        )
        enriched.append({**item, "days_until_expiry": days_left, "urgency": urgency})

    prefs_text = f"\nUser preferences: {json.dumps(user_prefs)}" if user_prefs else ""

    return f"""I have these ingredients in my kitchen:

{json.dumps(enriched, indent=2)}

Today's date: {today.isoformat()}{prefs_text}

Suggest 3 meal recommendations following your rules. Return ONLY valid JSON matching the schema."""


async def get_daily_recommendations(inventory: list[dict], user_prefs: dict = None) -> dict:
    """
    Fetch recommendations from your LLM endpoint.
    Returns a clean Python dict.
    """

    user_prompt = _build_user_prompt(inventory, user_prefs)

    # Full context for the LLM
    full_message = f"System: {SYSTEM_PROMPT}\n\nUser: {user_prompt}"

    payload = {"message": full_message}

    logger.info(f"Requesting AI recommendations (timeout: {AI_TIMEOUT.read}s read)")

    async with httpx.AsyncClient(timeout=AI_TIMEOUT) as client:
        response = await client.post(
            AI_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        raw = response.json()

        if isinstance(raw.get("response"), str):
            try:
                parsed = json.loads(raw["response"])
                logger.info("Parsed AI response successfully")
                return parsed
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response JSON: {e}")
                logger.error(f"Raw response string: {raw['response'][:200]}...")
                raise RuntimeError(f"AI returned invalid JSON: {e}")

        # Fallback: if response is already a dict (for testing)
        if isinstance(raw, dict):
            return raw

        raise RuntimeError(f"Unexpected AI response format: {type(raw)}")