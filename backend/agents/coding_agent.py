from backend.utils.logger import logger

class CodingAgent:

    def run(self, research_result):

        logger.info("[CodingAgent] Generating code...")

        code = '''
def train():
    print("training model")
'''

        logger.info("[CodingAgent] Code generation completed")

        return {
            "code": code
        }
