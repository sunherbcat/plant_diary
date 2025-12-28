#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植物日記 - Web 版本
基於 Flask 的 Web 應用程式，支持手機瀏覽器訪問
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
from werkzeug.utils import secure_filename
from functools import wraps
import json

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from plant_diary.database import get_db
    from plant_diary.ai_analyzer import get_analyzer
    from plant_diary.ocr_reader import get_ocr_reader
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent / "plant_diary"))
    from database import get_db
    from ai_analyzer import get_analyzer
    from ocr_reader import get_ocr_reader

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'plant-diary-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = Path('plant_photos').absolute()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 確保上傳目錄存在
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# 允許的文件擴展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# 初始化數據庫和工具
db = get_db()
analyzer = get_analyzer()
ocr_reader = get_ocr_reader()


def allowed_file(filename):
    """檢查文件擴展名是否允許"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    """登入檢查裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': '請先登入'}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """主頁"""
    # 如果未登入，重定向到登入頁面
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    plants = db.get_all_plants()
    user = db.get_user(session['user_id'])
    return render_template('index.html', plants=plants, user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登入頁面"""
    if request.method == 'GET':
        # 如果已登入，重定向到主頁
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('login.html')
    
    # POST 請求：處理登入
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'error': '請輸入用戶名和密碼'}), 400
    
    user = db.verify_user(username, password)
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['is_admin'] = user['is_admin']
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'is_admin': user['is_admin']
            }
        })
    else:
        return jsonify({'success': False, 'error': '用戶名或密碼錯誤'}), 401


@app.route('/register', methods=['GET', 'POST'])
def register():
    """註冊頁面"""
    if request.method == 'GET':
        # 如果已登入，重定向到主頁
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('register.html')
    
    # POST 請求：處理註冊
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'error': '請輸入用戶名和密碼'}), 400
    
    if len(username) < 3:
        return jsonify({'success': False, 'error': '用戶名至少需要3個字符'}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'error': '密碼至少需要6個字符'}), 400
    
    if password != confirm_password:
        return jsonify({'success': False, 'error': '兩次輸入的密碼不一致'}), 400
    
    user_id, error = db.create_user(username, password)
    if user_id:
        # 註冊成功，自動登入
        user = db.get_user(user_id)
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['is_admin'] = user['is_admin']
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'is_admin': user['is_admin']
            }
        })
    else:
        return jsonify({'success': False, 'error': error or '註冊失敗'}), 400


@app.route('/logout', methods=['POST'])
def logout():
    """登出"""
    session.clear()
    return jsonify({'success': True})


@app.route('/api/user/current', methods=['GET'])
def get_current_user():
    """獲取當前登入用戶信息"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '未登入'}), 401
    
    user = db.get_user(session['user_id'])
    if user:
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'is_admin': user['is_admin']
            }
        })
    return jsonify({'success': False, 'error': '用戶不存在'}), 404


@app.route('/api/plants', methods=['GET'])
@login_required
def get_plants():
    """獲取所有植物列表"""
    plants = db.get_all_plants()
    return jsonify([dict(plant) for plant in plants])


