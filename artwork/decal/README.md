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

### 設定済みBambu Suiteプロジェクト

[NC03_panel_A4_basic_cut.lac](NC03_panel_A4_basic_cut.lac) はBambu Suite 01.06.00.00で読み込み・設定・保存したネイティブプロジェクトです。[画面](../../docs/images/panel-suite-setup.png)

- 機種：Bambu Lab H3C。加工：基本カット。弱粘着カットマット。
- 読み込んだ原稿：[NC03_panel_Suite_basic_cut.svg](NC03_panel_Suite_basic_cut.svg)。286.0 × 176.0 mm・100%をGUI確認。33穴＋外周の34閉輪郭を一つのパスにまとめています。
- ベクター印刷絵柄のSVGはSuiteでクリップや色の解釈が崩れ、288 mmとして扱われたため、プロジェクトから取り除いています。**印刷は上記のパス化PDF、Suiteはカットのみ**です。ロゴや背景を切断しません。
- 仮の材料設定：250g厚口紙ホワイトの参考値、320 gf・50 mm/s・1パス。写真光沢紙の銘柄・厚さは未確認のため、実測・余白での試し切り後に調整してください。光沢紙専用の検証済み設定ではありません。
- 自動配置で加工範囲内に収め、範囲外の警告を解消しました。これは**印刷紙との位置合わせ済みという意味ではありません**。A4印刷の原稿位置（左5.5 mm、上17 mm）に対し、実際にマットへ置いた紙の位置・向きに合わせて切断パスを移動してください。配置後に自動配置を実行すると印刷との位置がずれるため使用しないでください。
- 用紙セット、紙との位置合わせ、刃圧テスト、実際の印刷・切断は未実施。GUIは設定画面までで、「製作」は押していません。

カット専用SVGの再生成：`python3 scripts/export_panel_suite_cut.py`。`.lac` はGUIで保存した設定を使用します。

### 絵柄＋カット線を重ねたSuite確認用プロジェクト

[NC03_panel_A4_artwork_and_cut_REVIEW.lac](NC03_panel_A4_artwork_and_cut_REVIEW.lac) に、天板の絵柄とカット情報の両方を読み込み済み。[Suite画面](../../docs/images/panel-suite-artwork-cut.png)。両者は286 × 176 mm、同じ座標変換で重なります。

- `ARTWORK_REFERENCE_disable_before_cutting`：絵柄の確認用。PNGを使わず、文字・模様もパス。SuiteがPDF/SVGのグラデーションやクリップを再現しないため、グラデーションを160段の色帯パスにして互換表示しています。細い装飾線等は省略しているため、**印刷の正本は `NC03_panel_decal_A4.pdf`**。Suite表示の色段階や一部装飾の差を印刷原稿へ反映しないでください。
- `CUT_33_holes_and_outer_perimeter`：原寸カット情報。確認用では線として表示し、絵柄の上に重ねています。切断実行には検証済みの閉輪郭を保持した `NC03_panel_A4_basic_cut.lac` を使用。

**このREVIEWプロジェクトは表示・重なり確認用です。そのまま「準備する」「製作」を実行しないでください。** 絵柄の表示にはSuiteのプリント後カット属性を使っているため、全オブジェクトを加工へ送ると絵柄の個々のパスも対象になり得ます。実際のカットは絵柄を含まないbasic_cutプロジェクトで行い、用紙との位置合わせ・試し切りを済ませます。Suite内で一体化した自動Print Then Cutジョブの設定完了を意味しません。印刷・切断は開始していません。

Suite用のベクター確認絵柄は `NC03_panel_Suite_vector_art.svg`。`python3 scripts/export_panel_suite_art.py` で再生成（`fonttools`、`skia-pathops`が必要）。

## 天板と前面ロゴをA4光沢ゴールド一枚に印刷

[NC03_deck_and_front_A4.pdf](NC03_deck_and_front_A4.pdf) はA4横一ページに天板と前面ロゴ帯を原寸で配置した印刷用PDF。文字はアウトライン、埋め込み画像なし。[配置見本](../../docs/images/deck-and-front-a4.png)

- 天板：286 × 176 mm、用紙左5.5 mm・上21 mm。
- 前面ロゴ帯：194 × 12.5 mm、用紙左51.5 mm・上5 mm。
- 両者の間隔3.5 mm。縮小していないので操作穴の中心・径は原寸。
- Canon XK130：A4横、後トレイ、写真用紙 光沢ゴールド（GL-101 / `com.canon-mtgr`）、高品質、カラー、片面、倍率100%、フチなしOFF、用紙に合わせるOFF。
- 本体にも後トレイの「A4／光沢ゴールド」を登録。L判等の登録が残っているとサイズ不一致になります。

[カット線入りPDF](NC03_deck_and_front_A4_cut_guide.pdf) は手切り・寸法確認用。[同じA4座標のカットSVG](NC03_deck_and_front_A4_cut.svg) も用意。組合せ版は天板単独版からY方向の配置を変えているため、既存の天板単独Suiteプロジェクトをそのまま位置合わせせずに使わないでください。組合せSVGのSuite読み込みと実機カットは未検証、自動位置合わせマークは含みません。

再生成：`python3 scripts/export_combined_decal_a4.py`（Google Chromeが必要）。

## 現行版 v1.1 / 2026-11-16：左右用と入稿風レイアウト

