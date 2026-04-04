import anthropic
import datetime
import os

# 오늘 날짜
today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
date_str = today.strftime("%Y.%m.%d")
day_str = ["MON","TUE","WED","THU","FRI","SAT","SUN"][today.weekday()]

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

print(f"📰 {date_str} 뉴스 브리핑 생성 시작...")

# Claude API로 뉴스 수집 + JSON 생성
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=3000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{
        "role": "user",
        "content": f"""오늘({date_str}) 기준 국내 뉴스만 검색해서 각 카테고리별로 3개씩 추출하고 아래 JSON 형식으로만 응답해줘. 다른 텍스트는 절대 포함하지 마.

검색 조건:
- 반드시 한국 뉴스 사이트(네이버뉴스, 전자신문, 아이티조선, AI타임스, 디지털데일리 등) 기준으로 검색
- 제목과 요약은 반드시 한국어로 작성
- 오늘 날짜({date_str}) 기준 최신 기사 우선

카테고리: AI(인공지능), 유튜브, 마케팅

JSON 형식:
{{
  "ai": [
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}}
  ],
  "youtube": [
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}}
  ],
  "marketing": [
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}}
  ]
}}"""
    }]
)

# 응답에서 텍스트 추출
raw = ""
for block in response.content:
    if block.type == "text":
        raw += block.text

# JSON 파싱
import json, re
match = re.search(r'\{.*\}', raw, re.DOTALL)
if not match:
    raise ValueError("JSON을 찾을 수 없습니다")

data = json.loads(match.group())
ai_news = data["ai"]
yt_news = data["youtube"]
mk_news = data["marketing"]

print(f"✅ 뉴스 수집 완료 — AI {len(ai_news)}건, 유튜브 {len(yt_news)}건, 마케팅 {len(mk_news)}건")

# 카드 HTML 생성
def make_cards(items, start_num):
    html = ""
    for i, item in enumerate(items):
        num = str(start_num + i).zfill(2)
        html += f"""
    <div class="card">
      <div class="card-num">{num}</div>
      <div>
        <div class="card-title">{item['title']}</div>
        <div class="card-summary">{item['summary']}</div>
      </div>
    </div>"""
    return html

