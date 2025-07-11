"""
Copyright 2025, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from pydantic import BaseModel, Field

from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF
from graphiti_core.llm_client import  OpenAIClient,LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.utils.maintenance.graph_data_operations import clear_data
from graphiti_core.utils.bulk_utils import (
    RawEpisode,
    add_nodes_and_edges_bulk,
    dedupe_edges_bulk,
    dedupe_nodes_bulk,
    extract_edge_dates_bulk,
    extract_nodes_and_edges_bulk,
    resolve_edge_pointers,
    retrieve_previous_episodes_bulk,
)

from graphiti_core.search.search_config_recipes import (
    COMBINED_HYBRID_SEARCH_RRF,
    COMBINED_HYBRID_SEARCH_MMR,
    COMBINED_HYBRID_SEARCH_CROSS_ENCODER,
    EDGE_HYBRID_SEARCH_NODE_DISTANCE,
    EDGE_HYBRID_SEARCH_RRF,
)


#################################################
# CONFIGURATION
#################################################
# Set up logging and environment variables for
# connecting to Neo4j database
#################################################

# Configure logging
logging.basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

load_dotenv()

# Neo4j connection parameters
# Make sure Neo4j Desktop is running with a local DBMS started
os.environ['OPENAI_API_KEY']='8e8723a1-8032-4213-9752-748fbd9fbd70'
neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
neo4j_password = os.environ.get('NEO4J_PASSWORD', 'neo4j@2025')

if not neo4j_uri or not neo4j_user or not neo4j_password:
    raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')


async def main():
    #################################################
    # INITIALIZATION
    #################################################
    # Connect to Neo4j and set up Graphiti indices
    # This is required before using other Graphiti
    # functionality
    #################################################

    namespace="product_sale"

    # Initialize Graphiti with Neo4j connection
    config=LLMConfig(
                        api_key='8e8723a1-8032-4213-9752-748fbd9fbd70',
                        model='deepseek-v3-241226',
                        # model="deepseek-r1-250120",
                        base_url='https://ark.cn-beijing.volces.com/api/v1'
                    )
    embed_config=OpenAIEmbedderConfig(
        embedding_dim=1024,
        embedding_model='doubao-embedding-text-240715',
        base_url='https://ark.cn-beijing.volces.com/api/v3'
    )
    graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password,
                        llm_client=OpenAIGenericClient(
                                config=config                        
                            ),
                            embedder=OpenAIEmbedder(config=embed_config)
                        )

    try:
        # Initialize the graph database with graphiti's indices. This only needs to be done once.


        #################################################
        # ADDING EPISODES
        #################################################
        # Episodes are the primary units of information
        # in Graphiti. They can be text or structured JSON
        # and are automatically processed to extract entities
        # and relationships.
        #################################################

        # Example: Add Episodes
        # Episodes list containing both text and JSON episodes
        d=True
        d=False
        if d:
            await clear_data(graphiti.driver)

            await graphiti.build_indices_and_constraints()             
            # episodes = [
            #     {
            #         'content': "顾客: 我的笔记本好像出现了故障，电池只能用半个钟，充电时屏幕会出现黑屏"
            #         "客服人员: 你能可以用手机录屏发给我吗，便于我们进一步排查故障",
            #         'type': EpisodeType.message,
            #         'description': '客服和顾客日常沟通',
            #     }
            # ]
            product_data = [
                {
                "name": "order_items",
                "alias":"订单明细记录表",
                "description": "订单明细记录表，一个订单有多条明细记录",
                "columns": [
                {
                    "name": "item_id",
                    "type": "integer",
                    "alias": "订单明细记录ID",
                    "description": "唯一ID"
                },
                {
                    "name": "order_id",
                    "type": "integer",
                    "alias": "订单ID",
                    "description": "订单ID，外键，和订单表主键order_id字段关联，表示订单明细表和订单表有关联"
                },
                {
                    "name": "product_id",
                    "type": "integer",
                    "alias": "产品ID",
                    "description": "产品ID，外键，和产品表主键product_id字段关联，表示订单明细表和订单表有关联，业务上表示购买了什么产品，可以获取所产品信息"
                },
                {
                    "name": "quantity",
                    "type": "integer",
                    "alias": "购买数量",
                    "description": "购买产品的数量"
                },
                {
                    "name": "list_price",
                    "type": "float",
                    "alias": "价格",
                    "description": "表示本地售出产品的实际价格，和产品表的标价可能不一致"
                },
                {
                    "name": "create_time",
                    "type": "datetime",
                    "alias": "购买日期",
                    "description": "购买日期"
                }
                ]
            },
            {
                "name": "products",
                "alias":"产品信息表",
                "description": "产品信息表，记录产品的详细信息",
                "columns": [
                {
                    "name": "product_id",
                    "type": "integer",
                    "alias": "产品ID",
                    "description": "主键，产品唯一ID"
                },
                {
                    "name": "product_name",
                    "type": "string",
                    "alias": "产品名称",
                    "description": "产品名称"
                },
                {
                    "name": "brand_id",
                    "type": "integer",
                    "alias": "品牌ID",
                    "description": "品牌ID"
                },
                {
                    "name": "category_id",
                    "type": "integer",
                    "alias": "类别ID",
                    "description": "产品类别ID"
                },
                {
                    "name": "list_price",
                    "type": "float",
                    "alias": "价格",
                    "description": "产品的标价"
                }
                ]
            },
            
            {
                "name": "orders",
                "alias":"订单表",
                "description": "订单表，记录客户订单记录，统计订单总数请使用该表，一个订单有多条订单明细记录",
                "columns": [
                {
                    "name": "order_id",
                    "type": "integer",
                    "alias": "订单ID",
                    "description": "主键，订单唯一ID"
                },
                {
                    "name": "order_status",
                    "alias": "订单状态",
                    "type": "integer",
                    "description": "订单状态，用以下值表示：1-接单,2-出库 ,3-运送中,4-完成"
                },
                {
                    "name": "order_date",
                    "type": "datetime",
                    "alias": "订单日期",
                    "description": "订单日期，表示客户购买下订单的日期"
                },
                {
                    "name": "store_id",
                    "type": "integer",
                    "alias": "门店ID",
                    "description": "门店ID，外键，关联门店表"
                }
                ]
            }  
            ]

            class Table(BaseModel):
                """数据库的表实体"""
                table_name :str  | None = Field(..., description="表英文名，从name字段获取")
                description: str | None = Field(..., description="表说明")


            class Column(BaseModel):
                """表字段实体"""
                column_name :str  | None = Field(..., description="字段英文名，从name字段获取")
                type :str  | None = Field(..., description="字段类型")
                description: str | None = Field(..., description="字段说明")

            await graphiti.build_communities()
            extract_instruction=f"""
                1、用JSON方式提供一组表结构，数组中的一个元素表示一个表，columns表的字段集合
                2、必须强调，优先从json的alias获取值设置实体的name，如果没有alias，则从description获取值设置name，如果也没有description，则获取name设置到实体的name
                3、每个表必须是一个实体，外层的name表示表英文名，设置到表实体的table_name，alias表示表名，设置到实体的name，description是表的描述，设置到实体的description，并根据description总结表节点的summary，
                4、每个字段必须是一个实体，而且一定要和表建立关系一起构建三元组，alias表示字段中文名，设置到字段实体的column_name，name表示字段名，设置到实体的name，type表示字段类型,description是字段的说明，并根据description总结表节点的summary，
                5、字段中有表示日期的字段，是属于业务需要，所以抽取实体时一定不要忽略              
                """
            for table in product_data:

                await graphiti.add_episode(
                    name=f"table_{table['name']}",
                    episode_body=json.dumps(table),
                    source=EpisodeType.json,
                    source_description="数据库表集合",
                    group_id=namespace,
                    update_communities=True,
                    reference_time=datetime.now(),
                    entity_types={"Table":Table,"Column":Column},
                    extract_node_instruction=extract_instruction,
                    extract_edge_instruction=extract_instruction

                )
                        

            # bulk_episodes = [
            #     RawEpisode(
            #     name=f"sale_table",
            #     content=json.dumps(table),
            #     source=EpisodeType.json,
            #     source_description="""
            #     用JSON方式提供一组表结构，数组中的一个元素表示一个表，外层的name表示表名，description是表的描述，请根据description总结表节点的summary，
            #     columns是一个json数组，里面的元素表示表的字段，name表示字段名称，type表示字段类型,alias表示表的别名，description是字段的说明，请根据这些信息总结字段节点的summary，
            #     字段中有表示日期的，是属于业务需要，所以一定不要忽略
            #     """,
            #     reference_time=datetime.now(),
            
            # )
            # for table in product_data
            # ]            

            # Add the episode to the graph
            # await graphiti.add_episode_bulk(bulk_episodes,group_id="product_sale")

            # Add episodes to the graph
            # for i, episode in enumerate(episodes):
            #     await graphiti.add_episode(
            #         name=f'Freakonomics Radio {i}',
            #         episode_body=episode['content']
            #         if isinstance(episode['content'], str)
            #         else json.dumps(episode['content']),
            #         source=episode['type'],
            #         source_description=episode['description'],
            #         reference_time=datetime.now(timezone.utc),
            #         group_id=namespace
            #     )
            #     print(f'Added episode: Freakonomics Radio {i} ({episode["type"].value})')

        #################################################
        # BASIC SEARCH
        #################################################
        # The simplest way to retrieve relationships (edges)
        # from Graphiti is using the search method, which
        # performs a hybrid search combining semantic
        # similarity and BM25 text retrieval.
        #################################################

        # Perform a hybrid search combining semantic similarity and BM25 retrieval
        # print("\nSearching for: 'Who was the California Attorney General?'")
        # q='统计产品数量'
        # q="统计每个产品的订单数量"
        q="统计产品数量"
        # results = await graphiti.search(q,group_ids=[namespace])
        # # results = await graphiti._search(q,group_ids=[namespace])

        # # Print search results
        # print('\nSearch Results:')
        # for result in results:
        #     print(f'UUID: {result.uuid}')
        #     print(f'Fact: {result.fact}')
        #     if hasattr(result, 'valid_at') and result.valid_at:
        #         print(f'Valid from: {result.valid_at}')
        #     if hasattr(result, 'invalid_at') and result.invalid_at:
        #         print(f'Valid until: {result.invalid_at}')
        #     print('---')


        #################################################
        # NODE SEARCH USING SEARCH RECIPES
        #################################################
        # Graphiti provides predefined search recipes
        # optimized for different search scenarios.
        # Here we use NODE_HYBRID_SEARCH_RRF for retrieving
        # nodes directly instead of edges.
        #################################################

        # Example: Perform a node search using _search method with standard recipes
        # print(
        #     '\nPerforming node search using _search method with standard recipe NODE_HYBRID_SEARCH_RRF:'
        # )

        # Use a predefined search configuration recipe and modify its limit
        node_search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        # node_search_config = COMBINED_HYBRID_SEARCH_MMR.model_copy(deep=True)
        
        node_search_config.limit = 10  # Limit to 5 results

        # Execute the node search
        node_search_results = await graphiti._search(
            query=q,
            config=node_search_config,
        )

        # Print node search results
        print('\nNode Search Results---:')
        for node in node_search_results.nodes:
            print(f'Node UUID: {node.uuid}')
            print(f'Node Name: {node.name}')
            node_summary = node.summary[:100] + '...' if len(node.summary) > 100 else node.summary
            print(f'Content Summary: {node_summary}')
            print(f'Node Labels: {", ".join(node.labels)}')
            print(f'Created At: {node.created_at}')
            if hasattr(node, 'attributes') and node.attributes:
                print('Attributes:')
                for key, value in node.attributes.items():
                    print(f'  {key}: {value}')
            print('---')

    finally:
        #################################################
        # CLEANUP
        #################################################
        # Always close the connection to Neo4j when
        # finished to properly release resources
        #################################################

        # Close the connection
        await graphiti.close()
        print('\nConnection closed')


if __name__ == '__main__':
    asyncio.run(main())