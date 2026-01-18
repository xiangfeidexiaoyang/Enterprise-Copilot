import os
from fastapi import FastAPI, HTTPException, Depends
from dotenv import load_dotenv

# 导入本地模块
from app.models import (
    SQLAnalysisRequest, 
    KnowledgeQueryRequest, 
    BaseResponse, 
    SQLResultData, 
    RAGResultData
)
# 注意：这里假设你已经创建了 sql_agent.py 和 rbac_rag.py
# 如果没有真实数据库连接，运行时会报错，但这作为代码展示是完美的
from app.sql_agent import SQLAgentEngine
from app.rbac_rag import RBACRetriever

# 加载环境变量
load_dotenv()

# 初始化 App
app = FastAPI(
    title="Enterprise Copilot API",
    description="基于 DeepSeek 和 RAG 的企业级智能助手接口服务",
    version="1.0.0"
)

# --- Dependency Injection (模拟依赖注入) ---
# 在真实生产环境中，这里会连接真实的 MySQL 和 Milvus
# 为了 GitHub 展示，我们在代码里保留结构，但可以用 try-except 包裹防止启动崩溃

def get_sql_engine():
    try:
        # 这里的 URI 仅为示例
        return SQLAgentEngine(
            db_uri=os.getenv("DB_URI", "mysql+pymysql://user:pass@localhost/erp"),
            api_key=os.getenv("DEEPSEEK_API_KEY", "mock-key")
        )
    except Exception as e:
        # 如果连接失败（因为你没起数据库），返回 None，仅做演示
        print(f"Warning: DB Connection failed: {e}")
        return None

# --- API Endpoints ---

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "running", "version": "1.0.0"}

@app.post("/api/v1/analysis/text-to-sql", response_model=BaseResponse)
async def analyze_data(
    request: SQLAnalysisRequest,
    engine: SQLAgentEngine = Depends(get_sql_engine)
):
    """
    数据分析接口 (Text-to-SQL)
    核心逻辑：Schema Linking -> SQL Generation -> Self-Correction
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Database Service Unavailable (Demo Mode)")

    try:
        # 1. 生成 SQL (包含 Schema Linking 和 Few-shot)
        sql = engine.generate_sql(request.query)
        
        # 2. 模拟执行结果 (Demo 用)
        # result = engine.db.run(sql) 
        result = [{"product": "Product A", "sales": 120000}] 
        
        return BaseResponse(
            data=SQLResultData(
                generated_sql=sql,
                execution_result=result,
                explanation="Successfully generated SQL via DeepSeek-Coder."
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/knowledge/ask", response_model=BaseResponse)
async def ask_knowledge_base(request: KnowledgeQueryRequest):
    """
    知识库问答接口 (Permission-Aware RAG)
    核心逻辑：Token Parsing -> Pre-filtering -> Retrieval -> Generation
    """
    try:
        # 1. 模拟 RBAC 角色解析
        # 在 rbac_rag.py 中定义的逻辑
        user_role = "student" if "student" in request.user_token else "teacher"
        filter_expr = f"array_contains(acl, '{user_role}')"
        
        # 2. 模拟检索 (Mock)
        # 真实场景调用: docs = rbac_retriever.retrieve(request.question, request.user_token)
        
        return BaseResponse(
            data=RAGResultData(
                answer=f"根据知识库（已过滤角色: {user_role}），报销标准为...",
                source_documents=["policy_v2.pdf (Page 10)", "finance_2024.docx"],
                permission_filter=filter_expr
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))