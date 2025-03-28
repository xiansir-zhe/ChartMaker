from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain.llms.base import LLM
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json
import os
import requests
import pandas as pd
import csv
import io
from typing import Any, List, Mapping, Optional, Dict, Union

class DeepSeekLLM(LLM):
    api_key: str
    model: str = "deepseek-chat"
    temperature: float = 0.7
    
    @property
    def _llm_type(self) -> str:
        return "deepseek"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature
        }
        
        if stop:
            data["stop"] = stop
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",  # 请确认DeepSeek的API端点
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise ValueError(f"Error from DeepSeek API: {response.text}")
        
        return response.json()["choices"][0]["message"]["content"]

app = FastAPI()

# 添加CORS中间件，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求体的数据模型
class ChartRequest(BaseModel):
    description: str
    data: list

class DataAnalysisRequest(BaseModel):
    data: list

# 初始化DeepSeek LLM
# 注意：需要设置DEEPSEEK_API_KEY环境变量
llm = DeepSeekLLM(
    model="deepseek-chat",  # 或其他DeepSeek模型
    temperature=0.7,
    api_key=os.environ.get("DEEPSEEK_API_KEY")
)

# 创建提示模板
chart_prompt_template = PromptTemplate(
    input_variables=["description", "data"],
    template="""
    根据以下描述和数据，生成一个ECharts配置：
    
    描述: {description}
    
    数据: {data}
    
    请生成一个完整的、有效的ECharts配置JSON。只返回JSON格式的配置，不要包含任何解释或其他文本。
    确保配置包含适当的标题、图例、坐标轴标签和数据系列。
    """
)

# 数据分析提示模板
analysis_prompt_template = PromptTemplate(
    input_variables=["data"],
    template="""
    分析以下数据并提供见解：
    
    数据: {data}
    
    请提供以下信息：
    1. 数据的基本统计信息（如有数值型数据）
    2. 数据中的主要趋势或模式
    3. 推荐的可视化图表类型及理由
    4. 其他任何有价值的观察
    
    请以JSON格式返回结果，包含以下字段：statistics, trends, recommended_charts, observations
    """
)

# 创建LLM链
chart_chain = LLMChain(llm=llm, prompt=chart_prompt_template)
analysis_chain = LLMChain(llm=llm, prompt=analysis_prompt_template)

@app.post("/generate-chart-config")
async def generate_chart_config(request: ChartRequest):
    try:
        # 将数据转换为字符串
        data_str = json.dumps(request.data)
        
        # 使用LLM链处理请求
        result = chart_chain.run(description=request.description, data=data_str)
        
        # 尝试解析结果为JSON
        try:
            # 尝试从结果中提取JSON部分
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result[json_start:json_end]
                echarts_config = json.loads(json_str)
            else:
                echarts_config = {"raw_text": result}
        except json.JSONDecodeError:
            # 如果结果不是有效的JSON，返回原始文本
            echarts_config = {"raw_text": result}
        
        return {"config": echarts_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-data")
async def analyze_data(request: DataAnalysisRequest):
    try:
        # 将数据转换为字符串
        data_str = json.dumps(request.data)
        
        # 使用LLM链处理请求
        result = analysis_chain.run(data=data_str)
        
        # 尝试解析结果为JSON
        try:
            # 尝试从结果中提取JSON部分
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result[json_start:json_end]
                analysis_result = json.loads(json_str)
            else:
                analysis_result = {"raw_text": result}
        except json.JSONDecodeError:
            # 如果结果不是有效的JSON，返回原始文本
            analysis_result = {"raw_text": result}
        
        return {"analysis": analysis_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        if file.filename.endswith('.json'):
            # 解析JSON文件
            data = json.loads(contents.decode('utf-8'))
        elif file.filename.endswith('.csv'):
            # 解析CSV文件
            csv_data = contents.decode('utf-8').splitlines()
            reader = csv.DictReader(csv_data)
            data = [row for row in reader]
            
            # 尝试将数值转换为数字
            for row in data:
                for key, value in row.items():
                    try:
                        row[key] = float(value) if '.' in value else int(value)
                    except (ValueError, TypeError):
                        pass
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式。请上传JSON或CSV文件。")
        
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chart-templates")
async def get_chart_templates():
    # 返回一些常用的图表模板
    templates = [
        {
            "name": "折线图",
            "description": "显示数据随时间变化的趋势",
            "example_config": {
                "title": {"text": "销售趋势"},
                "xAxis": {"type": "category", "data": ["一月", "二月", "三月", "四月", "五月", "六月"]},
                "yAxis": {"type": "value"},
                "series": [{"data": [150, 230, 224, 218, 135, 147], "type": "line"}]
            }
        },
        {
            "name": "柱状图",
            "description": "比较不同类别的数据",
            "example_config": {
                "title": {"text": "销售比较"},
                "xAxis": {"type": "category", "data": ["产品A", "产品B", "产品C", "产品D", "产品E"]},
                "yAxis": {"type": "value"},
                "series": [{"data": [5, 20, 36, 10, 10], "type": "bar"}]
            }
        },
        {
            "name": "饼图",
            "description": "显示部分与整体的关系",
            "example_config": {
                "title": {"text": "销售占比"},
                "series": [{
                    "type": "pie",
                    "data": [
                        {"value": 1048, "name": "产品A"},
                        {"value": 735, "name": "产品B"},
                        {"value": 580, "name": "产品C"},
                        {"value": 484, "name": "产品D"},
                        {"value": 300, "name": "产品E"}
                    ]
                }]
            }
        }
    ]
    
    return {"templates": templates}

# 添加一个简单的健康检查端点
@app.get("/")
async def read_root():
    return {"status": "ok"}
