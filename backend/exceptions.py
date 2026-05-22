class OmniResearchError(Exception):
    pass


class ProviderError(OmniResearchError):
    pass


class ToolError(OmniResearchError):
    pass


class ToolTimeoutError(OmniResearchError):
    pass


class CircuitBreakerOpenError(OmniResearchError):
    pass


class AgentError(OmniResearchError):
    pass


class WorkflowError(OmniResearchError):
    pass


class ConfigError(OmniResearchError):
    pass
