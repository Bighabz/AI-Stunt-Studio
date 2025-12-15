"""
AI Stunt Studio - CSE Python Final Project
Author: Habib
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import datetime
import os
import time
import threading


def log_event(event_type, **kwargs):
    """Logs events with timestamp and any extra info passed via kwargs"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    extras = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    log_line = f"[{timestamp}] {event_type}: {extras}"
    print(log_line)
    
    with open("app_log.txt", "a") as f:
        f.write(log_line + "\n")


def save_generation_request(prompt, image_path, api_key=None, **kwargs):
    """Saves the generation request to a file for demo mode"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generation_request_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write("=" * 50 + "\n")
        f.write("AI STUNT STUDIO - GENERATION REQUEST\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Timestamp: {datetime.datetime.now()}\n")
        f.write(f"Image: {image_path}\n")
        f.write(f"API Key Provided: {'Yes' if api_key else 'No'}\n\n")
        f.write("PROMPT:\n")
        f.write("-" * 50 + "\n")
        f.write(prompt + "\n")
        f.write("-" * 50 + "\n")
    
    log_event("Request_Saved", filename=filename)
    return filename


def generate_video_with_veo(prompt, image_path, api_key, status_callback=None):
    """
    Actually calls the Veo 3 API to generate a video.
    Returns (success, message, video_path)
    """
    try:
        from google import genai
        from google.genai import types
        
        if status_callback:
            status_callback("Connecting to Veo 3 API...")
        
        client = genai.Client(api_key=api_key)
        
        if status_callback:
            status_callback("Generating video (1-2 minutes)...")
        
        operation = client.models.generate_videos(
            model="veo-3.0-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
            ),
        )
        
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
            if status_callback:
                status_callback("Still generating...")
        
        generated_video = operation.result.generated_videos[0]
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"stunt_video_{timestamp}.mp4"
        
        client.files.download(file=generated_video.video)
        generated_video.video.save(video_filename)
        
        log_event("Video_Generated", filename=video_filename)
        return (True, f"Video saved as: {video_filename}", video_filename)
        
    except ImportError:
        return (False, "Missing library! Run: pip install google-genai", None)
    except Exception as e:
        error_msg = str(e)
        log_event("API_Error", error=error_msg)
        return (False, f"API Error: {error_msg}", None)


class AIStuntStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Stunt Studio")
        self.root.configure(bg="#1a1a2e")
        
        # Get screen size and set window size
        screen_height = self.root.winfo_screenheight()
        window_height = min(750, screen_height - 100)
        self.root.geometry(f"600x{window_height}")
        
        self.current_image = None
        self.selected_image_path = None
        self.is_generating = False
        
        self.setup_ui()
        self.fetch_random_face()
    
    def setup_ui(self):
        # ============================================
        # HEADER (compact)
        # ============================================
        header_frame = tk.Frame(self.root, bg="#16213e", pady=8)
        header_frame.pack(fill="x")
        
        title = tk.Label(
            header_frame, 
            text="🎬 AI Stunt Studio 🎬", 
            font=("Helvetica", 18, "bold"),
            bg="#16213e",
            fg="#e94560"
        )
        title.pack()
        
        # ============================================
        # MAIN CONTENT - Two columns
        # ============================================
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # LEFT COLUMN - Image
        left_frame = tk.Frame(main_frame, bg="#1a1a2e")
        left_frame.pack(side="left", fill="both", expand=True)
        
        # Image container
        image_container = tk.Frame(left_frame, bg="#e94560", padx=3, pady=3)
        image_container.pack(pady=5)
        
        self.image_label = tk.Label(
            image_container, 
            text="Loading...", 
            width=280,
            height=280,
            bg="#2d2d44",
            fg="#ffffff",
            font=("Helvetica", 10)
        )
        self.image_label.pack()
        
        # Buttons under image
        btn_frame = tk.Frame(left_frame, bg="#1a1a2e")
        btn_frame.pack(pady=5)
        
        self.skip_btn = tk.Button(
            btn_frame, 
            text="🔄 Skip to Next Face", 
            command=self.fetch_random_face, 
            width=18,
            font=("Helvetica", 9, "bold"),
            bg="#ff6b6b",
            fg="#ffffff",
            relief="flat",
            cursor="hand2"
        )
        self.skip_btn.pack(pady=2)
        
        self.upload_btn = tk.Button(
            btn_frame, 
            text="📁 Upload Your Photo", 
            command=self.on_upload,
            width=18,
            font=("Helvetica", 9, "bold"),
            bg="#a855f7",
            fg="#ffffff",
            relief="flat",
            cursor="hand2"
        )
        self.upload_btn.pack(pady=2)
        
        # RIGHT COLUMN - API Key + Prompt + Generate
        right_frame = tk.Frame(main_frame, bg="#1a1a2e")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # API Key Section
        api_frame = tk.LabelFrame(
            right_frame, 
            text="🔑 API Key (optional)", 
            padx=10, 
            pady=5,
            bg="#1a1a2e",
            fg="#ffffff",
            font=("Helvetica", 9, "bold")
        )
        api_frame.pack(fill="x", pady=5)
        
        self.api_key_entry = tk.Entry(
            api_frame, 
            width=30, 
            show="*",
            font=("Helvetica", 10),
            bg="#2d2d44",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat"
        )
        self.api_key_entry.pack(pady=3, ipady=3)
        
        key_options = tk.Frame(api_frame, bg="#1a1a2e")
        key_options.pack(fill="x")
        
        self.show_key_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            key_options, 
            text="Show", 
            variable=self.show_key_var,
            command=self.toggle_key_visibility,
            bg="#1a1a2e",
            fg="#a0a0a0",
            selectcolor="#2d2d44"
        ).pack(side="left")
        
        tk.Label(
            key_options,
            text="Get key: aistudio.google.com",
            font=("Helvetica", 7),
            bg="#1a1a2e",
            fg="#4ecdc4"
        ).pack(side="right")
        
        # Prompt Section
        prompt_frame = tk.LabelFrame(
            right_frame,
            text="✍ Describe the Stunt",
            padx=10,
            pady=5,
            bg="#1a1a2e",
            fg="#ffffff",
            font=("Helvetica", 9, "bold")
        )
        prompt_frame.pack(fill="both", expand=True, pady=5)
        
        self.prompt_entry = tk.Text(
            prompt_frame, 
            height=6, 
            width=30,
            font=("Helvetica", 10),
            bg="#2d2d44",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            padx=5,
            pady=5,
            wrap="word"
        )
        self.prompt_entry.pack(fill="both", expand=True, pady=3)
        self.prompt_entry.insert("1.0", "Doing a backflip on a skateboard at sunset")
        
        # Generate Button
        self.generate_btn = tk.Button(
            right_frame, 
            text="🎥 GENERATE VIDEO", 
            command=self.on_generate,
            font=("Helvetica", 12, "bold"),
            bg="#e94560",
            fg="#ffffff",
            activebackground="#d63050",
            relief="flat",
            cursor="hand2",
            pady=8
        )
        self.generate_btn.pack(fill="x", pady=10)
        
        # ============================================
        # STATUS BAR
        # ============================================
        status_frame = tk.Frame(self.root, bg="#16213e", pady=5)
        status_frame.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            status_frame, 
            text="✓ Ready", 
            font=("Helvetica", 9),
            bg="#16213e",
            fg="#4ecdc4"
        )
        self.status_label.pack()
    
    def update_status(self, text, color="#4ecdc4"):
        self.status_label.config(text=text, fg=color)
        self.root.update()
    
    def toggle_key_visibility(self):
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
    
    def get_api_key(self):
        return self.api_key_entry.get().strip()
    
    def fetch_random_face(self):
        if self.is_generating:
            return
            
        try:
            self.update_status("⏳ Fetching face...", "#feca57")
            
            url = "https://thispersondoesnotexist.com"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            
            img = Image.open(BytesIO(response.content))
            img = img.resize((280, 280))
            img.save("temp_face.jpg")
            
            self.selected_image_path = "temp_face.jpg"
            
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.current_image, text="", width=280, height=280)
            
            log_event("Face_Fetched")
            self.update_status("✓ Face loaded!", "#4ecdc4")
            
        except Exception as e:
            self.update_status(f"✗ Error: {str(e)[:25]}", "#ff6b6b")
            log_event("Error", message=str(e))
    
    def on_upload(self):
        if self.is_generating:
            return
            
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        if path:
            self.selected_image_path = path
            img = Image.open(path).resize((280, 280))
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.current_image, width=280, height=280)
            log_event("User_Upload", path=path)
            self.update_status("✓ Photo uploaded!", "#4ecdc4")
    
    def on_generate(self):
        if self.is_generating:
            messagebox.showinfo("Please Wait", "Already generating!")
            return
            
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        api_key = self.get_api_key()
        
        if not prompt:
            messagebox.showwarning("Missing Prompt", "Enter a stunt description!")
            return
        
        if not self.selected_image_path:
            messagebox.showwarning("No Image", "Load a face first!")
            return
        
        # DEMO MODE
        if not api_key:
            self.update_status("📝 Demo mode...", "#feca57")
            saved_file = save_generation_request(prompt, self.selected_image_path)
            self.update_status("✓ Saved to file!", "#4ecdc4")
            messagebox.showinfo(
                "Demo Mode", 
                f"Saved to: {saved_file}\n\nAdd API key for real video generation."
            )
            try:
                os.startfile(os.getcwd())
            except:
                pass
            return
        
        # REAL API MODE
        self.is_generating = True
        self.generate_btn.config(state="disabled", text="⏳ Generating...")
        self.update_status("🎬 Starting...", "#feca57")
        
        def generate_thread():
            success, message, video_path = generate_video_with_veo(
                prompt, 
                self.selected_image_path, 
                api_key,
                status_callback=lambda s: self.root.after(0, lambda: self.update_status(s, "#feca57"))
            )
            
            def finish():
                self.is_generating = False
                self.generate_btn.config(state="normal", text="🎥 GENERATE VIDEO")
                
                if success:
                    self.update_status("✓ Video created!", "#4ecdc4")
                    messagebox.showinfo("Success!", message)
                    try:
                        os.startfile(os.getcwd())
                    except:
                        pass
                else:
                    self.update_status("✗ Failed", "#ff6b6b")
                    messagebox.showerror("Error", message)
            
            self.root.after(0, finish)
        
        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = AIStuntStudio(root)
    root.mainloop()
