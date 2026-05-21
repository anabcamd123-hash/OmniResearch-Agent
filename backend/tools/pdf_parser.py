import fitz


class PDFParser:

    def parse(
        self,
        path
    ):

        doc = fitz.open(path)

        text = ""

        for page in doc:

            text += page.get_text()

        return text[:5000]
