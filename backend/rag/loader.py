import fitz


class PDFLoader:

    def load(self, path):

        doc = fitz.open(path)

        text = ""

        for page in doc:
            text += page.get_text()

        return text
