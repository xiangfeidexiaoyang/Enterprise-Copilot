from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.prompts import ChatPromptTemplate

class SQLAgentEngine:
    """
    企业级 Text-to-SQL 引擎
    特性: Schema Linking, Few-shot Prompting, Self-Correction
    """
    
    def __init__(self, db_uri: str, api_key: str):
        self.db = SQLDatabase.from_uri(db_uri)
        # 使用 DeepSeek-Coder 生成 SQL
        self.llm = ChatOpenAI(
            model="deepseek-coder", 
            api_key=api_key, 
            base_url="https://api.deepseek.com",
            temperature=0
        )
    
    def _schema_linking(self, query: str) -> str:
        """
        Schema Linking: 提取 Query 中的关键实体，只加载相关的表结构
        (模拟逻辑：生产环境通常使用向量检索匹配表名)
        """
        all_tables = self.db.get_usable_table_names()
        # 简单模拟：如果 query 里包含 "销售", 则只加载 sales 表
        relevant_tables = [t for t in all_tables if t in ["sales", "users", "orders"]] 
        return self.db.get_table_info(relevant_tables)

    def _get_few_shot_examples(self) -> str:
        """
        Few-shot: 注入高频业务场景 SQL
        """
        return """
        Q: 查询上个月销售额最高的3个产品
        SQL: SELECT product_id, SUM(amount) FROM sales WHERE date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) GROUP BY product_id ORDER BY 2 DESC LIMIT 3;
        """

    def generate_sql(self, query: str) -> str:
        """
        生成 SQL (带自修正机制)
        """
        schema = self._schema_linking(query)
        prompt = f"""
        基于以下表结构生成 SQL:
        {schema}
        
        参考示例:
        {self._get_few_shot_examples()}
        
        用户问题: {query}
        SQL:
        """
        
        # 第一次尝试生成
        sql = self.llm.invoke(prompt).content
        
        # Self-Correction 闭环
        try:
            # 尝试执行 (Explain 模式，不真正执行)
            self.db.run(f"EXPLAIN {sql}")
            return sql
        except Exception as e:
            # 捕获错误，回传给模型进行修复 (Self-Debug)
            print(f"SQL Execution Error: {e}. Triggering Self-Correction...")
            fix_prompt = f"原 SQL: {sql}\n报错信息: {str(e)}\n请修正 SQL:"
            fixed_sql = self.llm.invoke(fix_prompt).content
            return fixed_sql