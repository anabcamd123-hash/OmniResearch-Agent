class OmniResearchError(Exception):
    pass


class ProviderError(OmniResearchError):
    pass


class ToolError(OmniResearchError):
    pass


class AgentError(OmniResearchError):
    pass


class WorkflowError(OmniResearchError):
    pass


class ConfigError(OmniResearchError):
    pass
