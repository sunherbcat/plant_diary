#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植物日記 - 主應用程式
植物管理和成長記錄應用
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import shutil
from datetime import datetime
from pathlib import Path

# 處理導入路徑問題
import sys
from pathlib import Path

# 嘗試多種導入方式
try:
    from plant_diary.database import get_db
    from plant_diary.ai_analyzer import get_analyzer
    from plant_diary.ocr_reader import get_ocr_reader
except ImportError:
    try:
        # 如果從 plant_diary 目錄內運行，使用直接導入
        from database import get_db
        from ai_analyzer import get_analyzer
        from ocr_reader import get_ocr_reader
    except ImportError:
        # 最後嘗試：將當前目錄添加到路徑
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        from database import get_db
        from ai_analyzer import get_analyzer
        from ocr_reader import get_ocr_reader


class PlantDiaryApp:
    """植物日記主應用程式類"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("植物日記")
        self.root.geometry("1000x700")
        
        # 設置應用程式圖標
        try:
            # 嘗試多個可能的圖標路徑
            icon_paths = [
                Path("LOGO/FairyFern_logo.png"),
                Path("../LOGO/FairyFern_logo.png"),
                Path(__file__).parent.parent / "LOGO" / "FairyFern_logo.png"
            ]
            for icon_path in icon_paths:
                if icon_path.exists():
                    icon = Image.open(icon_path)
                    icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
                    self.root.iconphoto(False, ImageTk.PhotoImage(icon))
                    break
        except Exception:
            pass  # 如果載入圖標失敗，繼續運行
        
        # 初始化數據庫和 AI 分析器
        self.db = get_db()
        self.analyzer = get_analyzer()
        self.ocr_reader = get_ocr_reader()
        
        # 創建照片存儲目錄
        self.photos_dir = Path("plant_photos")
        self.photos_dir.mkdir(exist_ok=True)
        
        # 當前選中的植物
        self.current_plant_id = None
        self.current_photo_id = None
        
        # 創建界面
        self.create_widgets()
        self.refresh_plant_list()
    
    def create_widgets(self):
        """創建應用程式界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 左側：植物列表
        left_frame = ttk.LabelFrame(main_frame, text="我的植物", padding="10")
        left_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # 添加植物按鈕
        ttk.Button(left_frame, text="+ 添加新植物", command=self.add_plant_dialog).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 植物列表
        list_frame = ttk.Frame(left_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.plant_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.plant_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.plant_listbox.bind('<<ListboxSelect>>', self.on_plant_select)
        scrollbar.config(command=self.plant_listbox.yview)
        
        # 植物操作按鈕
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        ttk.Button(btn_frame, text="編輯", command=self.edit_plant_dialog).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(btn_frame, text="刪除", command=self.delete_plant).grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # 右側：植物詳情和照片
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # 植物信息區域
        info_frame = ttk.LabelFrame(right_frame, text="植物信息", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        self.info_text = tk.Text(info_frame, height=4, wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(info_frame, text="上傳照片", command=self.upload_photo).grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 照片時間線區域
        timeline_frame = ttk.LabelFrame(right_frame, text="成長歷程", padding="10")
        timeline_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        timeline_frame.columnconfigure(0, weight=1)
        timeline_frame.rowconfigure(0, weight=1)
        
        # 創建筆記本（標籤頁）
        self.notebook = ttk.Notebook(timeline_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 照片時間線標籤頁
        self.photo_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.photo_frame, text="照片時間線")
        self.photo_frame.columnconfigure(0, weight=1)
        self.photo_frame.rowconfigure(0, weight=1)
        
        # 照片列表（使用 Canvas + Scrollbar 實現滾動）
        photo_canvas_frame = ttk.Frame(self.photo_frame)
        photo_canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        photo_canvas_frame.columnconfigure(0, weight=1)
        photo_canvas_frame.rowconfigure(0, weight=1)
        
        photo_scrollbar = ttk.Scrollbar(photo_canvas_frame)
        photo_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.photo_canvas = tk.Canvas(photo_canvas_frame, yscrollcommand=photo_scrollbar.set)
        self.photo_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        photo_scrollbar.config(command=self.photo_canvas.yview)
        
        self.photo_content_frame = ttk.Frame(self.photo_canvas)
        self.photo_canvas_window = self.photo_canvas.create_window((0, 0), window=self.photo_content_frame, anchor="nw")
        
        # AI 分析標籤頁
        self.ai_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.ai_frame, text="AI 分析")
        self.ai_frame.columnconfigure(0, weight=1)
        self.ai_frame.rowconfigure(1, weight=1)
        
        ttk.Label(self.ai_frame, text="AI 分析結果和照顧建議", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.ai_text = scrolledtext.ScrolledText(self.ai_frame, wrap=tk.WORD, height=20)
        self.ai_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 綁定 Canvas 更新事件
        self.photo_content_frame.bind('<Configure>', lambda e: self.photo_canvas.configure(scrollregion=self.photo_canvas.bbox('all')))
        self.photo_canvas.bind('<Configure>', self._on_canvas_configure)
    
    def _on_canvas_configure(self, event):
        """當 Canvas 大小改變時，調整內部框架寬度"""
        canvas_width = event.width
        self.photo_canvas.itemconfig(self.photo_canvas_window, width=canvas_width)
    
    def refresh_plant_list(self):
        """刷新植物列表"""
        self.plant_listbox.delete(0, tk.END)
        plants = self.db.get_all_plants()
        for plant in plants:
            display_name = f"{plant['chinese_name']}"
            if plant['scientific_name']:
                display_name += f" ({plant['scientific_name']})"
            self.plant_listbox.insert(tk.END, display_name)
        
        # 存儲植物 ID 映射
        self.plant_id_map = {i: plant['id'] for i, plant in enumerate(plants)}
    
    def on_plant_select(self, event):
        """當選擇植物時"""
        selection = self.plant_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        self.current_plant_id = self.plant_id_map[idx]
        self.load_plant_info()
        self.load_plant_photos()
    
    def load_plant_info(self):
        """載入植物信息"""
        if not self.current_plant_id:
            self.info_text.delete(1.0, tk.END)
            return
        
        plant = self.db.get_plant(self.current_plant_id)
        if plant:
            info = f"中文名稱：{plant['chinese_name']}\n"
            if plant['scientific_name']:
                info += f"學名：{plant['scientific_name']}\n"
            if plant['notes']:
                info += f"備註：{plant['notes']}\n"
            info += f"建立日期：{plant['created_at'][:10]}"
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
    
    def add_plant_dialog(self):
        """添加植物對話框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加新植物")
        dialog.geometry("450x320")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 標題行
        title_label = ttk.Label(dialog, text="添加新植物", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(10, 20))
        
        # 從照片識別按鈕
        def recognize_from_photo():
            """從照片識別植物信息"""
            file_path = filedialog.askopenfilename(
                title="選擇植物花牌照片",
                filetypes=[
                    ("圖片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 顯示識別中提示
            recognize_btn.config(state="disabled")
            status_label = ttk.Label(dialog, text="正在識別...", foreground="blue")
            status_label.grid(row=1, column=0, columnspan=3, pady=5)
            dialog.update()
            
            try:
                # 獲取 OpenAI API 密鑰（如果可用）
                api_key = os.getenv("OPENAI_API_KEY")
                use_openai = api_key is not None
                
                # 進行 OCR 識別
                result = self.ocr_reader.recognize_text(
                    file_path, 
                    use_openai=use_openai,
                    openai_api_key=api_key
                )
                
                if result["success"]:
                    # 自動填充識別結果
                    if result["chinese_name"]:
                        chinese_entry.delete(0, tk.END)
                        chinese_entry.insert(0, result["chinese_name"])
                    
                    if result["scientific_name"]:
                        scientific_entry.delete(0, tk.END)
                        scientific_entry.insert(0, result["scientific_name"])
                    
                    status_label.config(text="識別成功！", foreground="green")
                    
                    # 如果識別結果不完整，顯示提示
                    if not result["chinese_name"] or not result["scientific_name"]:
                        status_label.config(
                            text="部分信息識別成功，請檢查並手動補充", 
                            foreground="orange"
                        )
                else:
                    status_label.config(text=f"識別失敗：{result.get('error', '未知錯誤')}", foreground="red")
                    
            except Exception as e:
                status_label.config(text=f"識別出錯：{str(e)}", foreground="red")
            finally:
                recognize_btn.config(state="normal")
                # 3秒後移除狀態標籤
                dialog.after(3000, status_label.destroy)
        
        recognize_btn = ttk.Button(
            dialog, 
            text="📷 從照片識別", 
            command=recognize_from_photo
        )
        recognize_btn.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
        
        # 分隔線
        separator = ttk.Separator(dialog, orient='horizontal')
        separator.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        ttk.Label(dialog, text="中文名稱：").grid(row=4, column=0, sticky=tk.W, padx=10, pady=10)
        chinese_entry = ttk.Entry(dialog, width=35)
        chinese_entry.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E))
        chinese_entry.focus()
        
        ttk.Label(dialog, text="學名：").grid(row=5, column=0, sticky=tk.W, padx=10, pady=10)
        scientific_entry = ttk.Entry(dialog, width=35)
        scientific_entry.grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="備註：").grid(row=6, column=0, sticky=(tk.W, tk.N), padx=10, pady=10)
        notes_text = tk.Text(dialog, width=35, height=5, wrap=tk.WORD)
        notes_text.grid(row=6, column=1, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # 配置列權重
        dialog.columnconfigure(1, weight=1)
        
        def save():
            chinese_name = chinese_entry.get().strip()
            if not chinese_name:
                messagebox.showerror("錯誤", "請輸入中文名稱")
                return
            
            self.db.add_plant(
                chinese_name=chinese_name,
                scientific_name=scientific_entry.get().strip(),
                notes=notes_text.get(1.0, tk.END).strip()
            )
            self.refresh_plant_list()
            dialog.destroy()
            messagebox.showinfo("成功", "植物已添加")
        
        # 按鈕框架
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="保存", command=save, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
        
        dialog.bind('<Return>', lambda e: save())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def edit_plant_dialog(self):
        """編輯植物對話框"""
        if not self.current_plant_id:
            messagebox.showwarning("提示", "請先選擇一個植物")
            return
        
        plant = self.db.get_plant(self.current_plant_id)
        if not plant:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("編輯植物")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="中文名稱：").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        chinese_entry = ttk.Entry(dialog, width=30)
        chinese_entry.insert(0, plant['chinese_name'])
        chinese_entry.grid(row=0, column=1, padx=10, pady=10)
        chinese_entry.focus()
        
        ttk.Label(dialog, text="學名：").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        scientific_entry = ttk.Entry(dialog, width=30)
        scientific_entry.insert(0, plant['scientific_name'] or "")
        scientific_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="備註：").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        notes_text = tk.Text(dialog, width=30, height=5, wrap=tk.WORD)
        notes_text.insert(1.0, plant['notes'] or "")
        notes_text.grid(row=2, column=1, padx=10, pady=10)
        
        def save():
            chinese_name = chinese_entry.get().strip()
            if not chinese_name:
                messagebox.showerror("錯誤", "請輸入中文名稱")
                return
            
            self.db.update_plant(
                self.current_plant_id,
                chinese_name=chinese_name,
                scientific_name=scientific_entry.get().strip(),
                notes=notes_text.get(1.0, tk.END).strip()
            )
            self.load_plant_info()
            self.refresh_plant_list()
            dialog.destroy()
            messagebox.showinfo("成功", "植物信息已更新")
        
        ttk.Button(dialog, text="保存", command=save).grid(row=3, column=0, columnspan=2, pady=20)
        dialog.bind('<Return>', lambda e: save())
    
    def delete_plant(self):
        """刪除植物"""
        if not self.current_plant_id:
            messagebox.showwarning("提示", "請先選擇一個植物")
            return
        
        plant = self.db.get_plant(self.current_plant_id)
        if not plant:
            return
        
        if messagebox.askyesno("確認", f"確定要刪除「{plant['chinese_name']}」嗎？\n這將同時刪除所有相關的照片記錄。"):
            self.db.delete_plant(self.current_plant_id)
            self.current_plant_id = None
            self.info_text.delete(1.0, tk.END)
            self.clear_photos()
            self.refresh_plant_list()
            messagebox.showinfo("成功", "植物已刪除")
    
    def upload_photo(self):
        """上傳照片"""
        if not self.current_plant_id:
            messagebox.showwarning("提示", "請先選擇一個植物")
            return
        
        file_path = filedialog.askopenfilename(
            title="選擇照片",
            filetypes=[
                ("圖片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # 複製照片到照片目錄
            plant = self.db.get_plant(self.current_plant_id)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = Path(file_path).suffix
            new_filename = f"{plant['chinese_name']}_{timestamp}{file_ext}"
            new_file_path = self.photos_dir / new_filename
            shutil.copy2(file_path, new_file_path)
            
            # 保存到數據庫
            photo_id = self.db.add_photo(
                plant_id=self.current_plant_id,
                photo_path=str(new_file_path),
                notes=""
            )
            
            # 使用 AI 分析（異步進行，不阻塞界面）
            self.root.after(100, lambda: self.analyze_photo(photo_id, str(new_file_path)))
            
            self.load_plant_photos()
            messagebox.showinfo("成功", "照片已上傳")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"上傳照片時出錯：{str(e)}")
    
    def analyze_photo(self, photo_id, image_path):
        """使用 AI 分析照片"""
        try:
            # 獲取植物信息以傳遞給 AI
            if self.current_plant_id:
                plant = self.db.get_plant(self.current_plant_id)
                chinese_name = plant.get('chinese_name') if plant else None
                scientific_name = plant.get('scientific_name') if plant else None
            else:
                chinese_name = None
                scientific_name = None
            
            result = self.analyzer.analyze_plant_photo(
                image_path,
                chinese_name=chinese_name,
                scientific_name=scientific_name
            )
            self.db.update_photo_analysis(
                photo_id=photo_id,
                ai_analysis=result['ai_analysis'],
                care_suggestions=result['care_suggestions']
            )
            # 如果當前顯示的是這張照片，刷新顯示
            if self.current_photo_id == photo_id:
                self.show_photo_details(photo_id)
        except Exception as e:
            print(f"AI 分析出錯：{e}")
    
    def load_plant_photos(self):
        """載入植物的照片列表"""
        if not self.current_plant_id:
            self.clear_photos()
            return
        
        # 清除現有內容
        for widget in self.photo_content_frame.winfo_children():
            widget.destroy()
        
        photos = self.db.get_plant_photos(self.current_plant_id)
        
        if not photos:
            ttk.Label(self.photo_content_frame, text="尚未添加照片，請點擊「上傳照片」按鈕添加。").pack(pady=20)
            return
        
        # 顯示每張照片
        for photo in photos:
            self.create_photo_widget(photo)
        
        # 更新滾動區域
        self.photo_content_frame.update_idletasks()
        self.photo_canvas.configure(scrollregion=self.photo_canvas.bbox('all'))
    
    def create_photo_widget(self, photo):
        """創建照片顯示組件"""
        photo_frame = ttk.LabelFrame(self.photo_content_frame, padding="10")
        photo_frame.pack(fill=tk.X, padx=5, pady=5)
        photo_frame.columnconfigure(1, weight=1)
        
        # 載入並顯示縮略圖
        try:
            img = Image.open(photo['photo_path'])
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            photo_img = ImageTk.PhotoImage(img)
            
            img_label = ttk.Label(photo_frame, image=photo_img)
            img_label.image = photo_img  # 保持引用
            img_label.grid(row=0, column=0, rowspan=3, padx=(0, 10))
            
        except Exception as e:
            ttk.Label(photo_frame, text="無法載入圖片").grid(row=0, column=0, rowspan=3, padx=(0, 10))
        
        # 照片信息
        date_str = photo['taken_at'][:10] if photo['taken_at'] else "未知日期"
        ttk.Label(photo_frame, text=f"拍攝日期：{date_str}", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W)
        
        if photo['notes']:
            ttk.Label(photo_frame, text=f"備註：{photo['notes']}", wraplength=400).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 查看詳情按鈕
        def show_details():
            self.show_photo_details(photo['id'])
        
        ttk.Button(photo_frame, text="查看詳情和AI分析", command=show_details).grid(row=2, column=1, sticky=tk.W, pady=5)
    
    def show_photo_details(self, photo_id):
        """顯示照片詳情和AI分析"""
        photos = self.db.get_plant_photos(self.current_plant_id)
        photo = next((p for p in photos if p['id'] == photo_id), None)
        
        if not photo:
            return
        
        self.current_photo_id = photo_id
        
        # 切換到 AI 分析標籤頁
        self.notebook.select(1)
        
        # 顯示分析結果
        content = f"拍攝日期：{photo['taken_at']}\n\n"
        content += "=" * 50 + "\n"
        content += "AI 分析結果\n"
        content += "=" * 50 + "\n\n"
        content += (photo['ai_analysis'] or "正在分析中...") + "\n\n"
        
        if photo['care_suggestions']:
            content += "=" * 50 + "\n"
            content += "照顧建議\n"
            content += "=" * 50 + "\n\n"
            content += photo['care_suggestions'] + "\n"
        
        self.ai_text.delete(1.0, tk.END)
        self.ai_text.insert(1.0, content)
        
        # 如果還在分析中，稍後再檢查
        if not photo['ai_analysis']:
            self.root.after(2000, lambda: self.show_photo_details(photo_id))
    
    def clear_photos(self):
        """清除照片顯示"""
        for widget in self.photo_content_frame.winfo_children():
            widget.destroy()
        self.ai_text.delete(1.0, tk.END)
        self.current_photo_id = None
    
    def on_closing(self):
        """應用程式關閉時"""
        self.db.close()
        self.root.destroy()


def main():
    """主函數"""
    root = tk.Tk()
    app = PlantDiaryApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

