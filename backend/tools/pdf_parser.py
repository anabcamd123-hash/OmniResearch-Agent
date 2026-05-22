import fitz
from backend.tools.base import BaseTool
from backend.tools.result import ToolResult


class PDFParserTool(BaseTool):

    name = "pdf"
    description = "Parse PDF documents and extract text"

    async def run(self, input: str) -> ToolResult:

        doc = fitz.open(input)
        text = ""
        for page in doc:
            text += page.get_text()

        return ToolResult(
            success=True,
            content=text[:5000],
        )
