from langchain_core.tools import tool
from pydantic import BaseModel, Field  # 用于工具参数严格校验
from rag.rag_service import RagSummarizeService
from .Weather.weather import get2_weather
from .Location.location import get2_location
import json
from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger
import os
from datetime import date




# =========================================================================================================================

rag = RagSummarizeService()

@tool(description='从向量存储中检索参考资料,输入检索内容(str),输出参考资料')
def rag_summarize(query:str)->str:
  return rag.rag_summarize(query)

# =========================================================================================================================

class cityNameInput(BaseModel):
   city:str = Field(description='需要查询天气的城市名字')
@tool(description='查询天气,输入城市名字,返回实时天气状况',args_schema=cityNameInput)
def get_weather(city:str) -> str:
   return get2_weather(city)

# =========================================================================================================================


@tool(description='通过 IP 获取当前设备的地理位置（精确到城市）,无输入参数,输出为json字符串格式')
def get_location():
  res_json = json.dumps( get2_location(),ensure_ascii=False )
  return str(res_json)

# =========================================================================================================================


@tool(description='获取用户ID,以字符串格式返回,无输入参数 ')
def get_user_id() -> str:
   return agent_conf['user_id']

# =========================================================================================================================

@tool(description='获取当前日期(年-月-日),以字符串形式返回,无输入参数 ')
def get_current_date() -> str:
  return date.today()

# =========================================================================================================================
external_data = {}

def generate_external_data():
  """
  {
    "user_id1":{
      "month1" : {"特征":xxx,"效率":xxx,...}   
      "month2" : {"特征":xxx,"效率":xxx,...}   
      "month3" : {"特征":xxx,"效率":xxx,...}   
      ...
    },
    "user_id2":{
      "month1" : {"特征":xxx,"效率":xxx,...}   
      "month2" : {"特征":xxx,"效率":xxx,...}   
      "month3" : {"特征":xxx,"效率":xxx,...}   
      ...
    },    
    "user_id3":{
      "month1" : {"特征":xxx,"效率":xxx,...}   
      "month2" : {"特征":xxx,"效率":xxx,...}   
      "month3" : {"特征":xxx,"效率":xxx,...}   
      ...
    },
    ...
  }
  """
  if not external_data:
    external_data_path = get_abs_path(agent_conf['external_data_path'])
    if not os.path.exists(external_data_path):
      raise FileNotFoundError(f'{external_data_path}文件不存在!')
    with open (external_data_path,'r',encoding='utf-8') as file:
      for line in file.readlines()[1:]:
        arr:list[str] = line.strip().split(',')
        user_id:str = arr[0].replace('"','')
        feather:str = arr[1].replace('"','')
        efficiency:str = arr[2].replace('"','')
        consumables:str = arr[3].replace('"','')
        comparison:str = arr[4].replace('"','')
        time:str = arr[5].replace('"','')
        if user_id not in external_data:
          external_data[user_id] = {}
        external_data[user_id][time]={
          "特征":feather,
          "效率":efficiency,
          "耗材":consumables,
          "对比":comparison
        }

class fetch_external_data_Input(BaseModel):
   user_id:str = Field(description='用户ID')
   month:str = Field(description='年月 严格遵循"YYYY-MM"格式，如"2025-03"')

@tool(
      description='从外部系统中检索指定用户在指定月份(年月)的扫地/扫拖机器人完整使用记录,以字符串形式返回,若未检索到则返回空字符串'
      ,args_schema=fetch_external_data_Input
    )
def fetch_external_data(user_id:str , month:str):
  generate_external_data()
  try:
    return external_data[user_id][month]
  except KeyError:
    logger.warning(f'[fetch_external_data]未检索到{user_id}在{month}的使用记录')
    return ''
  pass

# =========================================================================================================================

@tool(description='无入参无返回值,调用后触发中间件自动为报告生成的场景动态注入上下文信息,为后续切换提示词提通上下文信息')
def fill_context_for_report():
  logger.info(f'[fill_context_for_report]已调用')
  return '[fill_context_for_report]已调用'

# =========================================================================================================================

