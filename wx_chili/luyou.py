from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# 定义路由
@app.route('/region/<int:region_id>')
def region_details(region_id):
    # 根据片区 ID 确定 HTML 文件名
    html_file_name = f"{['first', 'second', 'third', 'fourth', 'fifth', 'sixth'][region_id - 1]}_chili.html"
    # HTML 文件路径
    html_file_path = os.path.join('templates', html_file_name)

    # 检查 HTML 文件是否存在
    if os.path.exists(html_file_path):
        # 返回 HTML 文件
        return send_from_directory('templates', html_file_name)
    else:
        return f"片区 {region_id} 的页面不存在", 404


# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 计算上级根目录路径
parent_dir = os.path.dirname(current_dir)

# 定义 /land 路由
@app.route('/land')
def land_page():
    return send_from_directory(current_dir, 'manage_landing.html')

# 定义 /upload 路由
@app.route('/upload')
def upload_page():
    return send_from_directory(current_dir, 'manage_upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
