# 🛡️ Enterprise Copilot - Intelligent Data Assistant

![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green) ![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek_Coder-blue) ![Milvus](https://img.shields.io/badge/VectorDB-Milvus-orange)

基于 **DeepSeek-Coder** 和 **RAG** 技术构建的企业级智能助手，实现了 **Text-to-SQL 自动化报表查询** 与 **带权限控制的文档问答**。

> **Note**: This is a demo version of the core logic from a school-enterprise cooperation project.
> (注：本项目为校企合作项目的核心逻辑脱敏演示版)

## 🌟 核心特性 (Key Features)

### 1. 📊 Data Analysis Agent (Text-to-SQL)
- **Schema Linking**: 智能提取 Query 相关表结构，减少上下文 Token 消耗。
- **Few-shot Prompting**: 注入业务场景 SQL 示例，生成准确率 > 90%。
- **Self-Correction**: 具备“执行-报错-自动修复”闭环能力。

### 2. 🔐 Permission-Aware RAG (权限感知检索)
- **RBAC Integration**: 深度集成基于角色的访问控制。
- **Pre-filtering**: 在向量检索前置入 Metadata 过滤条件 `expr="array_contains(acl, role)"`，从根源杜绝越权访问。

### 3. 📄 Unstructured ETL
- **PaddleOCR Pipeline**: 集成 OCR 识别扫描件与图片。
- **Markdown Reformatting**: 利用 LLM 重构复杂表格结构。

## 🛠️ 架构设计

```python
# Text-to-SQL Self-Correction Flow
User Query -> Schema Linking -> DeepSeek-Coder -> Generate SQL 
    -> Dry Run (Explain) 
    -> [If Error] -> Feed Error back to LLM -> Re-generate -> Execute