@app.route('/api/plants', methods=['POST'])
@login_required
def add_plant():
    """添加新植物"""
    data = request.get_json()
    chinese_name = data.get('chinese_name', '').strip()
    scientific_name = data.get('scientific_name', '').strip()
    notes = data.get('notes', '').strip()
    
    if not chinese_name:
        return jsonify({'success': False, 'error': '中文名稱不能為空'}), 400
    
    try:
        plant_id = db.add_plant(chinese_name, scientific_name, notes)
        return jsonify({'success': True, 'plant_id': plant_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/plants/<int:plant_id>', methods=['GET'])
@login_required
def get_plant(plant_id):
    """獲取單個植物信息"""
    plant = db.get_plant(plant_id)
    if plant:
        photos = db.get_plant_photos(plant_id)
        return jsonify({
            'success': True,
            'plant': dict(plant),
            'photos': [dict(photo) for photo in photos]
        })
    return jsonify({'success': False, 'error': '植物不存在'}), 404


@app.route('/api/plants/<int:plant_id>', methods=['PUT'])
@login_required
def update_plant(plant_id):
    """更新植物信息"""
    data = request.get_json()
    try:
        db.update_plant(
            plant_id,
            chinese_name=data.get('chinese_name'),
            scientific_name=data.get('scientific_name'),
            notes=data.get('notes')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/plants/<int:plant_id>', methods=['DELETE'])
@login_required
def delete_plant(plant_id):
    """刪除植物"""
    try:
        db.delete_plant(plant_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/plants/<int:plant_id>/photos', methods=['POST'])
@login_required
def upload_photo(plant_id):
    """上傳照片"""
    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': '沒有選擇文件'}), 400
    
    file = request.files['photo']
    notes = request.form.get('notes', '').strip()
    
    if file.filename == '':
        return jsonify({'success': False, 'error': '沒有選擇文件'}), 400
    
    if file and allowed_file(file.filename):
        # 生成安全的文件名
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plant = db.get_plant(plant_id)
        if not plant:
            return jsonify({'success': False, 'error': '植物不存在'}), 404
        
        filename = secure_filename(f"{plant['chinese_name']}_{timestamp}_{file.filename}")
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(str(filepath))
        
        # 保存到數據庫（不進行自動AI分析）
        photo_id = db.add_photo(
            plant_id=plant_id,
            photo_path=str(filepath),
            notes=notes
        )
        
        return jsonify({
            'success': True,
            'photo_id': photo_id,
            'filename': filename
        })
    
    return jsonify({'success': False, 'error': '不支持的文件格式，請使用 JPG、PNG、WebP 等圖片格式'}), 400


@app.route('/api/ocr/recognize', methods=['POST'])
@login_required
def recognize_photo():
    """OCR 識別照片"""
    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': '沒有選擇文件'}), 400
    
    file = request.files['photo']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': '沒有選擇文件'}), 400
    
    if not file:
        return jsonify({'success': False, 'error': '文件讀取失敗'}), 400
    
    # 驗證文件格式
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': '不支持的文件格式，請使用 JPG、PNG、WebP 等圖片格式'}), 400
    
    temp_filepath = None
    try:
        # 保存臨時文件
        from datetime import datetime
        import tempfile
        
        # 確保文件擴展名正確
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
        if file_ext not in ALLOWED_EXTENSIONS:
            file_ext = 'jpg'
        
        temp_filename = secure_filename(f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}")
        temp_filepath = app.config['UPLOAD_FOLDER'] / temp_filename
        
        # 保存文件
        file.save(str(temp_filepath))
        
        # 驗證文件是否成功保存
        if not temp_filepath.exists() or temp_filepath.stat().st_size == 0:
            return jsonify({
                'success': False,
                'error': '文件保存失敗，請重試'
            }), 500
        
        # 使用 PIL 驗證圖片
        try:
            from PIL import Image
            with Image.open(str(temp_filepath)) as img:
                img.verify()
            # 重新打開並轉換為標準格式
            img = Image.open(str(temp_filepath))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # 保存為標準 JPEG 格式
            temp_filepath_jpg = temp_filepath.with_suffix('.jpg')
            img.save(str(temp_filepath_jpg), 'JPEG', quality=95)
            if temp_filepath != temp_filepath_jpg:
                temp_filepath.unlink()
                temp_filepath = temp_filepath_jpg
        except Exception as img_error:
            return jsonify({
                'success': False,
                'error': f'圖片文件損壞或格式不支持: {str(img_error)}'
            }), 400
        
        # 進行 OCR 識別
        api_key = os.getenv('OPENAI_API_KEY')
        use_openai = api_key is not None
        
        result = ocr_reader.recognize_text(
            str(temp_filepath),
            use_openai=use_openai,
            openai_api_key=api_key
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'OCR 識別錯誤: {str(e)}'
        }), 500
    finally:
        # 刪除臨時文件
        if temp_filepath and temp_filepath.exists():
            try:
                temp_filepath.unlink()
            except Exception:
                pass


@app.route('/api/photos/<int:photo_id>', methods=['GET'])
@login_required
def get_photo_details(photo_id):
    """獲取照片詳情"""
    photo = db.get_photo(photo_id)
    if photo:
        return jsonify({
            'success': True,
            'photo': dict(photo)
        })
    return jsonify({'success': False, 'error': '照片不存在'}), 404


@app.route('/api/photos/analyze', methods=['POST'])
@login_required
def analyze_photos():
    """批量分析照片"""
    data = request.get_json()
    photo_ids = data.get('photo_ids', [])
    
    if not photo_ids:
        return jsonify({'success': False, 'error': '請選擇至少一張照片'}), 400
    
    if not isinstance(photo_ids, list):
        return jsonify({'success': False, 'error': '照片ID必須是列表'}), 400
    
    # 異步進行 AI 分析（在後台執行，不阻塞響應）
    import threading
    def analyze_photos_batch():
        try:
            for photo_id in photo_ids:
                try:
                    # 獲取照片信息
                    photo = db.get_photo(photo_id)
                    if not photo:
                        print(f"照片不存在 (ID: {photo_id})")
                        continue
                    
                    # 獲取植物信息以傳遞給 AI
                    plant_id = photo['plant_id']
                    plant = db.get_plant(plant_id)
                    chinese_name = plant.get('chinese_name') if plant else None
                    scientific_name = plant.get('scientific_name') if plant else None
                    
                    # 進行 AI 分析
                    result = analyzer.analyze_plant_photo(
                        photo['photo_path'],
                        chinese_name=chinese_name,
                        scientific_name=scientific_name
                    )
                    
                    # 更新數據庫
                    db.update_photo_analysis(
                        photo_id=photo_id,
                        ai_analysis=result.get('ai_analysis', ''),
                        care_suggestions=result.get('care_suggestions', '')
                    )
                    print(f"AI 分析完成 (照片 ID: {photo_id}, 植物: {chinese_name})")
                except Exception as e:
                    print(f"AI 分析出錯 (照片 ID: {photo_id}): {e}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            print(f"批量分析出錯: {e}")
            import traceback
            traceback.print_exc()
    
    # 在後台線程中執行 AI 分析
    thread = threading.Thread(target=analyze_photos_batch)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f'已開始分析 {len(photo_ids)} 張照片'
    })


@app.route('/api/photos/<int:photo_id>', methods=['DELETE'])
@login_required
def delete_photo(photo_id):
    """刪除照片"""
    try:
        # 先獲取照片信息，以便刪除文件
        photo = db.get_photo(photo_id)
        if not photo:
            return jsonify({'success': False, 'error': '照片不存在'}), 404
        
        # 刪除文件
        photo_path = Path(photo['photo_path'])
        if photo_path.exists():
            try:
                photo_path.unlink()
            except Exception as e:
                print(f"刪除照片文件失敗: {e}")
                # 即使文件刪除失敗，也繼續刪除數據庫記錄
        
        # 刪除數據庫記錄
        if db.delete_photo(photo_id):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '刪除失敗'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上傳的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/logo/<filename>')
def logo_file(filename):
    """提供LOGO文件"""
    logo_folder = Path(__file__).parent.parent / 'LOGO'
    if logo_folder.exists() and (logo_folder / filename).exists():
        return send_from_directory(str(logo_folder), filename)
    return '', 404


if __name__ == '__main__':
    # 本地開發模式
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

