from flask import Flask, request, jsonify, session, render_template
from datetime import datetime
import pymysql
import bcrypt
import hashlib
import os

app = Flask(__name__)
app.secret_key = "123456"

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'db': 'chili_wx',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# 连接到数据库
def get_db_connection():
    return pymysql.connect(**db_config)

# 生成防伪码
def generate_anti_counterfeiting_code():
    return hashlib.sha256(str(datetime.now()).encode()).hexdigest()

# 生成登录页面 HTML
def generate_landing_page():
    landing_html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>椒口称赞-防伪溯源管理中心</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .login-container {
                width: 90%;
                max-width: 400px;
                background-color: #fff;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            .form-group {
                margin-bottom: 15px;
                text-align: left;
            }
            .form-group label {
                display: block;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .form-group input {
                width: calc(100% - 20px); /* 减去 padding 的宽度 */
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
                margin: 0 auto; /* 居中 */
            }
            .form-group button {
                width: 100%;
                padding: 10px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
            }
            .form-group button:hover {
                background-color: #0056b3;
            }
            .captcha-group {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .captcha-group input {
                flex: 1;
            }
            .captcha-group button {
                width: auto;
                padding: 10px 15px;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1>椒口称赞-防伪溯源管理中心</h1>
            <form id="loginForm">
                <div class="form-group">
                    <label for="phone">账号:</label>
                    <input type="text" id="phone" name="phone" required>
                </div>
                <div class="form-group">
                    <label for="password">密码:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <div class="form-group captcha-group">
                    <label for="code">验证码:</label>
                    <input type="text" id="code" name="code" required>
                    <button type="button" id="get-code">获取验证码</button>
                </div>
                <div class="form-group">
                    <button type="submit">登录</button>
                </div>
            </form>
        </div>

        <script>
            // 获取验证码按钮点击事件
            document.getElementById('get-code').addEventListener('click', function() {
                alert('验证码已发送（模拟）');
            });

            // 表单提交事件
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (result.status === 'success') {
                    window.location.href = '/upload_page';
                } else {
                    alert(result.message);
                }
            });
        </script>
    </body>
    </html>
    """
    with open("manage_landing.html", "w", encoding="utf-8") as file:
        file.write(landing_html)
    print("登录页面已生成: manage_landing.html")

# 生成上传页面 HTML
def generate_upload_page():
    upload_html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>椒口称赞-防伪溯源管理中心</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }
            .container {
                width: 90%;
                max-width: 400px;
                margin: 20px auto;
                background-color: #fff;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            .form-group label {
                display: block;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .form-group input, .form-group textarea {
                width: calc(100% - 20px); /* 减去 padding 的宽度 */
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
                margin: 0 auto; /* 居中 */
            }
            .form-group textarea {
                resize: vertical;
                height: 100px;
            }
            .form-group button {
                width: 100%;
                padding: 10px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
            }
            .form-group button:hover {
                background-color: #0056b3;
            }
            .image-upload {
                text-align: center;
                margin: 20px 0;
            }
            .image-upload button {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
            }
            .image-upload button:hover {
                background-color: #218838;
            }
            .hidden-image {
                display: none;
                text-align: center;
                margin-top: 20px;
            }
            .hidden-image img {
                max-width: 100%;
                height: auto;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>椒口称赞-防伪溯源管理中心</h1>
            <form id="uploadForm">
                <!-- 所属片区 -->
                <div class="form-group">
                    <label for="region_name">所属片区:</label>
                    <input type="text" id="region_name" name="region_name" required>
                </div>
                <div class="image-upload">
                    <button type="button" onclick="captureImage('region')">拍摄片区图片</button>
                </div>
                <div class="hidden-image" id="regionImage">
                    <img src="" alt="片区图片">
                </div>

                <!-- 使用的肥料 -->
                <div class="form-group">
                    <label for="fertilizers_used">使用的肥料:</label>
                    <input type="text" id="fertilizers_used" name="fertilizers_used" required>
                </div>

                <!-- 农事活动 -->
                <div class="form-group">
                    <label for="farming_activities">农事活动:</label>
                    <input type="text" id="farming_activities" name="farming_activities" required>
                </div>

                <!-- 浇水施肥打药记录 -->
                <div class="form-group">
                    <label for="watering_fertilizing_pesticide_logs">浇水施肥打药记录:</label>
                    <textarea id="watering_fertilizing_pesticide_logs" name="watering_fertilizing_pesticide_logs" required></textarea>
                </div>

                <!-- 收割和晾晒图片 -->
                <div class="image-upload">
                    <button type="button" onclick="captureImage('harvest')">拍摄收割照片</button>
                    <button type="button" onclick="captureImage('drying')">拍摄晾晒照片</button>
                </div>
                <div class="hidden-image" id="harvestImage">
                    <img src="" alt="收割照片">
                </div>
                <div class="hidden-image" id="dryingImage">
                    <img src="" alt="晾晒照片">
                </div>

                <!-- 包装信息 -->
                <div class="form-group">
                    <label for="packaging_time">包装时间:</label>
                    <input type="text" id="packaging_time" name="packaging_time" readonly>
                </div>
                <div class="form-group">
                    <label for="packaging_leader">包装负责人:</label>
                    <input type="text" id="packaging_leader" name="packaging_leader" readonly>
                </div>
                <div class="image-upload">
                    <label style="font-weight: bold; display: block; text-align: center;">包装图片</label>
                    <button type="button" onclick="captureImage('packaging')">点击拍摄包装</button>
                </div>
                <div class="hidden-image" id="packagingImage">
                    <img src="" alt="包装图片">
                </div>

                <!-- 物流信息 -->
                <div class="form-group">
                    <label for="logistics_company">物流公司:</label>
                    <input type="text" id="logistics_company" name="logistics_company">
                </div>
                <div class="image-upload">
                    <label style="font-weight: bold; display: block; text-align: center;">物流单号</label>
                    <button type="button" onclick="captureImage('logistics')">点击拍摄物流单号</button>
                </div>
                <div class="hidden-image" id="logisticsImage">
                    <img src="" alt="物流单号">
                </div>

                <!-- 提交按钮 -->
                <div class="form-group">
                    <button type="submit">上传信息</button>
                </div>
            </form>
        </div>

        <script>
            // 自动填充包装时间和负责人
            document.getElementById('packaging_time').value = new Date().toLocaleString();
            document.getElementById('packaging_leader').value = "{{ session.get('real_name', '未知') }}";

            // 拍摄图片功能
            function captureImage(type) {
                // 这里可以调用摄像头 API 拍摄照片
                alert(`拍摄${type === 'region' ? '片区' : type === 'harvest' ? '收割' : type === 'drying' ? '晾晒' : type === 'packaging' ? '包装' : '物流单号'}照片`);
                const imageElement = document.getElementById(`${type}Image`);
                imageElement.style.display = 'block';
                imageElement.querySelector('img').src = 'https://via.placeholder.com/400x300'; // 示例图片
            }

            // 表单提交
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);

                // 添加图片数据（假设图片已上传到服务器并返回 URL）
                const regionImage = document.getElementById('regionImage').querySelector('img').src;
                const harvestImage = document.getElementById('harvestImage').querySelector('img').src;
                const dryingImage = document.getElementById('dryingImage').querySelector('img').src;
                const packagingImage = document.getElementById('packagingImage').querySelector('img').src;
                const logisticsImage = document.getElementById('logisticsImage').querySelector('img').src;
                formData.append('region_image_url', regionImage);
                formData.append('harvest_image_url', harvestImage);
                formData.append('drying_image_url', dryingImage);
                formData.append('packaging_image_url', packagingImage);
                formData.append('logistics_image_url', logisticsImage);

                // 提交表单数据
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (result.status === 'success') {
                    alert('信息上传成功');
                } else {
                    alert('信息上传失败');
                }
            });
        </script>
    </body>
    </html>
    """
    with open("manage_upload.html", "w", encoding="utf-8") as file:
        file.write(upload_html)
    print("上传页面已生成: manage_upload.html")

# 登录 bcrypt库 密码哈希存储和验证
@app.route('/login', methods=['POST'])
def login():
    phone = request.form['phone']
    password = request.form['password']

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE phone = %s"
            cursor.execute(sql, (phone,))
            user = cursor.fetchone()
            if user and bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
                session['logged_in'] = True
                session['real_name'] = user['real_name']
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'error', 'message': '用户名或密码错误'})
    finally:
        connection.close()

