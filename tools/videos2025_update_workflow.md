# videos2025.html 更新手順（Discord → 自動生成 → sequential自動追記）

## 前提

- Python 3 が使えること
- リポジトリ内に以下のスクリプトがあること
  - `tools/discord_to_titles_urls.py`
  - `tools/gen_video_links.py`
  - `tools/update_videos2025_sequential.py`
- 更新対象HTML
  - `ja/for-novices/videos2025.html`

---

## 1. Discordから元データとYouTubeリンクを取得する

Discordの該当チャンネルに、新規ビデオの情報が **2段階**で投稿される。

- 元データ（ビデオ作成者）
  - 例: `第110回は、...` で始まる説明文（複数行）
- YouTubeリンク（別の人）
  - URLの列
  - 並び順は元データの番号順

---

## 2. Discordの投稿を `discord_dump.txt` に貼り付ける

リポジトリのルート（または任意の場所）に `discord_dump.txt` を作成し、以下を1つのファイルにまとめて貼り付けて保存する。

- 元データ（`第NN回は、...` の投稿群）
- YouTubeリンク（URLの投稿群）

注意:

- 1つの動画につき、元データは「空行区切りの塊」で貼り付ける（Discord投稿の見た目そのままでOK）
- URLは行ごとに1つずつ並べる（余計な文字が混ざっていても可）

---

## 3. `titles.txt` と `urls.txt` を自動生成する

まずは安全のため、毎回作り直す運用（`overwrite`）を推奨。

```bash
python3 tools/discord_to_titles_urls.py tools/discord_dump.txt --mode overwrite
```

出力:

- `titles.txt`
  - 1行=1本
  - 行頭が `第NN回は、...` で始まる形式
- `urls.txt`
  - 1行=1本のURL

失敗する場合:

- `titles` と `urls` の件数が一致しないとエラーになる
  - 元データの本数とURL本数が揃っているか確認する

追記運用にしたい場合:

```bash
python3 tools/discord_to_titles_urls.py tools/discord_dump.txt --mode append
```

---

## 4. `out.html` を生成する（確認用）

既存スクリプトで、貼り付け用の `<li><a ...>` を生成する。

```bash
python3 tools/gen_video_links.py tools/titles.txt urls.txt > tools/out.html
```

`out.html` は次の2ブロックを含む:

- `<!-- sequential -->`（番号なしタイトル）
- `<!-- category -->`（`#番号 タイトル`）

---

## 5. sequential（番号順）だけ `videos2025.html` に自動追記する

### 5-1. まず dry-run（追記内容だけ表示）

```bash
python3 tools/update_videos2025_sequential.py ja/for-novices/videos2025.html tools/titles.txt tools/urls.txt --dry-run
```

### 5-2. 問題なければ実際に書き込み

```bash
python3 tools/update_videos2025_sequential.py ja/for-novices/videos2025.html tools/titles.txt tools/urls.txt
```

仕様:

- `section id="sequential"` 内の `<ol>` の `</ol>` 直前に追記する
- **既に存在するURL（`href`）は重複追加しない**

---

## 6. category（カテゴリ別）は手動で反映する

`out.html` の `<!-- category -->` 以降のブロックから必要な `<li>` を選び、`videos2025.html` の該当カテゴリの `<ul>` に手動で追加する。

※カテゴリ分類は厳密なルールがないため、自動化しない。

---

## 7. GitHubへ反映（いつも通り）

- `videos2025.html` の差分を確認
- 自分のリポジトリに `commit` / `push`
- INTER-Mediatorのマスタに対して Pull Request を作成

---

## よくあるエラー

### `Line count mismatch: titles=... urls=... (must match)`

- 元データ（第NN回…）の本数と、URLの本数が一致していない
- Discordのコピペが欠けていないか確認する

### `No title blocks found (lines starting with '第NN回は、')`

- 元データが `第NN回は、` で始まっていない
- 行頭の表記ゆれがないか確認する

### `No new entries to add.`

- `videos2025.html` の sequential 側に、同じURLがすでに存在する（追加不要）

---

## 最小コマンドまとめ（要点だけ）

```bash
python3 tools/discord_to_titles_urls.py tools/discord_dump.txt --mode overwrite
```

```bash
python3 tools/gen_video_links.py titles.txt tools/urls.txt > tools/out.html
```

```bash
python3 tools/update_videos2025_sequential.py ja/for-novices/videos2025.html tools/titles.txt urls.txt --dry-run
```

```bash
python3 tools/update_videos2025_sequential.py ja/for-novices/videos2025.html titles.txt urls.txt
```