# HTML 페이지 생성
html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📰 오늘의 뉴스 브리핑 · {date_str}</title>
<meta property="og:title" content="📰 오늘의 뉴스 브리핑 · {date_str}">
<meta property="og:description" content="AI · 유튜브 · 마케팅 최신 뉴스 9선">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700;900&family=DM+Mono:wght@400;500&display=swap');
  :root {{
    --bg: #0f0e0c; --card: #1a1916; --border: #2e2c28;
    --accent-ai: #f5c842; --accent-yt: #ff4444; --accent-mk: #4af0a0;
    --text: #f0ece0; --muted: #8a8678; --num: #3a3830;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Noto Serif KR', serif; min-height: 100vh; padding: 0 0 80px; }}
  .header {{ padding: 48px 24px 32px; border-bottom: 1px solid var(--border); position: relative; overflow: hidden; }}
  .header::before {{ content: ''; position: absolute; top: -60px; right: -60px; width: 240px; height: 240px; background: radial-gradient(circle, rgba(245,200,66,0.12) 0%, transparent 70%); pointer-events: none; }}
  .date-tag {{ font-family: 'DM Mono', monospace; font-size: 11px; letter-spacing: 0.15em; color: var(--muted); text-transform: uppercase; margin-bottom: 12px; }}
  h1 {{ font-size: clamp(28px, 7vw, 42px); font-weight: 900; line-height: 1.1; letter-spacing: -0.02em; }}
  h1 span {{ color: var(--accent-ai); }}
  .subtitle {{ margin-top: 10px; font-size: 14px; color: var(--muted); }}
  .section {{ padding: 32px 24px 0; opacity: 0; transform: translateY(16px); animation: fadeUp 0.5s forwards; }}
  .section:nth-child(2) {{ animation-delay: 0.1s; }}
  .section:nth-child(3) {{ animation-delay: 0.2s; }}
  .section:nth-child(4) {{ animation-delay: 0.3s; }}
  @keyframes fadeUp {{ to {{ opacity: 1; transform: none; }} }}
  .cat-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }}
  .cat-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
  .cat-label {{ font-family: 'DM Mono', monospace; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; }}
  .cat-line {{ flex: 1; height: 1px; background: var(--border); }}
  .cards {{ display: flex; flex-direction: column; gap: 2px; }}
  .card {{ background: var(--card); border-radius: 4px; padding: 20px; display: grid; grid-template-columns: 40px 1fr; gap: 0 14px; transition: background 0.2s; }}
  .card:hover {{ background: #211f1c; }}
  .card-num {{ font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 500; color: var(--num); line-height: 1; padding-top: 2px; text-align: right; }}
  .card-title {{ font-size: 15px; font-weight: 700; line-height: 1.45; margin-bottom: 6px; }}
  .card-summary {{ font-size: 13px; color: var(--muted); line-height: 1.6; }}
  .card-summary::before {{ content: '→ '; font-family: 'DM Mono', monospace; }}
  .ai .card:hover .card-title {{ color: var(--accent-ai); }}
  .yt .card:hover .card-title {{ color: var(--accent-yt); }}
  .mk .card:hover .card-title {{ color: var(--accent-mk); }}
  .footer {{ margin: 40px 24px 0; padding-top: 24px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .footer-left {{ font-family: 'DM Mono', monospace; font-size: 11px; color: var(--muted); letter-spacing: 0.1em; }}
  .share-btn {{ display: inline-flex; align-items: center; gap: 8px; background: #FAE100; color: #3A1D1D; font-family: 'Noto Serif KR', serif; font-weight: 700; font-size: 14px; padding: 10px 20px; border-radius: 50px; border: none; cursor: pointer; text-decoration: none; transition: transform 0.15s, box-shadow 0.15s; }}
  .share-btn:hover {{ transform: translateY(-1px); box-shadow: 0 6px 20px rgba(250,225,0,0.3); }}
</style>
</head>
<body>
<div class="header">
  <div class="date-tag">NEWS BRIEFING · {date_str} {day_str}</div>
  <h1>오늘의<br><span>뉴스 브리핑</span></h1>
  <div class="subtitle">AI · 유튜브 · 마케팅 최신 뉴스 9선</div>
</div>

<div class="section ai">
  <div class="cat-header">
    <div class="cat-dot" style="background:var(--accent-ai)"></div>
    <span class="cat-label" style="color:var(--accent-ai)">🤖 AI</span>
    <div class="cat-line"></div>
  </div>
  <div class="cards">{make_cards(ai_news, 1)}</div>
</div>

<div class="section yt">
  <div class="cat-header">
    <div class="cat-dot" style="background:var(--accent-yt)"></div>
    <span class="cat-label" style="color:var(--accent-yt)">📺 유튜브</span>
    <div class="cat-line"></div>
  </div>
  <div class="cards">{make_cards(yt_news, 4)}</div>
</div>

<div class="section mk">
  <div class="cat-header">
    <div class="cat-dot" style="background:var(--accent-mk)"></div>
    <span class="cat-label" style="color:var(--accent-mk)">📣 마케팅</span>
    <div class="cat-line"></div>
  </div>
  <div class="cards">{make_cards(mk_news, 7)}</div>
</div>

<div class="footer">
  <div class="footer-left">AUTO-GENERATED · POWERED BY CLAUDE AI</div>
  <button class="share-btn" onclick="copyLink()">
    🔗 링크 복사
  </button>
</div>
<script>
  function copyLink() {{
    navigator.clipboard.writeText(window.location.href).then(() => {{
      alert('링크 복사 완료! 카카오톡에 붙여넣기 하세요 😊');
    }});
  }}
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ index.html 생성 완료!")
