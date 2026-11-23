"""nice 第4部 バックナンバー閲覧ページ用の画像とデータを作る。

- strips/NNNN.webp : 1話ぶんの縦長ストリップ(タイトル込み)。幅800・グレー・webp q60
- covers/NNNN.webp : 50話ごとのまとまりと最新回の表紙(その回1話目の1コマ目を枠で切り抜き)
- data.json        : 公開済みの最終話・最新回の範囲と日付

公開範囲は新都社の作者コメント(「993-1000」など)の最新値で決める。
手元に描き上がっていても、新都社で公開する前の話は出さない。

使い方:
  python build.py            # 新都社を見て、公開済みの最終話まで作る(既にあるファイルは飛ばす)
  python build.py --max 1000 # 公開範囲を手で指定
"""
import argparse
import datetime as dt
import html
import json
import re
import urllib.request
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image, ImageOps

NICE4 = Path('/Volumes/sat_SSD/manga/nice/nice4')
SITE = Path(__file__).resolve().parent / 'docs'
CHUNK = 50
STRIP_W, STRIP_Q = 800, 60
COVER_W, COVER_Q = 720, 70
COMIC_ID = 3681


def strip_src(n: int) -> Path:
    if n >= 501:
        return NICE4 / 'latest' / 'strips' / f'nice_{n:04d}_strip.png'
    for ext in ('jpg', 'png'):
        p = NICE4 / f'nice4-{n}.{ext}'
        if p.exists():
            return p
    raise FileNotFoundError(f'strip {n}')


def panel1_src(n: int) -> Path:
    if n >= 501:
        return NICE4 / 'latest' / 'panels' / f'nice_{n:04d}_1.png'
    return NICE4 / 'panels' / f'nice_{n:03d}_1.png'


def make_strip(n: int) -> str:
    out = SITE / 'strips' / f'{n:04d}.webp'
    if out.exists():
        return ''
    im = Image.open(strip_src(n)).convert('L')
    im = im.resize((STRIP_W, round(STRIP_W * im.size[1] / im.size[0])), Image.LANCZOS)
    im.save(out, 'WEBP', quality=STRIP_Q, method=6)
    return f'strip {n}'


def make_cover(n: int) -> str:
    out = SITE / 'covers' / f'{n:04d}.webp'
    if out.exists():
        return ''
    im = Image.open(panel1_src(n)).convert('L')
    bb = ImageOps.invert(im).point(lambda v: 255 if v > 80 else 0).getbbox()
    if bb:
        im = im.crop((max(bb[0] - 6, 0), max(bb[1] - 6, 0), min(bb[2] + 6, im.size[0]), min(bb[3] + 6, im.size[1])))
    im = im.resize((COVER_W, round(COVER_W * im.size[1] / im.size[0])), Image.LANCZOS)
    im.save(out, 'WEBP', quality=COVER_Q, method=6)
    return f'cover {n}'


def neetsha_updates() -> list[dict]:
    """新都社のコメント欄から作者コメント(更新記録)を新しい順に返す。"""
    url = f'https://neetsha.jp/inside/comment.php?id={COMIC_ID}&page=1&limit=1000'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    h = urllib.request.urlopen(req, timeout=60).read().decode('utf-8')
    items = []
    for cls, body in re.findall(r'<p\s+id="comment_\d+"\s+class="([^"]*)"\s*>(.*?)</p>', h, re.S):
        if 'author-comment' not in cls.split():
            continue
        d = re.search(r'&lt;(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}&gt;', body)
        text = re.sub(r'<small>.*?</small>', '', body, flags=re.S)
        text = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', text)).split())
        m = re.match(r'^(\d+)\s*[-‐－~〜]\s*(\d+)$', text)
        if d and m:
            items.append({'date': d.group(1), 'from': int(m.group(1)), 'to': int(m.group(2))})
    return sorted(items, key=lambda x: (x['to'], x['date']), reverse=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--max', type=int, default=0, help='公開済みの最終話(省略時は新都社から取得)')
    args = ap.parse_args()

    ups = neetsha_updates()
    latest = ups[0] if ups else None
    published = args.max or (latest['to'] if latest else 0)
    if not published:
        raise SystemExit('公開済みの最終話が分からない')
    if latest is None or latest['to'] != published:
        latest = {'from': max(1, published - 7), 'to': published, 'date': ''}

    (SITE / 'strips').mkdir(parents=True, exist_ok=True)
    (SITE / 'covers').mkdir(parents=True, exist_ok=True)
    covers = sorted(set(list(range(1, published + 1, CHUNK)) + [latest['from']]))
    with ProcessPoolExecutor() as ex:
        done = [r for r in ex.map(make_strip, range(1, published + 1), chunksize=8) if r]
        done += [r for r in ex.map(make_cover, covers) if r]

    data = {
        'published': published,
        'chunk': CHUNK,
        'latest': {'from': latest['from'], 'to': latest['to'], 'date': latest['date'].replace('-', '.')},
        'built': dt.datetime.now().isoformat(timespec='seconds'),
    }
    (SITE / 'data.json').write_text(json.dumps(data, ensure_ascii=False))
    print(f'published={published} latest={latest} new files={len(done)}')


if __name__ == '__main__':
    main()
