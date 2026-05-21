from backend.tools.github_analyzer import GitHubAnalyzerTool
from backend.tools.pdf_parser import PDFParserTool
from backend.tools.web_search import WebSearchTool
from backend.tools.rag_tool import RAGTool
from backend.rag.rag_service import rag_service


class ToolRegistry:

    def __init__(self):

        self.tools = {
            "github": GitHubAnalyzerTool(),
            "pdf": PDFParserTool(),
            "web": WebSearchTool(),
            "rag": RAGTool(rag_service),
        }

    def get(self, name: str):

        return self.tools.get(name)

    def list_tools(self):

        return {
            name: tool.description
            for name, tool in self.tools.items()
        }


registry = ToolRegistry()
