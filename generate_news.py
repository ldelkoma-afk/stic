import anthropic
import datetime
import json
import re
import os

# 오늘 날짜
today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
date_str = today.strftime("%Y.%m.%d")
day_str = ["MON","TUE","WED","THU","FRI","SAT","SUN"][today.weekday()]

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

print(f"📰 {date_str} AI 직장인 브리핑 생성 시작...")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{
        "role": "user",
        "content": f"""오늘({date_str}) 기준 국내 뉴스와 콘텐츠를 검색해서 아래 4개 카테고리별로 3개씩 추출하고 JSON 형식으로만 응답해줘. 다른 텍스트는 절대 포함하지 마.

검색 조건:
- 한국 뉴스 사이트(네이버뉴스, 전자신문, AI타임스, 아이티조선, 디지털데일리, 블로터 등) 기준으로 검색
- 제목과 요약은 반드시 한국어로 작성
- 오늘 날짜({date_str}) 기준 최신 기사 우선
- 직장인이 실무에 바로 활용할 수 있는 내용 위주

카테고리 4개:
1. ai_trend: AI 신기술 동향 (최신 AI 모델·툴 출시 및 업데이트 소식)
2. automation: 업무 자동화 (AI로 반복업무를 줄이는 실전 팁·사례·도구)
3. ai_marketing: AI 마케팅 (AI 활용 광고·콘텐츠 제작·SEO 자동화 트렌드)
4. ai_tools: AI 툴 리뷰 (ChatGPT·Claude·Copilot·Gemini 등 실사용 후기·비교·활용법)

JSON 형식:
{{
  "ai_trend": [
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}}
  ],
  "automation": [
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}}
  ],
  "ai_marketing": [
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}}
  ],
  "ai_tools": [
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}},
    {{"title": "제목", "summary": "한줄요약"}}
  ]
}}"""
    }]
)

raw = ""
for block in response.content:
    if block.type == "text":
        raw += block.text

match = re.search(r'\{.*\}', raw, re.DOTALL)
if not match:
    raise ValueError("JSON을 찾을 수 없습니다")

data = json.loads(match.group())
trend_news = data["ai_trend"]
auto_news  = data["automation"]
mkt_news   = data["ai_marketing"]
tools_news = data["ai_tools"]