# 上传信息
@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('logged_in'):
        return jsonify({'status': 'error', 'message': '请先登录'})

    # 获取表单数据
    region_name = request.form['region_name']
    region_image_url = request.form.get('region_image_url', '')
    fertilizers_used = request.form['fertilizers_used']
    farming_activities = request.form['farming_activities']
    watering_fertilizing_pesticide_logs = request.form['watering_fertilizing_pesticide_logs']
    harvest_image_url = request.form.get('harvest_image_url', '')
    drying_image_url = request.form.get('drying_image_url', '')
    packaging_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 系统生成包装时间
    packaging_leader = session.get('real_name', '未知')  # 系统检测登录账号人姓名
    packaging_image_url = request.form.get('packaging_image_url', '')
    logistics_company = request.form.get('logistics_company', '')
    tracking_number = request.form.get('tracking_number', '')
    logistics_image_url = request.form.get('logistics_image_url', '')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 检查是否已生成防伪码
            sql = "SELECT anti_counterfeiting_code FROM regions WHERE region_name = %s"
            cursor.execute(sql, (region_name,))
            region = cursor.fetchone()
            if not region or not region['anti_counterfeiting_code']:
                anti_counterfeiting_code = generate_anti_counterfeiting_code()
            else:
                anti_counterfeiting_code = region['anti_counterfeiting_code']

            # 更新或插入数据
            sql = """
            INSERT INTO regions (
                region_name, region_image_url, operator, operation_time, fertilizers_used,
                farming_activities, watering_fertilizing_pesticide_logs, harvest_image_url,
                drying_image_url, packaging_time, packaging_leader, packaging_image_url,
                logistics_company, tracking_number, logistics_image_url, anti_counterfeiting_code
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                region_image_url = VALUES(region_image_url),
                operator = VALUES(operator),
                operation_time = VALUES(operation_time),
                fertilizers_used = VALUES(fertilizers_used),
                farming_activities = VALUES(farming_activities),
                watering_fertilizing_pesticide_logs = VALUES(watering_fertilizing_pesticide_logs),
                harvest_image_url = VALUES(harvest_image_url),
                drying_image_url = VALUES(drying_image_url),
                packaging_time = VALUES(packaging_time),
                packaging_leader = VALUES(packaging_leader),
                packaging_image_url = VALUES(packaging_image_url),
                logistics_company = VALUES(logistics_company),
                tracking_number = VALUES(tracking_number),
                logistics_image_url = VALUES(logistics_image_url)
            """
            cursor.execute(sql, (
                region_name, region_image_url, session.get('real_name'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                fertilizers_used, farming_activities, watering_fertilizing_pesticide_logs,
                harvest_image_url, drying_image_url, packaging_time, packaging_leader,
                packaging_image_url, logistics_company, tracking_number, logistics_image_url,
                anti_counterfeiting_code
            ))
            connection.commit()
            return jsonify({'status': 'success'})
    finally:
        connection.close()

if __name__ == '__main__':
    # 生成登录页面和上传页面
    generate_landing_page()
    generate_upload_page()

    # 启动 Flask 应用
    app.run(debug=True)