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
neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:17687')
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

    namespace="gz_news"

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



        d=True
        d=False
        if d:
            await clear_data(graphiti.driver)

            await graphiti.build_indices_and_constraints()             
            episodes = [
                {
                    'name':'gz_news',
                    'content': """
                    5月16日，省委书记黄坤明走访部分中央驻粤单位，就强化央地协同推动高质量发展进行调研，强调要深入学习贯彻习近平总书记对广东系列重要讲话和重要指示精神，紧扣落实总书记、党中央决策部署，持续深化央地全方位合作，合力推动中国式现代化的广东实践行稳致远，更好担起经济大省挑大梁的责任。

　　黄坤明首先来到省烟草专卖局（省烟草公司），听取我省烟草专卖和广东中烟生产经营情况汇报，希望全省烟草系统立足全国及全省工作大局，密切跟踪形势变化，在强化治理、打造品牌上下功夫，保持卷烟打假打私高压态势，营造干净有序的市场环境，积极履行社会责任，以更大力度参与“百县千镇万村高质量发展工程”实施，努力为广东经济社会发展作出新贡献。

　　随后，黄坤明来到国家税务总局广东省税务局，听取全省税收工作情况介绍。他希望省税务局和深圳市税务局坚持依法科学组织税费收入，扎实稳妥做好征管工作，积极涵养税源，全面落实减税降费政策，提供暖心高效的办税服务，强化银税互动和征信支持，助力各类经营主体纾困解难、稳健经营，更好服务经济高质量发展。

　　在全国海关信息中心广东分中心和海关总署广东分署，黄坤明通过视频系统察看口岸通关实况，听取我省外贸结构趋势和发展态势分析。他指出，广东是外贸大省，进出口贸易对稳住全省经济大盘至关重要。希望海关总署广东分署扎实做好监管、缉私、检验检疫等工作，进一步提升口岸通关效率，强化数据研究运用，以更有力举措、更优质服务支持外贸企业降成本稳订单拓市场，下力气培育做大综保区等各类开放新平台，助力广东推进高水平对外开放，更好服务和融入新发展格局。

　　黄坤明还来到国家金融监督管理总局广东监管局调研，并与国家金融监督管理总局广东监管局、中国人民银行广东省分行、中国证监会广东监管局等单位主要负责同志座谈交流。他希望中央驻粤金融管理部门进一步加大指导支持力度，着眼助力广东经济持续回升向好，组织动员各类金融机构加大对生产企业特别是外贸企业以及重大项目、重大工程的融资支持力度，积极发展消费金融，帮助广东更好稳外贸、扩投资、促消费。着眼培育壮大新质生产力，加大对科技企业信贷和直接融资支持，加快促进“科技—产业—金融”良性循环。着眼推进高水平金融开放，推动落实好中央各项金融开放政策，支持广东加强与港澳的金融合作，共同做强金融产品、拓宽金融通道、做大金融市场，营造开放安全的跨境金融环境。着眼有效防范化解金融风险，央地协同提高监管效能，坚决守住不发生系统性金融风险的底线。

　　在走访调研中，黄坤明看望慰问有关驻粤单位干部职工，广泛听取意见建议，并代表省委省政府向中央有关部委及驻粤单位长期以来对广东工作的指导支持表示感谢。他说，今年是“十四五”规划收官之年、“十五五”规划谋篇布局之年，做好今年工作意义重大、责任重大，推动广东发展离不开中央驻粤各单位的关心支持。希望大家紧紧围绕服务保障党和国家中心工作认真履职尽责，更加主动参与广东高质量发展、现代化建设进程，聚焦粤港澳大湾区建设、现代化产业体系建设、“百县千镇万村高质量发展工程”实施等重点工作，加强监管指导，多提宝贵意见，共同争取更多支持政策，帮助我们把各项工作做得更加扎实有力，更好服务国家发展大局。要加强党的全面领导和党的建设，认真开展深入贯彻中央八项规定精神学习教育，持之以恒抓好自身建设，锻造忠诚干净担当的干部队伍。省委省政府将一如既往全力支持中央驻粤单位在粤发展，进一步加强联络对接，做好服务保障，为中央驻粤单位开展工作创造良好条件，推动央地共赢发展取得更大成效。
                    """,
                    'type': EpisodeType.message,
                    'description': '客服和顾客日常沟通',
                }
            ]


            # await graphiti.build_communities()
            extract_instruction=f"""
                1、抽取人物去了那些地方
                2、抽取人物做了哪些事
            
                """
            for news in episodes:

                await graphiti.add_episode(
                    name=f"news_{news['name']}",
                    episode_body=news['content'],
                    source=EpisodeType.text,
                    source_description="新闻",
                    group_id=namespace,
                    # update_communities=True,
                    reference_time=datetime.now(),
                    # entity_types={"Table":Table,"Column":Column},
                    # extract_node_instruction=extract_instruction,
                    # extract_edge_instruction=extract_instruction

                )
                        

        q="黄坤明去过什么地方"
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