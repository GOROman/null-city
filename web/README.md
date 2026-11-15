# NULL CITY — PBR Web preview

公開先：**https://goroman.github.io/null-city/**

現在のBlender組立モデルをGLBへ出力し、`@google/model-viewer` 4.4.0で表示する静的Web UI。回転・ズーム・移動、俯瞰／正面／右側面／上面、分解スライダー、ケース透過、LED点灯、HDR IBL、環境回転・HDR背景、SSAO、任意の自動回転に対応。デカール、金属・粗さ、透過、クリアコート、発光をGLBに保持する。GLBはメートル単位、外幅0.300 m。照明・材質は完成イメージで、実物の配線・光学・温度検証ではない。

## ローカルで確認

Node.js 24以降とnpmを使用する。

```sh
npm ci --prefix web
npm run dev --prefix web
```

表示先は `http://127.0.0.1:4173`。公開用ビルドは `npm run build --prefix web`。依存ライブラリ、フォント、モデル、ポスターは同じ公開先へ配置し、CDNには依存しない。

## モデル更新

形状・材質を変更したら、先に `NULL_CITY_NC03.py` で最新の `.blend` を生成する。その後：

```sh
npm run model:export --prefix web
npm run build --prefix web
```

Blender実行ファイルが標準の場所にない場合は `BLENDER=/path/to/blender npm run model:export --prefix web`。

`public/model/nc03.glb` と `manifest.json` をコミットする。生成スクリプトは元のblendを保存せず、20個の印刷部品と外観部品だけを出力し、床・カメラ・照明器具を含めない。Blenderのmm座標はGLBのルートでメートルへ変換し、各部品の動きを1本の `Assembly` アニメーションにまとめる。乳白カバーは非発光時のベース色を白とし、マゼンタは発光チャンネルに持たせる。

ビルド時には元モデル・設計入力・GLBのSHA-256を照合する。古いGLBが残っていたらCIを失敗させ、古いプレビューの公開を防ぐ。Actions上でBlenderを再実行せず、検証済みのエクスポートを配信する。

## 検証と自動公開

```sh
npm run build --prefix web
cd web
npx playwright install chromium
npm test
```

macOSでインストール済みChromeを使う場合は `PW_USE_CHROME=1 npm test`。Playwrightは本番ビルドを `/null-city/` 配下で開き、PC・スマートフォンでGLB読み込み、寸法・材質、視点、分解、発光、透過、明るさ、回転、リセット、横はみ出し、読み込み失敗時の表示を確認する。GLBはKhronos glTF Validatorでも検証する。

`.github/workflows/pages.yml` がmainへの関連変更と手動実行で、依存インストール→GLB整合性・ビルド→ブラウザー検証→Pages公開を行う。PRでは同じ検証を行い、公開しない。PagesのSourceは **GitHub Actions**。公開ジョブだけに `pages: write` と `id-token: write` を付与する。

コードはMIT、GLB・画像はCC BY 4.0、NULL FONTはSIL OFL 1.1。npmの第三者ライセンスは公開先の `project/THIRD_PARTY_LICENSES.txt` に同梱する。

## HDR IBL / SSAO

Poly Havenの **Studio Small 03 / Studio Small 02**（Greg Zaal、CC0）を1K Radiance HDRとして `public/environments/` に同梱する。環境選択でIBLを切り替え、環境の回転でモデルを動かさず反射・照明とHDR背景を回す。既定はStudio 03、環境角90°、露出0.8、背景非表示。元画像・取得元・ライセンス・SHA-256は同ディレクトリの `manifest.json` と公開先の `project/HDRI_CREDITS.txt` に記録する。

ビルドではハッシュとHDRデコードを検証。両画像とも1024 × 512、RGB値が有限かつ1.0を超える実際のHDRであることを確認する。色調変換前のピーク輝度はStudio 03が3565.93、Studio 02が694.71。トーンマップ済みJPEGを照明へ流用していない。

`@google/model-viewer-effects` の高精度バッファでSSAO→SMAA→Khronos Neutralの順に処理する。SSAOはON／OFF可能。MSAAは無効にして深度効果との不整合を避ける。環境回転は公開されているcustom-pass API経由でThree.jsのSceneへ適用し、モデルの回転角とは独立させる。

自動回転は待ち時間0 ms・20°/秒。スマートフォンでスイッチがモデル表示領域より下にある場合は、ON時にネイティブのフォーカス移動完了後、モデルが見える位置へ即座に戻す。モデル上の回転ボタンからもON／OFFできる。テストではONという属性だけでなく、実際の角度増加とOFF後の停止を確認する。
