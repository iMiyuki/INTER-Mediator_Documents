# gen_video_links.py 実運用手順（titles.txt / urls.txt 更新 → 生成 → 貼り付け）

この手順は、`titles.txt` と `urls.txt` に最新分を追記したあと、`tools/gen_video_links.py` で `<li><a ...>` を生成し、`videos2025.html` に貼り付けるためのものです。

---

## 0. 前提（置き場所）

- Python 3 が使えること
- スクリプトの場所（リポジトリ内）
  - `tools/gen_video_links.py`
- 作業用の入力ファイルを用意すること（例）
  - `titles.txt`
  - `urls.txt`

※入力ファイルの置き場所はどこでも良いですが、ここでは「リポジトリのルートに置く」想定で書きます。

---

## 1. `titles.txt` を最新データに更新する

### 1-1. 追記のルール

- 1行 = 1本の動画
- 空行は無視されます
- 各行は **必ず** `第NN回は、` で始めます（NNは数字）
- `第NN回は、` の後に、`、`（読点）区切りの要素が **最低2つ**必要です
  - スクリプトは最初の要素をタイトルとして採用します

### 1-2. 記述例

```txt
第101回は、アップロードのカスタマイズ、説明文（ここ以降は無視されます）
第102回は、データベースの利用とMySQL、説明文
```

この場合、タイトルとして使われるのは

- `#101` → `アップロードのカスタマイズ`
- `#102` → `データベースの利用とMySQL`

---

## 2. `urls.txt` を最新データに更新する

### 2-1. 追記のルール

- 1行 = 1本のURL
- 空行は無視されます
- `titles.txt` と同じ本数（空行を除いた行数）になるようにします

### 2-2. 記述例

```txt
https://youtu.be/F7ey8lzAChE
https://youtu.be/xJufgW5Frok
```

---

## 3. 前準備チェック（ここが一番大事）

### 3-1. 行数が一致しているか確認（推奨）

`titles.txt` と `urls.txt` の **空行を除いた行数**が一致していないと失敗します。

例（macOS / zsh）：

```bash
grep -cve '^[[:space:]]*$' titles.txt
grep -cve '^[[:space:]]*$' urls.txt
```

出力される数が同じであることを確認してください。

### 3-2. `titles.txt` の形式が崩れていないか軽く確認（推奨）

```bash
grep -nve '^第[0-9]\+回は、' titles.txt
```

何も出なければOKです（出た行はフォーマット違反の可能性があります）。

---

## 4. `gen_video_links.py` を実行する（コマンド）

### 4-1. そのまま標準出力に出す

```bash
python3 tools/gen_video_links.py titles.txt urls.txt
```

### 4-2. 出力をファイルに保存する（おすすめ）

あとでコピペしやすいので、いったんファイルに落とすのがおすすめです。

```bash
python3 tools/gen_video_links.py titles.txt urls.txt > out.html
```

---

## 5. 出力を `videos2025.html` に貼り付ける

出力は次の2ブロックに分かれています。

- `<!-- sequential -->`
  - タイトルだけ（番号なし）
  - `section id="sequential"` の `<ol>` の中に貼る用途
- `<!-- category -->`
  - `#番号 タイトル`
  - `section id="category"` の該当カテゴリの `<ul>` の中に貼る用途

### 5-1. sequential ブロックの貼り付け

`out.html`（または標準出力）から

- `<!-- sequential -->` から始まるブロック
- `<!-- category -->` の直前まで

を、`videos2025.html` の `section id="sequential"` 内の `<ol>` に貼ります。

### 5-2. category ブロックの貼り付け

`<!-- category -->` 以降のブロックを、`videos2025.html` の `section id="category"` で、該当するカテゴリの `<ul>` に貼ります。

---

## 6. よくあるエラーと対処

### 6-1. `Line count mismatch: titles=... urls=... (must match)`

- 原因：`titles.txt` と `urls.txt` の行数（空行除外後）が一致していない
- 対処：本数を揃える（余分な行を削除、足りない行を追加）

### 6-2. `Invalid line (missing '第NN回は、'): ...`

- 原因：`titles.txt` の行頭が `第NN回は、` になっていない
- 対処：該当行を `第NN回は、...` に修正

### 6-3. `Invalid line (need at least 2 '、'): ...`

- 原因：`第NN回は、` の後の `、` 区切りが少なく、要素が足りない
- 対処：`第NN回は、タイトル、説明文` のように `、` を追加

### 6-4. `File not found: ...`

- 原因：ファイルパスが違う / 実行場所が違う
- 対処：`titles.txt` `urls.txt` の場所を確認し、必要ならパスを明示して実行

例：

```bash
python3 tools/gen_video_links.py /path/to/titles.txt /path/to/urls.txt > out.html
```

---

## 7. 最小ワークフロー（要点だけ）

```bash
# 1) 行数チェック
grep -cve '^[[:space:]]*$' titles.txt
grep -cve '^[[:space:]]*$' urls.txt

# 2) 生成
python3 tools/gen_video_links.py titles.txt urls.txt > out.html

# 3) out.html を見ながら videos2025.html に sequential/category をそれぞれ貼り付け
```
