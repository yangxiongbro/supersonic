import traceback
import warnings
from typing import Any, List, Optional, Union
import asyncio
import duckdb
import pandas as pd
import re,json
from sqlalchemy import create_engine

from pandasai.core.code_execution.code_executor import CodeExecutor
from pandasai.core.code_generation.base import CodeGenerator
from pandasai.core.prompts import (
    get_chat_prompt_for_sql,
    get_correct_error_prompt_for_sql,
    get_correct_output_type_error_prompt,
    get_analyze_report_prompt
)

from pandasai.core.response.error import ErrorResponse
from pandasai.core.response.parser import ResponseParser
from pandasai.core.user_query import UserQuery
from pandasai.dataframe.base import DataFrame
from pandasai.dataframe.virtual_dataframe import VirtualDataFrame
from pandasai.exceptions import (
    CodeExecutionError,
    InvalidLLMOutputType,
    MissingVectorStoreError,
)
from pandasai.sandbox import Sandbox
from pandasai.vectorstores.vectorstore import VectorStore

from .. import SqlQueryBuilder
from ..config import Config
from ..constants import LOCAL_SOURCE_TYPES
from ..data_loader.duck_db_connection_manager import DuckDBConnectionManager
from ..query_builders.base_query_builder import BaseQueryBuilder
from ..query_builders.sql_parser import SQLParser
from .state import AgentState
from pandasai.core.prompts.base import BasePrompt


