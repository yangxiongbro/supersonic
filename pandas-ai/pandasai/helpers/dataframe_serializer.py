import typing

if typing.TYPE_CHECKING:
    from ..dataframe.base import DataFrame


class DataframeSerializer:
    def __init__(self) -> None:
        pass

    @staticmethod
    def serialize(df: "DataFrame", dialect: str = "postgres") -> str:
        """
        Convert df to csv like format where csv is wrapped inside <dataframe></dataframe>
        Args:
            df (pd.DataFrame): PandaAI dataframe or dataframe

        Returns:
            str: dataframe stringify
        """
        if df.schema.source.type=='parquet':#本地文件
            table_name=df.schema.name
        else:
            if df.schema.source.type=='trino':
                table_name=df.schema.source.connection.database+"."+df.schema.source.table
            else:
                table_name=df.schema.source.table
            
        dataframe_info = f"<table dialect='{dialect}' table_name='{table_name}'"

        # Add description attribute if available
        if df.schema.description is not None:
            dataframe_info += f" description='{df.schema.description}'"

        # dataframe_info += f" dimensions='{df.rows_count}x{df.columns_count}'>"
        dataframe_info += f" >"
        if df.schema.source.view is not None:
            dataframe_info+=f"<!-- 当view存在时，表示数据表是一个视图表达式，生成SQL时应该用视图替换表名 -->"
            dataframe_info += f" <view>\n{df.schema.source.view}\n</view>"

        # dataframe_info+=f"\n<sample_data>"

        # # Add dataframe details
        # columnDict={}
        # for col in df.schema.columns:
        #     columnDict[col.alias]=col.name
        # dfhead=df.head().rename(columns=columnDict)
        # dataframe_info += f"\n{dfhead.to_csv(index=False)}"
        # # dataframe_info += f"\n{df.head().to_csv(index=False)}"

        # dataframe_info+=f"</sample_data>"

        print(df.schema.relations)

        relationDict={}
        if df.schema.relations:
            for rela in df.schema.relations:
                relationDict.setdefault(rela.to, []).append(rela.from_)

        dataframe_info+=(
            "<!-- 生成SQL时，引用的字段必须是以下定义的，不要凭空捏造不存在的字段，"
            "一般情况下，SQL使用column属性中的name作为字段名称，当expression不为空时，表示字段由表达式表示，必须expression的值作为字段，否则会出错。"
            "relation为关联关系数组，同一字段可能会有多个关联关系，根据情况选择合适的关联关系，注意不要循环关联 -->"
        )
        dataframe_info+=f"\n<columns>"
        for col in df.schema.columns:
            dataframe_info+=f"\n<column name='"+col.name+f"' type='"+col.type+"'"
            if col.alias is not None and col.alias!="":
                dataframe_info+=f" alias='"+col.alias+"'"
            if col.description is not None and col.description!="":
                dataframe_info+=f" description='"+col.description+f"'"
            if col.expression is not None and col.expression!="":
                dataframe_info+=f" expression='"+col.expression+f"'"
            if relationDict.get(col.name, None) is not None:
                joins = ",".join(f"'{join_table}'" for join_table in relationDict[col.name])
                dataframe_info+=f" relation=[{joins}]"
            dataframe_info+="/>"
            
        dataframe_info+=f"\n</columns>"
        
        # Close the dataframe tag
        dataframe_info += "\n</table>\n"

        return dataframe_info