- **A4一枚・全4枚**：[NC03_all_decals_A4_versioned.pdf](NC03_all_decals_A4_versioned.pdf)。天板、前面、左右をすべて原寸で配置。用紙の空きを詰めた省スペース版なので、3 mm塗り足し＋通常のトンボ余白は確保していません。
- **A4二枚・余白付き**：[NC03_decals_A4_2sheets.pdf](NC03_decals_A4_2sheets.pdf)。1ページ目は天板、2ページ目は前面＋左右。前面・左右は3 mm塗り足し、トンボ、寸法ラベル、フッターの版数・日付付き。
- [前面＋左右のみA4](NC03_front_and_sides_A4_prepress.pdf)／[カット線入り確認PDF](NC03_front_and_sides_A4_cut_guide.pdf)／[輪郭SVG](NC03_front_and_sides_A4_cut.svg)。トンボは矩形バウンディングボックスの位置を示します。最終外形は別のカット輪郭に従ってください。
- **A3入稿風・全4枚**：[NC03_all_decals_A3_prepress.pdf](NC03_all_decals_A3_prepress.pdf)／[輪郭確認PDF](NC03_all_decals_A3_cut_guide.pdf)／[カットSVG](NC03_all_decals_A3_cut.svg)。原寸、3 mm塗り足し、トンボ、寸法ラベル、版数・日付付き。前面・左右の間隔を広く取っています。

PDFの文字はNULL FONTのパス、埋め込み画像なし。ISOのA4/A3ページ寸法を数値確認。RGBベクター原稿であり、印刷所指定のCMYKプロファイル変換やPDF/X認証は行っていません。塗り足しは濃色のベースを輪郭の外へ延長したものです。トンボはSuite自動位置合わせ用のマークではありません。

左右のロゴ帯は、側面乳白カバーの外面 `side.lens_front` を共通設定から読み、全周0.5 mm内側の形にしています。長辺が水平になるよう2.55°回転して紙へ配置。**各141.04 × 8.94 mm**の平行四辺形で、取付時はケース側面の傾きに戻します。左と右は輪郭だけ鏡対称、NULL CITYの文字は読みやすい向きを維持。寸法はモデル由来で、実物への貼付・光の透過は未検証。写真紙では白文字も透光しにくく、発光を残すための周囲0.5 mmの縁以外は覆います。

### Suite確認用

- [全4枚のA4重ね合わせ](NC03_all_decals_v1.1_REVIEW.lac)
- [余白を取った前面＋左右のA4重ね合わせ](NC03_front_and_sides_A4_REVIEW.lac)

いずれも絵柄とカット輪郭を読み込んだ**確認用**で、実行ジョブではありません。絵柄レイヤーを含んだまま加工しないでください。紙面配置を変えたため、古い単独天板の位置合わせをそのまま流用できません。Suiteの表示には互換ベクター絵柄を使用し、印刷は上記の正本PDFから行います。

再生成順：

```sh
python3 scripts/export_all_decals_a4.py
python3 scripts/export_decal_prepress.py
python3 scripts/build_combined_suite_review.py
```

PDF生成にはGoogle Chrome、入稿風PDFにはPythonの`fonttools`と`pypdf`が必要。

### 使用用紙の確定：Canon写真用紙・光沢ゴールド A4 厚手

ユーザー指定の光沢ゴールドはGL-101。Canon公式の紙厚は **0.27 mm**：[製品仕様](https://personal.canon.jp/product/supply/paper/2310B014)。保存済みSuiteプロジェクトの材料紙厚を0.30から0.27 mmへ更新しました。材料名は元の「250g厚口紙ホワイト」の参考プロファイルを保持し、刃圧320 gf・速度50 mm/s・1パスは**光沢紙で未検証の仮値**です。紙厚を合わせても切断条件の検証にはなりません。余白で試し切りして調整してください。

Canon印刷はA4・写真用紙 光沢ゴールド・後トレイ・高品質・カラー・片面・倍率100%・フチなしOFF。用紙の銘柄指定と、後トレイへ実際にセットしたことの確認は別です。プリンターがL判を報告している間、用意した印刷ジョブは保留し、A4のセット・本体登録が確認できるまで再開しません。

## 印刷済みA4一枚版の実カット用データ

[NC03_all_decals_A4_CUT_ONLY_NOMINAL.lac](NC03_all_decals_A4_CUT_ONLY_NOMINAL.lac)／[SVG](NC03_all_decals_A4_CUT_ONLY.svg) は、実際にCanonへ送った全4枚一枚版 `NC03_all_decals_A4_versioned.pdf` に対応。天板の33穴と、天板・前面・左・右の4外周、**合計37閉輪郭のみ**。絵柄・文字・フッター・トンボを加工データに含めません。全輪郭を一つのパスにして相対配置を保持。GUIプレビューで286 × 199.9 mm・100%、加工時間約3分8秒を確認。

**NOMINALは紙面上の原点配置であり、マットへの位置合わせ済みジョブではありません。** 現物の貼付位置ごとに俯瞰カメラで照合し、必要な移動・回転を適用してから実行してください。紙を貼り直したら前の補正は使わず再撮影します。今回の一枚版には自動位置合わせ用マークがないため、自動Print Then Cutの登録ではなく、画像を基準に合わせる工程が必要です。画面上のトンボを自動登録マークとして扱わないでください。

紙厚0.27 mm、仮の厚紙参考値320 gf・50 mm/s・1パス。カメラ確認・カットパスプレビューまで行いましたが、貼り直し後の最終位置合わせと実機切断は未完了です。光沢紙での刃圧も未検証です。

再生成：`python3 scripts/build_all_decals_cut_job.py`（`fonttools`が必要）。[検証メタデータ](NC03_all_decals_A4_cut_validation.json)の`physical_alignment_verified`と`pressure_verified`は未検証のためfalse。
