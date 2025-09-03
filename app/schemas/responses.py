from pydantic import BaseModel, ConfigDict

class HomeResponse(BaseModel):
    message: str
    version: str
    status: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "LLM Text Processor API",
                "version": "0.1.0",
                "status": "running"
            }
        }
    )

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "service": "llm-text-processor",
                "version": "0.1.0"
            }
        }
    )
