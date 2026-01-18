from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict

# --- Request Models (请求体) ---

class SQLAnalysisRequest(BaseModel):
    query: str = Field(
        ..., 
        description="用户的自然语言查询", 
        example="查询上个季度销售额前三的产品"
    )
    table_scope: Optional[List[str]] = Field(
        default=None, 
        description="可选：限制查询的表范围，用于 Schema Linking 优化"
    )

class KnowledgeQueryRequest(BaseModel):
    question: str = Field(
        ..., 
        description="针对知识库的提问", 
        example="公司的差旅报销标准是什么？"
    )
    user_token: str = Field(
        ..., 
        description="模拟用户 Token (用于 RBAC 权限解析)", 
        example="eyJhbGciOiJIUzI1... (student_role)"
    )
    top_k: int = Field(default=3, ge=1, le=10)

# --- Response Models (响应体) ---

class BaseResponse(BaseModel):
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="提示信息")
    data: Optional[Any] = None

class SQLResultData(BaseModel):
    generated_sql: str
    execution_result: List[Dict[str, Any]]
    explanation: str

class RAGResultData(BaseModel):
    answer: str
    source_documents: List[str]
    permission_filter: str # 展示使用了什么权限过滤条件