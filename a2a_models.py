from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum

# Define Enums
class TaskState(str, Enum):
    submitted = "submitted"
    working = "working"
    input_required = "input-required"
    completed = "completed"
    canceled = "canceled"
    failed = "failed"
    unknown = "unknown"

# Define basic Part types
class TextPart(BaseModel):
    type: str = "text"
    text: str
    metadata: Optional[Dict[str, Any]] = None

class FileContent(BaseModel):
    name: Optional[str] = None
    mimeType: Optional[str] = None
    bytes: Optional[str] = None # Base64 encoded bytes
    uri: Optional[str] = None

    @validator('uri', always=True)
    def check_bytes_or_uri(cls, v, values):
        if values.get('bytes') is None and v is None:
            raise ValueError('Either bytes or uri must be provided')
        if values.get('bytes') is not None and v is not None:
            raise ValueError('Only one of bytes or uri can be provided')
        return v

class FilePart(BaseModel):
    type: str = "file"
    file: FileContent
    metadata: Optional[Dict[str, Any]] = None

class DataPart(BaseModel):
    type: str = "data"
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

# Define the union type for Part
Part = Union[TextPart, FilePart, DataPart]

class Message(BaseModel):
    role: str # Can be "user" or "agent" based on context, schema says enum but leaving as str for flexibility
    parts: List[Part]
    metadata: Optional[Dict[str, Any]] = None

class Artifact(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parts: List[Part]
    index: int = 0
    append: Optional[bool] = None
    lastChunk: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskStatus(BaseModel):
    state: TaskState
    message: Optional[Message] = None
    timestamp: Optional[str] = None # Should be a datetime string

class Task(BaseModel):
    id: str
    sessionId: Optional[str] = None
    status: TaskStatus
    artifacts: Optional[List[Artifact]] = None
    history: Optional[List[Message]] = None
    metadata: Optional[Dict[str, Any]] = None

class AuthenticationInfo(BaseModel):
    schemes: List[str]
    credentials: Optional[str] = None

class PushNotificationConfig(BaseModel):
    url: HttpUrl
    token: Optional[str] = None
    authentication: Optional[AuthenticationInfo] = None

class TaskIdParams(BaseModel):
    id: str
    metadata: Optional[Dict[str, Any]] = None

class TaskQueryParams(BaseModel):
    id: str
    historyLength: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskSendParams(BaseModel):
    id: str
    sessionId: Optional[str] = None
    message: Message
    pushNotification: Optional[PushNotificationConfig] = None
    historyLength: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskPushNotificationConfig(BaseModel):
    id: str
    pushNotificationConfig: PushNotificationConfig

# Define Request/Response/Event models based on JSON-RPC 2.0
class JSONRPCMessage(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[int, str]] = None

class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

class JSONRPCResponse(JSONRPCMessage):
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None

class JSONRPCRequest(JSONRPCMessage):
    method: str

# Specific Request/Response models
class SendTaskRequest(JSONRPCRequest):
    method: Literal["tasks/send"] = "tasks/send"
    params: TaskSendParams = Field(...)

class SendTaskResponse(JSONRPCResponse):
    result: Optional[Task] = None
    error: Optional[JSONRPCError] = None

class GetTaskRequest(JSONRPCRequest):
    method: Literal["tasks/get"] = "tasks/get"
    params: TaskQueryParams = Field(...)

class GetTaskResponse(JSONRPCResponse):
    result: Optional[Task] = None
    error: Optional[JSONRPCError] = None

class CancelTaskRequest(JSONRPCRequest):
    method: Literal["tasks/cancel"] = "tasks/cancel"
    params: TaskIdParams = Field(...)

class CancelTaskResponse(JSONRPCResponse):
    result: Optional[Task] = None
    error: Optional[JSONRPCError] = None

class SetTaskPushNotificationRequest(JSONRPCRequest):
    method: Literal["tasks/pushNotification/set"] = "tasks/pushNotification/set"
    params: TaskPushNotificationConfig = Field(...)

class SetTaskPushNotificationResponse(JSONRPCResponse):
    result: Optional[TaskPushNotificationConfig] = None
    error: Optional[JSONRPCError] = None

class GetTaskPushNotificationRequest(JSONRPCRequest):
    method: Literal["tasks/pushNotification/get"] = "tasks/pushNotification/get"
    params: TaskIdParams = Field(...)

class GetTaskPushNotificationResponse(JSONRPCResponse):
    result: Optional[TaskPushNotificationConfig] = None
    error: Optional[JSONRPCError] = None

class TaskResubscriptionRequest(JSONRPCRequest):
    method: Literal["tasks/resubscribe"] = "tasks/resubscribe"
    params: TaskQueryParams = Field(...)

# Event models (used in streaming, but defining structure)
class TaskStatusUpdateEvent(BaseModel):
    id: str
    status: TaskStatus
    final: bool = False
    metadata: Optional[Dict[str, Any]] = None

class TaskArtifactUpdateEvent(BaseModel):
    id: str
    artifact: Artifact
    metadata: Optional[Dict[str, Any]] = None

# Union of possible A2A Requests
A2ARequest = Union[
    SendTaskRequest,
    GetTaskRequest,
    CancelTaskRequest,
    SetTaskPushNotificationRequest,
    GetTaskPushNotificationRequest,
    TaskResubscriptionRequest
]

# Union of possible A2A Streaming Responses (Events)
A2AStreamingResponse = Union[
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent
]
