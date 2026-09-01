#!/usr/bin/env python3
"""現場で渡すQRカードの印刷用シートを生成する。

URLを変えたいときは TOOL_URL を書き換えて実行するだけ。

    pip install segno
    python3 review-assist/build-cards.py

出力：
    review-assist/card-print.html … A4に名刺サイズ10枚を並べた印刷用ページ
    review-assist/qr.svg          … QRコード単体（他の印刷物に使う場合用）
"""

import io
from pathlib import Path

import segno

# ── ここだけ書き換えれば作り直せる ──────────────────────
TOOL_URL = "https://japan-unlockservice.com/review-assist/"
# ────────────────────────────────────────────────

HERE = Path(__file__).parent


def qr_svg(url: str, size_mm: float) -> str:
    """QRコードを、カードに埋め込めるインラインSVGとして返す。"""
    qr = segno.make(url, error="m")
    buf = io.BytesIO()
    qr.save(
        buf,
        kind="svg",
        border=2,
        unit="mm",
        scale=size_mm / qr.symbol_size(border=2)[0],
        svgclass=None,
        lineclass=None,
        xmldecl=False,
        svgns=True,
        nl=False,
    )
    return buf.getvalue().decode("utf-8")


CARD = """    <div class="card">
      <div class="qr">{qr}</div>
      <div class="body">
        <p class="lead">ご感想を<br>お聞かせください</p>
        <ol class="steps">
          <li>カメラでQRを読み取る</li>
          <li>かんたんな質問に答える</li>
          <li>口コミの文章ができます</li>
        </ol>
        <p class="note">所要およそ60秒です。<br>投稿されるかどうかも、星の数も、<br>お客様のご判断でお決めください。</p>
        <p class="brand">日本アンロックサービス株式会社</p>
        <p class="url">{host}</p>
      </div>
    </div>
"""

PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>口コミQRカード 印刷用｜日本アンロックサービス</title>
<style>
  @page {{ size: A4; margin: 0; }}

  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: #EDEAE4;
    font-family: "Hiragino Sans", "Yu Gothic", Meiryo, sans-serif;
    color: #221E18;
  }}

  /* 画面で見るときだけ出る操作説明。印刷には出ない */
  .screen-only {{
    max-width: 210mm;
    margin: 0 auto;
    padding: 20px 18px;
    font-size: 14px;
    line-height: 1.8;
  }}
  .screen-only h1 {{ font-size: 17px; margin: 0 0 8px; }}
  .screen-only p {{ margin: 0 0 6px; color: #554E45; }}
  .screen-only code {{
    background: #fff; padding: 1px 6px; border-radius: 4px;
    font-size: 13px; word-break: break-all;
  }}

  .sheet {{
    width: 210mm;
    height: 297mm;
    margin: 0 auto;
    padding: 11mm 14mm;
    background: #fff;
    display: grid;
    grid-template-columns: repeat(2, 91mm);
    grid-template-rows: repeat(5, 55mm);
    gap: 0;
  }}

  .card {{
    width: 91mm;
    height: 55mm;
    padding: 5mm 5mm 4mm;
    display: flex;
    align-items: center;
    gap: 4.5mm;
    outline: 0.2mm dashed #C9C2B6;   /* 裁断ガイド。境界を共有させるため outline */
    outline-offset: -0.1mm;
  }}

  .qr {{ flex: 0 0 auto; line-height: 0; }}
  .qr svg {{ display: block; }}

  .body {{ flex: 1 1 auto; min-width: 0; }}

  .lead {{
    margin: 0 0 1.8mm;
    font-size: 10.5pt;
    font-weight: 700;
    line-height: 1.4;
    letter-spacing: .02em;
  }}

  .steps {{
    margin: 0 0 1.8mm;
    padding-left: 4.4mm;
    font-size: 7.2pt;
    line-height: 1.5;
    color: #4A443C;
  }}
  .steps li {{ margin: 0; }}

  .note {{
    margin: 0 0 1.8mm;
    font-size: 6.2pt;
    line-height: 1.45;
    color: #6E665A;
  }}

  .brand {{
    margin: 0;
    padding-top: 1.3mm;
    border-top: 0.2mm solid #E0D9CC;
    font-size: 7pt;
    line-height: 1.3;
    letter-spacing: .04em;
    color: #8A6019;
  }}
  .url {{
    margin: 0.3mm 0 0;
    font-size: 5.6pt;
    line-height: 1.3;
    color: #9C948A;
  }}

  @media print {{
    body {{ background: #fff; }}
    .screen-only {{ display: none; }}
    .sheet {{ margin: 0; page-break-after: always; }}
  }}
</style>
</head>
<body>

<div class="screen-only">
  <h1>口コミQRカード（名刺サイズ10枚／A4）</h1>
  <p>このページをそのまま印刷してください。用紙はA4、余白なし（等倍100%）の設定にします。破線が裁断位置です。</p>
  <p>QRコードのリンク先： <code>{url}</code></p>
  <p>URLを変える場合は <code>review-assist/build-cards.py</code> の TOOL_URL を書き換えて再実行してください。</p>
</div>

<div class="sheet">
{cards}</div>

</body>
</html>
"""


def main() -> None:
    svg = qr_svg(TOOL_URL, size_mm=30)
    (HERE / "qr.svg").write_text(svg, encoding="utf-8")

    host = TOOL_URL.split("://", 1)[-1].rstrip("/")
    cards = "".join(CARD.format(qr=svg, host=host) for _ in range(10))
    (HERE / "card-print.html").write_text(
        PAGE.format(cards=cards, url=TOOL_URL), encoding="utf-8"
    )

    print(f"生成しました（リンク先: {TOOL_URL}）")
    print("  review-assist/card-print.html")
    print("  review-assist/qr.svg")


if __name__ == "__main__":
    main()
