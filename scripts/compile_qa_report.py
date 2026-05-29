import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

REPORT_DIR = 'reports'
ASSETS_DIR = 'reports/assets'
OUTPUT_HTML = os.path.join(REPORT_DIR, 'qa_report.html')
OUTPUT_MD = os.path.join(REPORT_DIR, 'qa_report.md')
XAI_JSON = os.path.join(ASSETS_DIR, 'xai_data.json')
TEMPLATE_DIR = 'scripts/templates'

def compile_report():
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    # Load XAI chart data
    chart_data = {'labels': [], 'data': []}
    if os.path.exists(XAI_JSON):
        with open(XAI_JSON, 'r', encoding='utf-8') as f:
            chart_data = json.load(f)
            
    # Render HTML using Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('qa_report.html')
    
    html_out = template.render(
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        chart_data=json.dumps(chart_data)
    )
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_out)
        
    print(f"QA report (HTML) compiled successfully at {OUTPUT_HTML}")
    
if __name__ == '__main__':
    compile_report()
