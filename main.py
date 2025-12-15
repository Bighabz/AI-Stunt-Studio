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


def log_event(event_type, **kwargs):
    """Logs events with timestamp and any extra info passed via kwargs"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    extras = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    log_line = f"[{timestamp}] {event_type}: {extras}"
    print(log_line)
    
    with open("app_log.txt", "a") as f:
        f.write(log_line + "\n")


def generate_image_with_veo(prompt, image_path, api_key=None, **kwargs):
    """Calls Veo 3 API (or runs in demo mode if no key)"""
    log_event("Veo_Request", prompt=prompt[:50], image=image_path, has_key=bool(api_key))
    
    if not api_key:
        return "DEMO MODE: Please enter your Gemini API key above."
    
    # TODO: Real Veo 3 API call would go here
    return f"API key received! Would send prompt: {prompt}"


class AIStuntStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Stunt Studio")
        self.root.geometry("420x650")
        
        self.current_image = None
        self.selected_image_path = None
        
        self.setup_ui()
        self.fetch_random_face()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="AI Stunt Studio", font=("Helvetica", 18, "bold"))
        title.pack(pady=10)
        
        # API Key Section
        api_frame = tk.LabelFrame(self.root, text="API Key", padx=10, pady=5)
        api_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(api_frame, text="Gemini API Key:", font=("Helvetica", 9)).pack(anchor="w")
        
        self.api_key_entry = tk.Entry(api_frame, width=45, show="*")
        self.api_key_entry.pack(pady=2)
        
        self.show_key_var = tk.BooleanVar(value=False)
        self.show_key_btn = tk.Checkbutton(
            api_frame, 
            text="Show key", 
            variable=self.show_key_var,
            command=self.toggle_key_visibility
        )
        self.show_key_btn.pack(anchor="w")
        
        # Image Display
        self.image_label = tk.Label(self.root, text="Loading face...", width=32, height=16)
        self.image_label.pack(pady=10)
        
        # Pass / Use Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="Pass", command=self.on_pass, width=12).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Use This", command=self.on_use_face, width=12).grid(row=0, column=1, padx=5)
        
        # Upload Button
        tk.Button(self.root, text="Upload Your Own Photo", command=self.on_upload).pack(pady=5)
        
        # Prompt Input
        tk.Label(self.root, text="Describe the stunt:").pack(pady=(10, 0))
        self.prompt_entry = tk.Text(self.root, height=3, width=45)
        self.prompt_entry.pack(pady=5)
        self.prompt_entry.insert("1.0", "Doing a backflip on a skateboard")
        
        # Generate Button
        tk.Button(
            self.root, 
            text="Generate with Veo 3", 
            command=self.on_generate,
            bg="#4CAF50", 
            fg="white",
            font=("Helvetica", 11, "bold"),
            padx=20,
            pady=5
        ).pack(pady=10)
        
        # Status Label
        self.status_label = tk.Label(self.root, text="Ready", fg="gray")
        self.status_label.pack()
    
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
        try:
            self.status_label.config(text="Fetching face...")
            self.root.update()
            
            url = "https://thispersondoesnotexist.com"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            
            img = Image.open(BytesIO(response.content))
            img = img.resize((256, 256))
            img.save("temp_face.jpg")
            
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.current_image, text="")
            
            log_event("Face_Fetched", source="thispersondoesnotexist.com")
            self.status_label.config(text="New face loaded!")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)[:30]}")
            log_event("Error", message=str(e))
    
    def on_pass(self):
        """Skip current face"""
        log_event("Face_Passed")
        self.fetch_random_face()
    
    def on_use_face(self):
        """Select current face"""
        self.selected_image_path = "temp_face.jpg"
        log_event("Face_Selected", path=self.selected_image_path)
        self.status_label.config(text="Face selected!")
        messagebox.showinfo("Selected", "This face will be used for generation!")
    
    def on_upload(self):
        """Upload own photo"""
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        if path:
            self.selected_image_path = path
            img = Image.open(path).resize((256, 256))
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.current_image)
            log_event("User_Upload", path=path)
            self.status_label.config(text="Your photo loaded!")
    
    def on_generate(self):
        """Generate with Veo 3"""
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        api_key = self.get_api_key()
        
        if not prompt:
            messagebox.showwarning("Missing Prompt", "Please enter a stunt description!")
            return
        
        if not self.selected_image_path:
            messagebox.showwarning("No Image", "Please select or upload a face first!")
            return
        
        if not api_key:
            messagebox.showwarning("No API Key", "Please enter your Gemini API key.\n\nGet one at:\nhttps://aistudio.google.com/apikey")
            return
        
        self.status_label.config(text="Sending request...")
        self.root.update()
        
        result = generate_image_with_veo(prompt, self.selected_image_path, api_key=api_key)
        
        self.status_label.config(text="Done!")
        messagebox.showinfo("Veo 3 Result", result)
        log_event("Generation_Complete", prompt=prompt[:30])


if __name__ == "__main__":
    root = tk.Tk()
    app = AIStuntStudio(root)
    root.mainloop()
```
