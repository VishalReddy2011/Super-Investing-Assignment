import os
import sys
import asyncio
import warnings
from pathlib import Path
import yfinance as yf
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=UserWarning, module="google.adk")
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

def read_research_pack() -> str:
    return "\n\n".join(
        f"=== {p.name} ===\n{p.read_text(encoding='utf-8')}"
        for p in sorted(Path("research_pack").glob("*.md"))
    )

def fetch_live_data(ticker: str) -> str:
    symbol = ticker if "." in ticker else f"{ticker}.NS"
    info = yf.Ticker(symbol).info
    news = [n["title"] for n in yf.Search(ticker).news[:5]]
    return (
        f"=== LIVE DATA FOR {symbol} ===\n"
        f"Company: {info.get('longName')}\n"
        f"Price: {info.get('currentPrice')} | MCap: {info.get('marketCap')}\n"
        f"P/E: {info.get('trailingPE')} | Margins: {info.get('operatingMargins')}\n"
        f"Description: {info.get('longBusinessSummary')}\n\n"
        f"Recent News:\n" + "\n".join(f"- {t}" for t in news)
    )

async def main(ticker="SRVCABLE", live=False):
    model = os.getenv("MODEL_NAME", "gemini-3.1-flash-lite")
    instruction = Path("system_prompt.txt").read_text(encoding="utf-8")

    agent = LlmAgent(
        name="equity_research_agent",
        model=model,
        instruction=instruction,
        tools=[fetch_live_data] if live else [],
    )
    runner = InMemoryRunner(agent=agent)
    session = await runner.session_service.create_session(user_id="analyst", app_name=runner.app_name)

    if live:
        query = f"Use your tools to fetch live market data for NSE ticker {ticker} and generate the one-page research brief."
    else:
        docs = read_research_pack()
        query = f"Generate the one-page research brief for {ticker} based on these documents:\n\n{docs}"

    msg = types.Content(role="user", parts=[types.Part.from_text(text=query)])

    output = ""
    for event in runner.run(user_id="analyst", session_id=session.id, new_message=msg):
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    output += part.text

    out_dir = Path("briefs")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"brief_{ticker.replace('.', '_')}.md"
    out_file.write_text(output, encoding="utf-8")
    print(f"\nSaved brief to {out_file}\n\n{output}\n")

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "SRVCABLE"
    live = ticker != "SRVCABLE"
    asyncio.run(main(ticker=ticker, live=live))
