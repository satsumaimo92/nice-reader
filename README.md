# reader — nice 第4部 バックナンバー閲覧ページ（試作）

50話ずつのまとまり（表紙は1話目の1コマ目）と最新回を並べた一覧と、
1話ずつ左右にめくって読むビューの、1枚の静的ページ。

- 公開URL: https://nice.satsumaimo.org/ （DNS は FC2ドメインの CNAME nice → satsumaimo92.github.io、`docs/CNAME`）
- satsumaimo.org/manga/nice の第4部カードは STUDIO CMS の `nice4` モデル。50話たまったら1件足す（手順は ~/Desktop/code/org/PLAN.md）
- リポジトリ: https://github.com/satsumaimo92/nice-reader （main の `docs/` を GitHub Pages で配信）
- 更新: 毎晩23:30に launchd（`com.satsumaimo.nice-reader`）が `update.sh` を実行する。
  build.py → 変化があればコミットして push。ログは `logs/YYYYMM.log`（git 管理外）

## 自動更新の安全策

- 新都社に出た話でも、手元に素材（ストリップ）がまだ無ければ、その手前で止める
- 新都社の読み取りに失敗するなどして公開範囲が前回より小さくなったら、何もしない
- 変化の無い日はコミットしない
- Mac が寝ていた・SSD が外れていた日は、次に回ったときにまとめて拾う

launchd を入れ直すとき:

```bash
cp com.satsumaimo.nice-reader.plist ~/Library/LaunchAgents/ && launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.satsumaimo.nice-reader.plist
```

## 構成

```
reader/
├─ build.py        画像とデータを作る（既にあるファイルは飛ばす）
└─ docs/           このフォルダを GitHub Pages で公開する
    ├─ index.html  一覧＋読むビュー（JSは同梱、外部依存は Google Fonts だけ）
    ├─ data.json   公開済みの最終話・最新回の範囲と日付
    ├─ strips/     NNNN.webp 1話ぶんの縦長（幅800・グレー・q60、計約150MB）
    └─ covers/     NNNN.webp 表紙（50話ごと＋最新回の1話目の1コマ目）
```

## 素材の出どころ

- 1〜500話のストリップ: `nice4/nice4-N.jpg|png`（Nが話数そのもの）
- 501話〜: `nice4/latest/strips/nice_NNNN_strip.png`（extract_latest.py の出力）
- 1コマ目: 1〜500 `nice4/panels/nice_NNN_1.png`、501〜 `nice4/latest/panels/nice_NNNN_1.png`

## 公開範囲

新都社の作者コメント（「993-1000」）の最新値までだけを出す。
描き上がっていても新都社で公開前の話は出ない。`--max` で手動指定もできる。

```bash
/Volumes/sat_SSD/manga/nice/nice4/latest/.venv/bin/python build.py
```

## 操作

- 一覧のカード → その50話の1話目から（最新カードは最新回の1話目から）
- 左ボタン / 指を右へ払う / ← キー = 次の話、右 = 前の話（漫画の向き）
- スマホでは下の帯の左半分・右半分がまるごとボタン（丸の外を押しても効く）。ダブルタップでの拡大は止めてある（ピンチ拡大は可）
- 50話の境目もそのまま次へ続く。URL は `#962` のように1話ごと
- × の戻り先: このページの一覧から入ったなら一覧の元の位置、satsumaimo.org（/manga/nice のカード）や直リンクから入ったなら satsumaimo.org/manga/nice
- 各話の下に新都社のコメント欄（`docs/comment.html` を iframe で。nice4_latest の STUDIO 埋め込みと同じフォーム、作品ID 3681）。戻るボタンは置かない（× と行き先が同じなので）

## 手元で見る

```bash
python3 -m http.server 8765 --directory docs
```
