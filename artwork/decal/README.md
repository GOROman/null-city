# 前面 NULL CITY デカール：A4写真光沢紙 / Bambu Suite

現行の前面乳白カバーに貼る台形ロゴ帯。天板全体のデカールとは別です。

- **切り出し外形194 × 12.5 mm**、上辺175.6 mm。`lighting_layout.json` の `front.mask_outline` と一致。
- 元原稿 `NC03_front_mask.svg` の203 × 17 mmは余白込みキャンバスです。Suiteに読み込む以下のデータは余白を除去済み。
- 図柄は既存のNULL FONTのアウトライン。文字のフォントインストールは不要。

## 推奨：Bambu SuiteからPrint Then Cut

1. **`NC03_front_suite_print.png`** を画像として読み込む。3880 × 250 px、外側が透明の約508 dpi画像です。文字も一枚の印刷画像にまとめてあるため、白文字を切断対象にしません。
2. 寸法を **幅194 mm / 高さ12.5 mm** に設定。PNGの読み込み時の解像度解釈に任せず、寸法欄を確認します。
3. 「Print Then Cut」を選択し、透明領域との境界に沿う**外周のみ**の切断輪郭を作成。オフセットは0 mm、輪郭は一周の閉じた台形。印刷プレビューでロゴの文字やスラッシュが個別に切断されないことを確認。
4. ベクター輪郭が必要な場合は **`NC03_front_suite_cut.svg`** を使用。同じ194 × 12.5 mmの単一閉輪郭です。印刷画像と中心位置・寸法を揃えます。自動生成の輪郭と重複して二重切断しないよう、一方だけを切断対象にします。ベクター印刷原稿は `NC03_front_suite_print.svg` にあります。
5. 用紙は **A4・横**。プリンターの用紙種類を実際の「写真光沢紙」に合わせ、倍率100%、フチなし拡大・用紙に合わせる・自動縮小を無効にします。Suiteが作成する位置合わせマークも印刷します。領域に入らない場合は図柄を縮小せず、A4横と配置を再確認。
6. インクが乾いてからカッティングマットへ固定し、Suiteの位置合わせ工程を使ってカットします。紙厚・紙の銘柄が未指定なので刃圧・速度・回数は固定していません。実測した厚さで設定し、余白の小片で試し切りしてから本体を切ります。

**先に下記の手切り用PDFを印刷しても、Suiteの位置合わせマークは付いていません。自動位置合わせを使うときは、Suite側から印刷してください。**

このリポジトリにあるのはSuiteに読み込む原稿と輪郭であり、材料設定済みのSuiteネイティブプロジェクトや実機検証済みのカットジョブではありません。印刷・カットは未実行です。

## 手切り用A4 PDF

`NC03_front_decal_A4.pdf` はA4横1ページに原寸3枚、台形のカットガイド、100 mmの確認スケールを配置。印刷後にスケールを定規で確認します。Suite用の位置合わせマークは含みません。

通常の写真光沢紙は白文字部分も紙として残ります。このデータは外周だけを切り、文字やスラッシュをくり抜きません。背面LEDを文字から透かしたい場合は別途、透光素材や文字抜きマスクが必要です。粘着層がない写真用紙は薄い両面テープ等で貼り付けます。

## 再生成

```sh
python3 scripts/export_front_mask.py
python3 scripts/export_front_decal_a4.py
python3 scripts/export_front_suite.py
```

PDFとPNG生成にはGoogle Chromeを使用。

参考：[Bambu Suite Sticker Tool](https://wiki.bambulab.com/en/software/bambu-suite/manual/sticker-tool)、[Bambu Lab Cutting Module公式クイックスタート](https://csm.bblcdn.com/hub/cc1fd0d0f2ec4af18949093d3b163fa1.pdf)。機器への取付・校正は使用機種の現行手順に従ってください。

## 天板パネル：A4横一枚・完全ベクターPDF

- **`NC03_panel_decal_A4.pdf`**：印刷用。画像の埋め込みなし、文字はNULL FONTのパス。A4横一枚。
- **`NC03_panel_decal_A4_cut_guide.pdf`**：同寸法のカット線入り。穴を手切りする場合や位置確認用。
- **`NC03_panel_A4_print.svg`**：編集用ベクター原稿、286 × 176 mm。
- **`NC03_panel_A4_cut.svg`**：Suite用の外周＋内部33穴の切断線。同じ286 × 176 mmキャンバス。
- **`NC03_panel_A4_inner_cut.svg`**：内部33穴だけの切断線。外周の重複切断を避ける場合に使用。SVGの内部原点は (1,1) mmで、全体版と同じ座標を維持。

天板本体は288 × 178 mm。デカールだけ全周1 mm内側へオフセットし、**286 × 176 mm**にしています。全体を縮小していないため、操作穴・取付穴・四角LED窓の中心はモデルと一致。斜めの角も1 mmのオフセットです。ボタン穴6個30.4 mm、補助2個24.4 mm、レバー24 mm、レバー取付4個4.5 mm、外周ネジ4個3.4 mm、LED窓16個4 mmを反映。

ネットワークで検出したCanon PIXUS XK130はA3非対応。A4の通常印刷可能範囲は203.2 × 287 mmなので、286 × 176 mmの原稿を**A4横・倍率100%・フチなしOFF・自動縮小OFF**で印刷します。PDF上の配置は左5.5 mm、上17 mm。用紙種類は実際の写真光沢紙に合わせ、写真用紙は後トレイから給紙。最初に普通紙で穴の位置と幅286 mmを確認し、光沢紙で本印刷してください。

このPDFは直接印刷用で、SuiteのPrint Then Cut用マークは含みません。**A4一枚にこの寸法で収めたままSuiteのマーク領域も確保できるとは確認していません。** Suiteの自動位置合わせを使う場合は、原寸の絵柄とSVGカット線を同じ位置に揃え、Suite上でマークを含む用紙への収まりを確認する必要があります。原寸で収まらないときは縮小せず、手動位置合わせで試し切り、または分割・大判印刷を選びます。カットSVGは作成済み、Suite上の配置・実機切断は未検証です。

凹ロゴのある多色天板に貼るとロゴの凹みを覆います。全面デカールの仕上がりにはフラット天板が適しています。紙は照明窓を透かさないため、16個の四角窓は切り抜いてください。

再生成にはPythonの`fonttools`とGoogle Chromeが必要：

```sh
python3 scripts/export_panel_decal.py
```

参考：[Canon XK130対応用紙](https://ij.manual.canon/ij/webmanual/Manual/All/XK130%20series/JP/UG/ug-280.html)、[A4印刷可能範囲](https://ij.manual.canon/ij/webmanual/Manual/All/XK130%20series/JP/UG/ug-196.html)、[Mac給紙設定](https://ij.manual.canon/ij/webmanual/PrinterDriver/M/XK130%20series/CO/JP/PPG/dg-c_pc_basic.html)。
