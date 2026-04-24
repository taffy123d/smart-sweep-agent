from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from .tools.agent_tools import (
  rag_summarize,get_weather,get_location,get_current_date,get_user_id,generate_external_data,fill_context_for_report
)
from .tools.middleware import  (
 monitor_tool,log_before_model,report_prompt_switch 
)



tools = [rag_summarize,get_weather,get_location,get_current_date,get_user_id,generate_external_data,fill_context_for_report]
middleware = [monitor_tool,log_before_model,report_prompt_switch]

class ReactAgent:
  def __init__(self):
    self.agent = create_agent(
      model=chat_model,
      system_prompt=load_system_prompts(),
      tools=tools,
      middleware=middleware
    )
  def execute_stream(self,query:str):
    input_dict = {
      'messages' : [
        {'role':'user','content':query}
      ]
    }
    for chunk in self.agent.stream(input_dict,stream_mode='values',context={'report':False}): #contexnt即为提示词切换标记
      latest_message = chunk['messages'][-1]
      if latest_message.content:
        yield latest_message.content.strip()+'\n'    

  def execute_invoke(self,query:str) ->str :
    input_dict = {
      'messages' : [
        {'role':'user','content':query}
      ]
    }
    res = self.agent.invoke(input_dict)
    return res["output"]

if __name__ == '__main__':
  agent = ReactAgent()
  for chunk in agent.execute_stream('扫地机器人在当前地区的气温下如何保养？'):
    print(chunk,end='',flush=True)
