"""
# rs04.py
文章が二列になっている論文に一列ずつ対応

### 機能
- 指定ページの処理範囲減少（ページ上が図になったものなど）

- 分割に対応した処理
- サイズ→A4見開き

1.A4見開きの空間を用意 \n
見開きPDFイメージ： \n
|1|2|3|4| \n
2.元のページ左半分を|1|に描画 \n
3.元のページ右半分を|3|に描画 \n
4.罫線を|2|,|4|に描画
"""

import fitz  # PyMuPDF
import sys


def process(
        input_path, 
        output_path, 
        divide = 595 // 2, # A4サイズの半分
        grid_width = 20,
        option_obj = {}):
    """2列PDFを2分割して、それぞれ書き込む関数

    :param input_path: 入力PDFファイルのパス
    :param output_path: 出力PDFファイルのパス
    :param divide: ページを分割する位置
    :param grid_width: グリッドの幅
    :param option_obj: オプションオブジェクト
    """
    # pdfのオープン
    print(f"Opening PDF: {input_path}")
    src_doc:fitz = fitz.open(input_path)
    new_doc:fitz = fitz.open()

    # ページごとに処理
    for i, page in enumerate(src_doc):
        orig_rect = page.rect
        new_width = orig_rect.width * 2 
        new_height = orig_rect.height   

        print(f"Page {i+1}: original size = ({orig_rect.width:.2f} x {orig_rect.height:.2f})")
        print(f"Page {i+1}: new size      = ({new_width:.2f} x {new_height:.2f})")


        # 新しいページ作成（A4縦に固定）
        new_page = new_doc.new_page(width=new_width, height=new_height)

        clip_height = 0

        # クリップ指定がある場合
        if option_obj.get(i+1) is not None:
            clip_height = option_obj.get(i+1)
            print(f"Page {i+1}: clip height = ({clip_height:.2f})")
            # clip指定範囲の出力
            new_page.show_pdf_page(
                rect = fitz.Rect(0, 0, orig_rect.width, clip_height),# 描画位置がおかしいなら修正
                src = src_doc,
                pno = i,
                clip = fitz.Rect(0, 0, orig_rect.width, clip_height)
            )



        # 元のページを新しいページに描画
        # 左側
        new_page.show_pdf_page(
            rect = fitz.Rect(0, clip_height, divide, orig_rect.height),
            src = src_doc,
            pno = i,
            clip = fitz.Rect(0, clip_height, divide, orig_rect.height) 
        )
        # 右側
        new_page.show_pdf_page(
            rect = fitz.Rect(orig_rect.width, clip_height, 2*orig_rect.width - divide, orig_rect.height),
            src = src_doc,
            pno = i,
            clip = fitz.Rect(divide, clip_height, orig_rect.width, orig_rect.height) 
        )

        # 罫線を描画
        GRID_OFFSET = 10
        # 左側の余白に罫線を描画
        for y in range(clip_height, int(new_height), grid_width):
            new_page.draw_line(fitz.Point(divide + GRID_OFFSET, y), fitz.Point(orig_rect.width - GRID_OFFSET, y), color=(0, 0, 0), width=0.5)

        # 右側の余白に罫線を描画
        for y in range(clip_height, int(new_height), grid_width):
            new_page.draw_line(fitz.Point(2*orig_rect.width -  divide + GRID_OFFSET, y), fitz.Point(new_width - GRID_OFFSET, y), color=(0, 0, 0), width=0.5)


    print(f"Saving to: {output_path}")
    new_doc.save(output_path)
    print("Done!")

def show_help():
    print("Usage: python rs04.py <input_pdf_file> [options]")
    print("Options:")
    print("  --divide=<value>       Set the divide position (default: A4_WIDTH // 2)")
    print("  --grid_width=<value>   Set the grid width (default: 20)")
    print("  --clip=page_number: clip_height,page_number2: clip_height2,...   Set the clip height for specific pages")
    print("  --output=<output_file> Set the output PDF file name")
    # print("  --input=<input_file>   Set the input PDF file name")
    print("  --help                 Show this help message")
    sys.exit(0)



#################
### 使用例 ########
#################
if __name__ == "__main__":
    if sys.argv[1] == "--help":
        show_help()
    if len(sys.argv) < 2:
        print("python rs04.py <input_pdf_file> \nで実行してください。\nまたは、python rs04.py --help でヘルプを表示します。")
        sys.exit(1)  # エラーコード 1 で終了


    INPUT_PDF = sys.argv[1]  # 入力PDFのファイル名を指定
    if not INPUT_PDF.endswith(".pdf"):
        print("エラー: 入力ファイルはPDF形式である必要があります。")
        sys.exit(1)

    OUTPUT_PDF = INPUT_PDF.replace(".pdf", "_converted.pdf")  # 出力PDFのファイル名を指定
    A4_WIDTH = 595 
    A4_HEIGHT = 842
    divide = A4_WIDTH // 2  # A4サイズの半分
    grid_width = 20
    option_obj = {} # ページ番号をキーにして、クリップする高さを指定
    # 例: 1ページ目のクリップ高さを100 & 2ページ目のクリップ高さを200に設定:option_obj = {1: 100, 2: 200}

    # sys.argv[2] 以降の引数をオプションとして取得
    while len(sys.argv) > 2:
        arg = sys.argv.pop(2)
        if arg.startswith("--divide="):
            divide = int(arg.split("=")[1])
        elif arg.startswith("--grid_width="):
            grid_width = int(arg.split("=")[1])
        elif arg.startswith("--clip="): # --clip={page_number: clip_height}
            print(f"arg: {arg}")
            # 引数を辞書に変換
            clip_arg = arg.split("=")[1]
            print(f"clip_arg: {clip_arg}")
            # 例: --clip={1: 100, 2: 200}
            # 文字列を辞書に変換する
            # clip_arg = clip_arg.replace("{", "").replace("}", "")
            if "," in clip_arg:
                # 例: 1: 100, 2: 200
                clip_arg = clip_arg.split(",")
            else:
                # 例: 1: 100
                clip_arg = [clip_arg]

            while len(clip_arg) > 0:
                # 例: 1: 100
                print(f"clip_arg: {clip_arg}")
                page_number, clip_height = clip_arg.pop(0).split(":")
                # 辞書に追加
                option_obj[int(page_number)] = int(clip_height)
        elif arg.startswith("--output="):
            OUTPUT_PDF = arg.split("=")[1]
        # elif arg.startswith("--input="):
        #     INPUT_PDF = arg.split("=")[1]
        elif arg.startswith("--help"):
            show_help()
        else:
            print(f"Unknown option: {arg}")
            sys.exit(1)
    """
    page_number: clip_height,
    # 例: 1ページ目のクリップ高さを100 & 2ページ目のクリップ高さを200に設定
    option_obj = {1: 100,2: 200}
    """
    try:
        process(
            input_path=INPUT_PDF, 
            output_path=OUTPUT_PDF,
            divide=divide,
            grid_width=grid_width, 
            option_obj=option_obj
            )
        ####################################
        ### それぞれ、結果に合わせて変更してください。
        ### 分割がずれる場合：divide
        ### 罫線の幅を変更する場合：grid_width
        ### ページの上部を切り抜かないように指定する場合：option_obj
        ####################################
    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{INPUT_PDF}' が見つかりません。")
        sys.exit(1)
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        sys.exit(1)

