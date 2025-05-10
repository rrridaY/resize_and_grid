"""
# rs02.py
# 縦の長さはA4サイズ変更する
# 右側に指定した余白を追加する

注意点
元のページの高さが A4 より高いと、一部が切れる可能性があります。


"""

import fitz  # PyMuPDF
import sys

def add_right_margin_and_fix_height(input_path, output_path, margin=300, a4_height=842):
    print(f"Opening PDF: {input_path}")
    src_doc = fitz.open(input_path)
    new_doc = fitz.open()

    for i, page in enumerate(src_doc):
        orig_rect = page.rect
        new_width = orig_rect.width + margin
        new_height = a4_height  # 高さを固定

        print(f"Page {i+1}: original size = ({orig_rect.width:.2f} x {orig_rect.height:.2f})")
        print(f"Page {i+1}: new size      = ({new_width:.2f} x {new_height:.2f})")

        # 新しいページ作成（A4縦に固定）
        new_page = new_doc.new_page(width=new_width, height=new_height)

        # 元のページを新しいページに描画（左上起点）
        new_page.show_pdf_page(
            fitz.Rect(0, 0, orig_rect.width, orig_rect.height),
            src_doc,
            i
        )

    print(f"Saving to: {output_path}")
    new_doc.save(output_path)
    print("Done!")

# 使用例
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python rs02.py <input_pdf_file> \nで実行してください。")
        sys.exit(1)  # エラーコード 1 で終了

    INPUT_PDF = sys.argv[1]  # 最初のコマンドライン引数を入力PDFとする
    OUTPUT_PDF = "output.pdf" # 出力ファイル名は固定または引数で指定も可能

    try:
        add_right_margin_and_fix_height(INPUT_PDF, OUTPUT_PDF, margin=300)
    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{INPUT_PDF}' が見つかりません。")
        sys.exit(1)
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        sys.exit(1)