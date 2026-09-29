import pymysql
from datetime import datetime
import qrcode
import os
import hashlib
import time

# 数据库连接参数
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'db': 'chili_wx',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# 生成防伪码（哈希值）
def generate_anti_counterfeiting_code(data):
    data_str = str(data)
    hash_object = hashlib.sha256(data_str.encode())
    return hash_object.hexdigest()

# 生成区块哈希
def calculate_block_hash(index, previous_hash, timestamp, data):
    block_string = f"{index}{previous_hash}{timestamp}{data}"
    return hashlib.sha256(block_string.encode()).hexdigest()

# 创建新区块
def create_new_block(previous_block, data):
    index = previous_block['block_index'] + 1  # 使用 block_index
    timestamp = time.time()
    hash = calculate_block_hash(index, previous_block['hash'], timestamp, data)
    return {
        'block_index': index,  # 使用 block_index
        'previous_hash': previous_block['hash'],
        'timestamp': timestamp,
        'data': data,
        'hash': hash,
    }

# 插入区块到数据库
def insert_block_to_db(block):
    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO blockchain (block_index, previous_hash, timestamp, data, hash)
            VALUES (%s, %s, %s, %s, %s)
            """  # 使用 block_index
            cursor.execute(sql, (block['block_index'], block['previous_hash'], block['timestamp'], block['data'], block['hash']))
        connection.commit()
    except Exception as e:
        print(f"插入区块失败: {e}")

# 查询最新区块
def get_latest_block():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM blockchain ORDER BY block_index DESC LIMIT 1"  # 使用 block_index
            cursor.execute(sql)
            return cursor.fetchone()
    except Exception as e:
        print(f"查询最新区块失败: {e}")
        return None

# 连接到数据库
connection = pymysql.connect(**db_config)

try:
    with connection.cursor() as cursor:
        # 查询片区 6 的数据
        sql = "SELECT * FROM chili_6pq LIMIT 1"
        cursor.execute(sql)
        record = cursor.fetchone()

        # 提取记录中的关键信息
        region_name = record['region_name'] if record else '第六片区'
        region_image_url = record['region_image_url'] if record else ''
        operator = record['operator'] if record else '刘十三'
        operation_time = record['operation_time'] if record else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        region_leader = record['region_leader'] if record else '高十四'
        fertilizers_used = record['fertilizers_used'] if record else '尿素,钙镁磷肥'
        farming_activities = record['farming_activities'] if record else '修剪枝叶'
        watering_fertilizing_pesticide_logs = record['watering_fertilizing_pesticide_logs'] if record else '2023-04-15 09:00 刘十三修剪; 2023-04-30 15:00 高十四清理落叶'
        harvest_time = record.get('harvest_time', '未知')
        drying_time = record.get('drying_time', '未知')

        # 获取最新区块
        latest_block = get_latest_block()
        if not latest_block:
            # 如果区块链为空，创建创世区块
            latest_block = {
                'block_index': 0,  # 使用 block_index
                'previous_hash': '0',
                'timestamp': time.time(),
                'data': 'Genesis Block',
                'hash': calculate_block_hash(0, '0', time.time(), 'Genesis Block'),
            }
            insert_block_to_db(latest_block)

        # 准备新区块数据
        new_block_data = {
            'region_name': region_name,
            'operator': operator,
            'operation_time': operation_time,
            'fertilizers_used': fertilizers_used,
            'farming_activities': farming_activities,
            'watering_fertilizing_pesticide_logs': watering_fertilizing_pesticide_logs,
            'harvest_time': harvest_time,
            'drying_time': drying_time,
        }

        # 检查数据是否有变化
        if str(new_block_data) != latest_block['data']:
            # 创建新区块
            new_block = create_new_block(latest_block, str(new_block_data))
            insert_block_to_db(new_block)
            latest_block = new_block
            print("新区块已创建并插入数据库。")
        else:
            print("数据未发生变化，跳过创建新区块。")

        # 生成防伪码（取区块哈希的前10位）
        anti_counterfeiting_code = latest_block['hash'][:10]

        # 生成HTML内容
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>椒口称赞-防伪溯源查询中心</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    width: 90%;
                    max-width: 400px; /* 调整为适合手机屏幕的宽度 */
                    margin: 50px auto;
                    background-color: #fff;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    word-wrap: break-word; /* 确保所有文本自动换行 */
                    overflow-wrap: break-word; /* 确保所有文本自动换行 */
                }}
                h1 {{
                    text-align: center;
                    color: #333;
                }}
                .section-title {{
                    font-size: 18px;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0;
                }}
                .info-section {{
                    margin-bottom: 20px;
                }}
                .info-section label, .info-section span {{
                    display: block;
                    word-wrap: break-word; /* 自动换行 */
                    overflow-wrap: break-word; /* 自动换行 */
                }}
                .info-section label {{
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .highlight {{
                    font-size: 20px;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 20px;
                    padding: 10px;
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                    word-wrap: break-word; /* 自动换行 */
                    overflow-wrap: break-word; /* 自动换行 */
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                .image-button {{
                    display: block;
                    text-align: right;
                    margin-top: -20px; /* 调整按钮位置 */
                }}
                .image-button button {{
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    cursor: pointer;
                }}
                .hidden-image {{
                    display: none;
                    text-align: center;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- 突出显示防伪码 -->
                <div class="highlight">防伪码: {anti_counterfeiting_code}</div>
                <h1>椒口称赞-防伪溯源查询中心</h1>
                <div class="info-section">
                    <img src="https://pic.vjshi.com/2023-05-26/cdbd0139cf4b4cbe87c6f89d46741446/online/main.jpg?x-oss-process=style/w342_h192_center" alt="辣椒图片" style="width:100%;">
                </div>
                <div class="info-section">
                    <label>所属片区:</label>
                    <span>{region_name} </span>
                    <div class="image-button">
                        <button onclick="toggleImage('regionImage')">点击查看片区图片</button>
                    </div>
                    <div class="hidden-image" id="regionImage">
                        <img src="{region_image_url}" alt="{region_name} 图片">
                    </div>
                </div>
                <div class="info-section">
                    <label>负责人:</label>
                    <span>{operator}</span>
                </div>
                <div class="info-section">
                    <label>操作时间:</label>
                    <span>{operation_time}</span>
                </div>
                <div class="info-section">
                    <label>区域负责人:</label>
                    <span>{region_leader}</span>
                </div>

                <!-- 种植信息板块 -->
                <div class="section-title">种植信息</div>
                <div class="info-section">
                    <label>使用的肥料:</label>
                    <span>{fertilizers_used}</span>
                </div>
                <div class="info-section">
                    <label>农事活动:</label>
                    <span>{farming_activities}</span>
                </div>
                <div class="info-section">
                    <label>浇水施肥打药记录:</label>
                    <div>
                    {(', ').join([f'<span>{log}</span>' for log in watering_fertilizing_pesticide_logs.split('; ')])}
                    </div>
                </div>
                <div class="info-section">
                    <label>收割时间:</label>
                    <span>{harvest_time}</span>
                </div>
                <div class="info-section">
                    <label>晾晒时间:</label>
                    <span>{drying_time}</span>
                </div>

                <!-- 包装信息板块 -->
                <div class="section-title">包装信息</div>
                <div class="info-section">
                    <label>包装时间:</label>
                    <span>暂无数据</span>
                </div>
                <div class="info-section">
                    <label>包装负责人:</label>
                    <span>暂无数据</span>
                </div>
                <div class="info-section">
                    <label>包装图片:</label>
                    <div class="image-button">
                        <button onclick="toggleImage('packagingImage')">点击查看包装图片</button>
                    </div>
                    <div class="hidden-image" id="packagingImage">
                        <img src="https://img95.699pic.com/photo/60031/9724.jpg_wh860.jpg" alt="包装图片">
                    </div>
                </div>

                <!-- 物流信息板块 -->
                <div class="section-title">物流信息</div>
                <div class="info-section">
                    <label>物流公司:</label>
                    <span>暂无数据</span>
                </div>
                <div class="info-section">
                    <label>物流单号:</label>
                    <span>暂无数据</span>
                </div>
                <div class="info-section">
                    <label>打包图片:</label>
                    <div class="image-button">
                        <button onclick="toggleImage('logisticsImage')">点击查看打包图片</button>
                    </div>
                    <div class="hidden-image" id="logisticsImage">
                        <img src="https://img95.699pic.com/photo/30789/7478.jpg_wh300.jpg" alt="打包图片">
                    </div>
                </div>

                <!-- 区块链信息 -->
                <div class="info-section">
                    <label>区块链信息:</label>
                    <div>
                        <p>区块高度: {latest_block['block_index']}</p>
                        <p>区块哈希: {latest_block['hash']}</p>
                        <p>前一区块哈希: {latest_block['previous_hash']}</p>
                    </div>
                </div>
            </div>

            <script>
                // 切换图片显示
                function toggleImage(imageId) {{
                    var img = document.getElementById(imageId);
                    if (img.style.display === 'none' || img.style.display === '') {{
                        img.style.display = 'block';
                    }} else {{
                        img.style.display = 'none';
                    }}
                }}
            </script>
        </body>
        </html>
        """

        # 生成HTML文件名
        html_file_name = "../templates/sixth_chili.html"
        html_file_path = os.path.join(os.getcwd(), html_file_name)

        # 将HTML内容保存到文件中
        with open(html_file_path, "w", encoding="utf-8") as file:
            file.write(html_content)

        print(f"HTML 文件已生成: {html_file_path}")

        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"http://120.46.15.113/region/6")  # 修改为片区6的URL
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_file_name = "sixth_chili_qr.png"
        qr_file_path = os.path.join(os.getcwd(), qr_file_name)
        qr_img.save(qr_file_path)
        print(f"二维码已生成: {qr_file_path}")

finally:
    connection.close()