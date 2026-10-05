import pymupdf

def extract_text(file):
    pdf_bytes = file.getvalue()
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text()

    doc.close()
    return text