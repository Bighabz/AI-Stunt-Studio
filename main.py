"""
AI Stunt Studio - Python Final Project
Author: Habib Jahshan
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
        # Import the Google GenAI library
        from google import genai
        from google.genai import types
        
        if status_callback:
            status_callback("🔄 Connecting to Veo 3 API...")
        
        # Create client with API key
        client = genai.Client(api_key=api_key)
        
        if status_callback:
            status_callback("🎬 Generating video (this may take 1-2 minutes)...")
        
        # Start video generation
        operation = client.models.generate_videos(
            model="veo-3.0-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
            ),
        )
        
        # Wait for generation to complete
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
            if status_callback:
                status_callback("⏳ Still generating...")
        
        # Get the generated video
        generated_video = operation.result.generated_videos[0]
        
        # Download and save
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
        self.root.geometry("500x800")
        self.root.configure(bg="#1a1a2e")
        
        self.current_image = None
        self.selected_image_path = None
        self.is_generating = False
        
        self.setup_ui()
        self.fetch_random_face()
    
    def setup_ui(self):
        # ============================================
        # HEADER
        # ============================================
        header_frame = tk.Frame(self.root, bg="#16213e", pady=15)
        header_frame.pack(fill="x")
        
        title = tk.Label(
            header_frame, 
            text="🎬 AI Stunt Studio 🎬", 
            font=("Helvetica", 24, "bold"),
            bg="#16213e",
            fg="#e94560"
        )
        title.pack()
        
        subtitle = tk.Label(
            header_frame,
            text="Generate epic stunt videos with AI faces",
            font=("Helvetica", 10),
            bg="#16213e",
            fg="#a0a0a0"
        )
        subtitle.pack()
        
        # ============================================
        # API KEY SECTION
        # ============================================
        api_frame = tk.LabelFrame(
            self.root, 
            text="🔑 API Key", 
            padx=15, 
            pady=10,
            bg="#1a1a2e",
            fg="#ffffff",
            font=("Helvetica", 10, "bold")
        )
        api_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            api_frame, 
            text="Enter your Gemini API Key (optional for demo):", 
            font=("Helvetica", 9),
            bg="#1a1a2e",
            fg="#a0a0a0"
        ).pack(anchor="w")
        
        self.api_key_entry = tk.Entry(
            api_frame, 
            width=50, 
            show="*",
            font=("Helvetica", 11),
            bg="#2d2d44",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat"
        )
        self.api_key_entry.pack(pady=5, ipady=5)
        
        self.show_key_var = tk.BooleanVar(value=False)
        self.show_key_btn = tk.Checkbutton(
            api_frame, 
            text="Show key", 
            variable=self.show_key_var,
            command=self.toggle_key_visibility,
            bg="#1a1a2e",
            fg="#a0a0a0",
            selectcolor="#2d2d44",
            activebackground="#1a1a2e",
            activeforeground="#ffffff"
        )
        self.show_key_btn.pack(anchor="w")
        
        # Get API key link
        api_link = tk.Label(
            api_frame,
            text="Get a free API key at: aistudio.google.com/apikey",
            font=("Helvetica", 8),
            bg="#1a1a2e",
            fg="#4ecdc4",
            cursor="hand2"
        )
        api_link.pack(anchor="w")
        
        # ============================================
        # IMAGE DISPLAY SECTION
        # ============================================
        image_section = tk.LabelFrame(
            self.root,
            text="👤 Select a Face",
            padx=15,
            pady=10,
            bg="#1a1a2e",
            fg="#ffffff",
            font=("Helvetica", 10, "bold")
        )
        image_section.pack(fill="x", padx=20, pady=10)
        
        # Image container with border
        image_container = tk.Frame(
            image_section,
            bg="#e94560",
            padx=3,
            pady=3
        )
        image_container.pack(pady=10)
        
        self.image_label = tk.Label(
            image_container, 
            text="Loading face...", 
            width=350,
            height=350,
            bg="#2d2d44",
            fg="#ffffff",
            font=("Helvetica", 12)
        )
        self.image_label.pack()
        
        # Button frame
        btn_frame = tk.Frame(image_section, bg="#1a1a2e")
        btn_frame.pack(pady=10)
        
        # SKIP BUTTON
        self.skip_btn = tk.Button(
            btn_frame, 
            text="🔄 Skip to Next Face", 
            command=self.fetch_random_face, 
            width=20,
            font=("Helvetica", 11, "bold"),
            bg="#ff6b6b",
            fg="#ffffff",
            activebackground="#ee5a5a",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2"
        )
        self.skip_btn.pack(pady=5)
        
        # Upload button
        self.upload_btn = tk.Button(
            btn_frame, 
            text="📁 Upload Your Own Photo", 
            command=self.on_upload,
            width=20,
            font=("Helvetica", 11, "bold"),
            bg="#a855f7",
            fg="#ffffff",
            activebackground="#9333ea",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2"
        )
        self.upload_btn.pack(pady=5)
        
        # ============================================
        # PROMPT SECTION
        # ============================================
        prompt_section = tk.LabelFrame(
            self.root,
            text="✍ Describe the Stunt",
            padx=15,
            pady=10,
            bg="#1a1a2e",
            fg="#ffffff",
            font=("Helvetica", 10, "bold")
        )
        prompt_section.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            prompt_section,
            text="What epic stunt should this person do?",
            font=("Helvetica", 9),
            bg="#1a1a2e",
            fg="#a0a0a0"
        ).pack(anchor="w")
        
        self.prompt_entry = tk.Text(
            prompt_section, 
            height=3, 
            width=50,
            font=("Helvetica", 11),
            bg="#2d2d44",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            padx=10,
            pady=10
        )
        self.prompt_entry.pack(pady=10)
        self.prompt_entry.insert("1.0", "Doing a backflip on a skateboard at sunset")
        
        # ============================================
        # GENERATE BUTTON
        # ============================================
        self.generate_btn = tk.Button(
            self.root, 
            text="🎥 Generate Stunt Video", 
            command=self.on_generate,
            font=("Helvetica", 14, "bold"),
            bg="#e94560",
            fg="#ffffff",
            activebackground="#d63050",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=10
        )
        self.generate_btn.pack(pady=15)
        
        # ============================================
        # STATUS BAR
        # ============================================
        status_frame = tk.Frame(self.root, bg="#16213e", pady=8)
        status_frame.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            status_frame, 
            text="✓ Ready - Select a face and enter a prompt", 
            font=("Helvetica", 10),
            bg="#16213e",
            fg="#4ecdc4"
        )
        self.status_label.pack()
    
    def update_status(self, text, color="#4ecdc4"):
        """Update status label (thread-safe)"""
        self.status_label.config(text=text, fg=color)
        self.root.update()
    
    def toggle_key_visibility(self):
        """Shows or hides the API key"""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
    
    def get_api_key(self):
        """Returns the API key from input"""
        return self.api_key_entry.get().strip()
    
    def fetch_random_face(self):
        """Fetches a random AI-generated face"""
        if self.is_generating:
            return
            
        try:
            self.update_status("⏳ Fetching new face...", "#feca57")
            
            url = "https://thispersondoesnotexist.com"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            
            img = Image.open(BytesIO(response.content))
            img = img.resize((350, 350))
            img.save("temp_face.jpg")
            
            self.selected_image_path = "temp_face.jpg"
            
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.current_image, text="", width=350, height=350)
            
            log_event("Face_Fetched", source="thispersondoesnotexist.com")
            self.update_status("✓ Face loaded and selected!", "#4ecdc4")
            
        except Exception as e:
            self.update_status(f"✗ Error: {str(e)[:30]}", "#ff6b6b")
            log_event("Error", message=str(e))
    
    def on_upload(self):
        """Upload own photo"""
        if self.is_generating:
            return
            
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        if path:
            self.selected_image_path = path
            img = Image.open(path).resize((350, 350))
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.current_image, width=350, height=350)
            log_event("User_Upload", path=path)
            self.update_status("✓ Your photo loaded and selected!", "#4ecdc4")
    
    def on_generate(self):
        """Generate with Veo 3"""
        if self.is_generating:
            messagebox.showinfo("Please Wait", "A video is already being generated!")
            return
            
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        api_key = self.get_api_key()
        
        if not prompt:
            messagebox.showwarning("Missing Prompt", "Please enter a stunt description!")
            return
        
        if not self.selected_image_path:
            messagebox.showwarning("No Image", "Please wait for a face to load or upload one!")
            return
        
        # ============================================
        # DEMO MODE (no API key)
        # ============================================
        if not api_key:
            self.update_status("📝 Demo mode - saving request...", "#feca57")
            saved_file = save_generation_request(prompt, self.selected_image_path)
            self.update_status("✓ Demo complete! Check your folder.", "#4ecdc4")
            messagebox.showinfo(
                "Demo Mode", 
                f"Request saved to: {saved_file}\n\n"
                "To actually generate videos, enter your Gemini API key.\n\n"
                "Get one at: aistudio.google.com/apikey"
            )
            try:
                os.startfile(os.getcwd())
            except:
                pass
            return
        
        # ============================================
        # REAL API MODE (has API key)
        # ============================================
        self.is_generating = True
        self.generate_btn.config(state="disabled", text="⏳ Generating...")
        self.update_status("🎬 Starting Veo 3 generation...", "#feca57")
        
        # Run in thread so UI doesn't freeze
        def generate_thread():
            success, message, video_path = generate_video_with_veo(
                prompt, 
                self.selected_image_path, 
                api_key,
                status_callback=lambda s: self.root.after(0, lambda: self.update_status(s, "#feca57"))
            )
            
            # Update UI on main thread
            def finish():
                self.is_generating = False
                self.generate_btn.config(state="normal", text="🎥 Generate Stunt Video")
                
                if success:
                    self.update_status("✓ Video generated!", "#4ecdc4")
                    messagebox.showinfo("Success!", message)
                    try:
                        os.startfile(os.getcwd())
                    except:
                        pass
                else:
                    self.update_status("✗ Generation failed", "#ff6b6b")
                    messagebox.showerror("Error", message)
            
            self.root.after(0, finish)
        
        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = AIStuntStudio(root)
    root.mainloop()
