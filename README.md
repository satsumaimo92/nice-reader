# reader — nice 第4部 バックナンバー閲覧ページ（試作）

50話ずつのまとまり（表紙は1話目の1コマ目）と最新回を並べた一覧と、
1話ずつ左右にめくって読むビューの、1枚の静的ページ。

- 公開URL: https://satsumaimo92.github.io/nice-reader/
- リポジトリ: https://github.com/satsumaimo92/nice-reader （main の `docs/` を GitHub Pages で配信）
- 更新: `build.py` を実行 → `git add -A && git commit && git push`（自動化は未設定）

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
- 50話の境目もそのまま次へ続く。URL は `#962` のように1話ごと
- × で一覧の元の位置に戻る

## 手元で見る

```bash
python3 -m http.server 8765 --directory docs
```