class Agent:
    """
    Base Agent class to improve the conversational experience in PandaAI
    """

    def __init__(
        self,
        dfs: Union[
            Union[DataFrame, VirtualDataFrame], List[Union[DataFrame, VirtualDataFrame]]
        ],
        config: Optional[Union[Config, dict]] = None,
        memory_size: Optional[int] = 10,
        vectorstore: Optional[VectorStore] = None,
        description: str = None,
        sandbox: Sandbox = None,
    ):
        """
        Args:
            dfs (Union[Union[DataFrame, VirtualDataFrame], List[Union[DataFrame, VirtualDataFrame]]]): The dataframe(s) to be used for the conversation.
            config (Optional[Union[Config, dict]]): The configuration for the agent.
            memory_size (Optional[int]): The size of the memory.
            vectorstore (Optional[VectorStore]): The vectorstore to be used for the conversation.
            description (str): The description of the agent.
        """
        # 获取trino连接地址

        # Deprecation warnings
        if config is not None:
            warnings.warn(
                "The 'config' parameter is deprecated and will be removed in a future version. "
                "Please use the global configuration instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.trino_host=dfs[0].schema.source.connection.host
        self.trino_user=dfs[0].schema.source.connection.user
        self.trino_password=dfs[0].schema.source.connection.password
        self.trino_port=dfs[0].schema.source.connection.port

        # if isinstance(dfs, list):
        #     sources = [df.schema.source for df in dfs]
        #     if not BaseQueryBuilder.check_compatible_sources(sources):
        #         raise ValueError(
        #             f"The sources of these datasets: {dfs} are not compatibles"
        #         )

        
        self.description = description
        self._state = AgentState()
        self._state.initialize(dfs, config, memory_size, vectorstore, description)

        self._code_generator = CodeGenerator(self._state)
        self._response_parser = ResponseParser()
        self._sandbox = sandbox

    def chat(self, query: str, output_type: Optional[str] = None):
        """
        Start a new chat interaction with the assistant on Dataframe.
        """
        self.start_new_conversation()
        retResult=[]
        errResult=[]
        resultArr=self._process_query(query, output_type)
        for result in resultArr:
            if result is None or not isinstance(result,dict) or "data" not in result.keys() or result["data"] is None:
                continue
            result["analyze"]=self._execute_data_analyze(data=result["data"],userQuery=result["question"],explanatory=result["explanatory"])
            retResult.append(result)
        return retResult

    def follow_up(self, query: str, output_type: Optional[str] = None):
        """
        Continue the existing chat interaction with the assistant on Dataframe.
        """
        return self._process_query(query, output_type)

    def generate_code(self, query: Union[UserQuery, str]) -> str:
        """Generate code using the LLM."""

        # self._state.memory.add(str(query), is_user=True)

        # self._state.logger.log("Generating new code...")
        # prompt = get_chat_prompt_for_sql(self._state)
        prompt=self.generate_prompt(query)

        code = self._code_generator.generate_code(prompt)
        self._state.last_prompt_used = prompt
        return code
    async def load_from_trino(self,query):
    # 配置Trino连接字符串
        # 格式：trino://[username:password@]host:port/[catalog.schema]
        # 注意：如果使用用户名和密码，它们应该以用户名:密码的形式放在URL中。
        # 如果你使用的是Kerberos认证或其他认证方式，你可能需要配置额外的参数。    
        loop = asyncio.get_event_loop()
        if self.trino_password:
            engine = create_engine(
            f"""trino://{self.trino_user}@{self.trino_host}:{self.trino_port}""",
            connect_args={
            "http_scheme": "http",  # 或 "https" 如果启用了 TLS
            "auth": "basic",        # 指定使用基本认证
            "password": self.trino_password
            }
            )
        else:
            engine = create_engine(
            f"""trino://{self.trino_user}@{self.trino_host}:{self.trino_port}"""
            )            
        df = await loop.run_in_executor(None, pd.read_sql, query, engine) 
        return df     
    async def _gen_result(self,response,result):
        pattern_json = r"\[(.*?)\]"
        match_json = re.search(pattern_json, response, re.DOTALL)
        if match_json:
            response = match_json.group(1).strip() 
            response=f'[{response}]'     
        sqlArr=json.loads(response)
        for el in sqlArr:
            dataEl={}
            result.append(dataEl) 
            sql=el["sql"]
            # 执行sql
            pattern = r"```sql(.*?)```"
            match = re.search(pattern, sql, re.DOTALL)
            if match:
                sql = match.group(1).strip()
            dataEl["sql"]=sql
            # 执行sql
            sqlArr = SQLParser.transpile_sql_dialect(sql, to_dialect="trino")
            print("======最终的sql====\n"+sql)
            dataEl["errsql"]=sql
            df:pd.DataFrame=await self.load_from_trino(sql)
            dataEl["question"]=el["question"]
            dataEl["explain"]=el["explain"]
            dataEl["data"]=df
            dataEl["vis"]=el["vis"]
                   
    async def generate_data_with_retries(self, query: Union[UserQuery, str]):
            """Generate code using the LLM."""
            max_retries = self._state.config.max_retries
            attempts = 0
            result=[]
            response=""
            errsql=""
            prompt=""
            while attempts < max_retries:
                result.clear()
                if attempts==0:#第一次生成                        
                    prompt=self.generate_prompt(query)
                    response = await self._code_generator.generate_code(prompt)
                
                if response is None:
                    # 表示大模型出错，跳出循环
                    result=[]
                    raise Exception("大模型服务异常")
                    # break
                self._state.last_prompt_used = prompt
                try:
                    await self._gen_result(response,result)    
                    break 
                except Exception as e:
                    # 表示执行SQL出错，则重试
                    attempts += 1
                    if attempts == max_retries:
                        raise Exception(str(e))
                    self._state.logger.log(
                        f"SQL执行出错，重新执行： ({attempts}/{max_retries})..."
                    )
                    #错误则继续生成代码，直到大于3次结束
                    self._state.code_fixing=True #表示正在修复代码中
                    # 取出执行出错的SQL
                    errsql=""
                    if len(result)>0:
                        # 进入这里表示sql查询出错
                        errsql=result[len(result)-1]["sql"]
                        response = await self._regenerate_data_after_error(response,errsql, e)  
                        # if response is None:
                        #     # 表示大模型出错，跳出循环
                        #     result=[]
                        #     break   
                    else:
                         # 进入这里表示respone不是一个合格的json
                        response = await self._code_generator.generate_code(prompt)  
                        # if response is None:
                        # # 表示大模型出错，跳出循环
                        #     result=[]
                        #     break                                     

            return result

        

    def generate_code_with_retries(self, query: Union[UserQuery, str]):
        """Generate code using the LLM."""

        max_retries = self._state.config.max_retries
        attempts = 0
        code_exe=""
        while attempts <= max_retries:
            try:
                if attempts==0:#第一次生成
                    
                    prompt=self.generate_prompt(query)
                    #generate_code已包含了validate_and_clean_code
                    code_exe = self._code_generator.generate_code(prompt)                    
                    self._state.last_prompt_used = prompt
                else:#错误后生成再次验证
                    code_exe=self._code_generator.validate_and_clean_code(code_exe)
                #验证后都没发生错误则返回代码
                self._state.code_fixing=False
                return code_exe
            except Exception as e:
                attempts += 1
                if attempts > max_retries:#如果3次都验证不正确，则结束，抛出异常
                    self._state.logger.log(f"生成代码错误重试次数超过了{max_retries}次. Error: {e}")
                    self._state.code_fixing=False
                    raise
                self._state.logger.log(
                    f"重新生成代码 ({attempts}/{max_retries})..."
                )
                #错误则继续生成代码，直到大于3次结束
                self._state.code_fixing=True #表示正在修复代码中
                code_exe = self._regenerate_code_after_error(code_exe, e)  
                # print(code_exe)
    

    
    def generate_prompt(self, query: Union[UserQuery, str]) -> BasePrompt:
        """Generate code using the LLM."""

        self._state.memory.add(str(query), is_user=True)
        self._state.logger.log("Generating new code...")
        prompt = get_chat_prompt_for_sql(self._state)
        return prompt    

    def execute_code(self, code: str) -> dict:
        """Execute the generated code."""
        self._state.logger.log(f"Executing code: {code}")

        code_executor = CodeExecutor(self._state.config)
        code_executor.add_to_env("execute_sql_query", self._execute_sql_query)

        if self._sandbox:
            return self._sandbox.execute(code, code_executor.environment)

        return code_executor.execute_and_return_result(code)

    @staticmethod
    def _parse_correct_table_name(query: str, dfs: List[VirtualDataFrame]) -> str:
        table_mapping = {
            df.schema.name: df.query_builder._get_table_expression() for df in dfs
        }

        return SQLParser.replace_table_and_column_names(query, table_mapping)

    def _execute_local_sql_query(self, query: str) -> pd.DataFrame:
        try:
            db_manager = DuckDBConnectionManager()
            for df in self._state.dfs:
                db_manager.register(df.schema.name, df)
            return db_manager.sql(query).df()
        except duckdb.Error as e:
            raise RuntimeError(f"SQL execution failed: {e}") from e

    def _execute_sql_query(self, query: str) -> pd.DataFrame:
        """
        Executes an SQL query on registered DataFrames.

        Args:
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: The result of the SQL query as a pandas DataFrame.
        """
        if not self._state.dfs:
            raise ValueError("No DataFrames available to register for query execution.")

        df0 = self._state.dfs[0]
        source = df0.schema.source or None

        if source and source.type in LOCAL_SOURCE_TYPES:
            return self._execute_local_sql_query(query)
        else:
            query = self._parse_correct_table_name(query, self._state.dfs)
            return df0.execute_sql_query(query)
        
    def _execute_data_analyze(self, data: pd.DataFrame,userQuery:str,explanatory:str) -> str:
        self._state.report_dataframe=data
        self._state.report_use_query=userQuery
        self._state.report_explanatory=explanatory
        prompt = get_analyze_report_prompt(self._state)
        report = self._code_generator._context.config.llm.call(prompt)
        return report    
    
     

    def execute_with_retries(self, code: str) -> Any:
        """执行代码错误重试逻辑."""
        max_retries = self._state.config.max_retries
        attempts = 0
        exe_code=code
        while attempts <= max_retries:
            try:
                exe_code=self._code_generator.validate_and_clean_code(exe_code)
                result = self.execute_code(exe_code)
                if isinstance(result,list):
                    self._state.code_fixing=False
                    return result
                else:
                    raise CodeExecutionError("result 变量不是一个数组")
                # return self._response_parser.parse(result, code)
            # except CodeExecutionError as e:
            except Exception as e:
                attempts += 1
                if attempts > max_retries:
                    self._state.logger.log(f"Max retries reached. Error: {e}")
                    self._state.code_fixing=False
                    raise
                self._state.logger.log(
                    f"Retrying execution ({attempts}/{max_retries})..."
                )
                self._state.code_fixing=True
                exe_code = self._regenerate_code_after_error(exe_code, e)

    def train(
        self,
        queries: Optional[List[str]] = None,
        codes: Optional[List[str]] = None,
        docs: Optional[List[str]] = None,
    ) -> None:
        """
        Trains the context to be passed to model
        Args:
            queries (Optional[str], optional): user user
            codes (Optional[str], optional): generated code
            docs (Optional[List[str]], optional): additional docs
        Raises:
            ImportError: if default vector db lib is not installed it raises an error
        """
        if self._state.vectorstore is None:
            raise MissingVectorStoreError(
                "No vector store provided. Please provide a vector store to train the agent."
            )

        if (queries and not codes) or (not queries and codes):
            raise ValueError(
                "If either queries or codes are provided, both must be provided."
            )

        if docs is not None:
            self._state.vectorstore.add_docs(docs)

        if queries and codes:
            self._state.vectorstore.add_question_answer(queries, codes)

        self._state.logger.log("Agent successfully trained on the data")

    def clear_memory(self):
        """
        Clears the memory
        """
        self._state.memory.clear()

    def add_message(self, message, is_user=False):
        """
        Add message to the memory. This is useful when you want to add a message
        to the memory without calling the chat function (for example, when you
        need to add a message from the agent).
        """
        self._state.memory.add(message, is_user=is_user)

    def add_node(self, note=""):
        """
        Add message to the memory. This is useful when you want to add a message
        to the memory without calling the chat function (for example, when you
        need to add a message from the agent).
        """
        self._state.note=note

    def start_new_conversation(self):
        """
        Clears the previous conversation
        """
        self.clear_memory()

    def _process_query(self, query: str, output_type: Optional[str] = None):
        """Process a user query and return the result."""
        query = UserQuery(query)
        self._state.logger.log(f"Question: {query}")
        self._state.logger.log(
            f"Running PandaAI with {self._state.config.llm.type} LLM..."
        )

        self._state.output_type = output_type
        try:
            self._state.assign_prompt_id()

            # Generate code
            code = self.generate_code(query)

            # Execute code with retries
            result = self.execute_with_retries(code)

            self._state.logger.log("Response generated successfully.")
            # Generate and return the final response
            return result

        except CodeExecutionError:
            return self._handle_exception(code)

    def _regenerate_code_after_error(self, code: str, error: Exception) -> str:
        """Generate a new code snippet based on the error."""
        error_trace = traceback.format_exc()
        self._state.logger.log(f"Execution failed with error: {error_trace}")

        if isinstance(error, InvalidLLMOutputType):
            prompt = get_correct_output_type_error_prompt(
                self._state, code, error_trace
            )
        else:
            prompt = get_correct_error_prompt_for_sql(self._state, code, error_trace)

        return self._code_generator.generate_code(prompt)
    async def _regenerate_data_after_error(self, code: str,errsql:str, error: Exception) -> str:
        response=None
        error_trace = traceback.format_exc()
        self._state.logger.log(f"Execution failed with error: {error_trace}")
        try:
            if isinstance(error, InvalidLLMOutputType):
                prompt = get_correct_output_type_error_prompt(
                    self._state, code, error_trace
                )
            else:
                # prompt = get_correct_error_prompt_for_sql(self._state, code,errsql, error_trace)
                prompt = get_correct_error_prompt_for_sql(self._state, code, error_trace)
            self._state.last_prompt_used = prompt
            response=await self._code_generator.generate_code(prompt) 
        except Exception as e:
            self._state.logger.log(f"Execution failed with error: {e}")
            response=None
        return response   

    def _handle_exception(self, code: str) -> str:
        """Handle exceptions and return an error message."""
        error_message = traceback.format_exc()
        self._state.logger.log(f"Processing failed with error: {error_message}")

        return ErrorResponse(last_code_executed=code, error=error_message)

    @property
    def last_generated_code(self):
        return self._state.last_code_generated

    @property
    def last_code_executed(self):
        return self._state.last_code_generated

    @property
    def last_prompt_used(self):
        return self._state.last_prompt_used
