import fitz
from backend.tools.base import BaseTool


class PDFParserTool(BaseTool):

    name = "pdf"
    description = "Parse PDF documents and extract text"

    async def run(self, input: str):

        try:
            doc = fitz.open(input)
            text = ""
            for page in doc:
                text += page.get_text()
            return {"text": text[:5000]}
        except Exception as e:
            return {"error": str(e)}