print(f"✅ 수집 완료 — 신기술 {len(trend_news)}건, 자동화 {len(auto_news)}건, 마케팅 {len(mkt_news)}건, 툴리뷰 {len(tools_news)}건")

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

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🤖 AI 직장인 브리핑 · {date_str}</title>
<meta property="og:title" content="🤖 AI 직장인 브리핑 · {date_str}">
<meta property="og:description" content="AI 신기술 · 업무자동화 · AI마케팅 · AI툴 최신 뉴스 12선">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700;900&family=DM+Mono:wght@400;500&display=swap');
  :root {{
    --bg:#0f0e0c; --card:#1a1916; --border:#2e2c28;
    --c1:#f5c842; --c2:#4af0a0; --c3:#ff7043; --c4:#64b5f6;
    --text:#f0ece0; --muted:#8a8678; --num:#3a3830;
  }}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{background:var(--bg);color:var(--text);font-family:'Noto Serif KR',serif;min-height:100vh;padding:0 0 80px;}}
  .header{{padding:48px 24px 32px;border-bottom:1px solid var(--border);position:relative;overflow:hidden;}}
  .header::before{{content:'';position:absolute;top:-60px;right:-60px;width:240px;height:240px;background:radial-gradient(circle,rgba(245,200,66,0.12) 0%,transparent 70%);pointer-events:none;}}
  .date-tag{{font-family:'DM Mono',monospace;font-size:11px;letter-spacing:.15em;color:var(--muted);text-transform:uppercase;margin-bottom:12px;}}
  h1{{font-size:clamp(26px,6vw,40px);font-weight:900;line-height:1.1;letter-spacing:-.02em;}}
  h1 span{{color:var(--c1);}}
  .subtitle{{margin-top:10px;font-size:13px;color:var(--muted);}}
  .section{{padding:28px 24px 0;opacity:0;transform:translateY(16px);animation:fadeUp .5s forwards;}}
  .section:nth-child(2){{animation-delay:.1s;}}
  .section:nth-child(3){{animation-delay:.2s;}}
  .section:nth-child(4){{animation-delay:.3s;}}
  .section:nth-child(5){{animation-delay:.4s;}}
  @keyframes fadeUp{{to{{opacity:1;transform:none;}}}}
  .cat-header{{display:flex;align-items:center;gap:10px;margin-bottom:14px;}}
  .cat-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;}}
  .cat-label{{font-family:'DM Mono',monospace;font-size:11px;letter-spacing:.12em;}}
  .cat-line{{flex:1;height:1px;background:var(--border);}}
  .cards{{display:flex;flex-direction:column;gap:2px;}}
  .card{{background:var(--card);border-radius:4px;padding:18px 20px;display:grid;grid-template-columns:36px 1fr;gap:0 14px;transition:background .2s;}}
  .card:hover{{background:#211f1c;}}
  .card-num{{font-family:'DM Mono',monospace;font-size:24px;font-weight:500;color:var(--num);line-height:1;padding-top:2px;text-align:right;}}
  .card-title{{font-size:14px;font-weight:700;line-height:1.5;margin-bottom:5px;}}
  .card-summary{{font-size:12px;color:var(--muted);line-height:1.6;}}
  .card-summary::before{{content:'→ ';font-family:'DM Mono',monospace;}}
  .footer{{margin:40px 24px 0;padding-top:24px;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;}}
  .footer-left{{font-family:'DM Mono',monospace;font-size:11px;color:var(--muted);letter-spacing:.1em;}}
  .share-btn{{display:inline-flex;align-items:center;gap:8px;background:#FAE100;color:#3A1D1D;font-family:'Noto Serif KR',serif;font-weight:700;font-size:14px;padding:10px 20px;border-radius:50px;border:none;cursor:pointer;transition:transform .15s,box-shadow .15s;}}
  .share-btn:hover{{transform:translateY(-1px);box-shadow:0 6px 20px rgba(250,225,0,.3);}}
</style>
</head>
<body>
<div class="header">
  <div class="date-tag">AI BRIEFING FOR WORKERS · {date_str} {day_str}</div>
  <h1>직장인<br><span>AI 브리핑</span></h1>
  <div class="subtitle">AI 신기술 · 업무자동화 · AI마케팅 · AI툴 최신 뉴스 12선</div>
</div>

<div class="section">
  <div class="cat-header">
    <div class="cat-dot" style="background:var(--c1)"></div>
    <span class="cat-label" style="color:var(--c1)">🤖 AI 신기술 동향</span>
    <div class="cat-line"></div>
  </div>
  <div class="cards">{make_cards(trend_news, 1)}</div>
</div>

<div class="section">
  <div class="cat-header">
    <div class="cat-dot" style="background:var(--c2)"></div>
    <span class="cat-label" style="color:var(--c2)">⚡ 업무 자동화</span>
    <div class="cat-line"></div>
  </div>
  <div class="cards">{make_cards(auto_news, 4)}</div>
</div>

<div class="section">
  <div class="cat-header">
    <div class="cat-dot" style="background:var(--c3)"></div>
    <span class="cat-label" style="color:var(--c3)">📣 AI 마케팅</span>
    <div class="cat-line"></div>
  </div>
  <div class="cards">{make_cards(mkt_news, 7)}</div>
</div>

<div class="section">
  <div class="cat-header">
    <div class="cat-dot" style="background:var(--c4)"></div>
    <span class="cat-label" style="color:var(--c4)">🛠️ AI 툴 리뷰</span>
    <div class="cat-line"></div>
  </div>
  <div class="cards">{make_cards(tools_news, 10)}</div>
</div>

<div class="footer">
  <div class="footer-left">AUTO-GENERATED · POWERED BY CLAUDE AI</div>
  <button class="share-btn" onclick="copyLink()">🔗 링크 복사</button>
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

print("✅ index.html 생성 완료!")
