import os

import httpx


async def generate_recommendation(account, health_result: dict) -> str | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    signals_text = "\n".join(f"- {s}" for s in health_result["signals"])
    user_message = (
        f"Company: {account.company_name}\n"
        f"Industry: {account.industry or 'Unknown'}\n"
        f"Health Score: {health_result['score']}/100\n"
        f"Risk Level: {health_result['risk_level']}\n"
        f"Signals:\n{signals_text}"
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 256,
                    "system": (
                        "You are an expert Customer Success Manager. Given account data "
                        "and health signals, provide a concise, actionable recommendation "
                        "in 2-3 sentences. Be specific, not generic."
                    ),
                    "messages": [{"role": "user", "content": user_message}],
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
    except Exception:
        return None
