# 🎬 AI Stunt Studio

A Python GUI app for generating AI stunt videos using Google Veo 3.

---

## 📥 Download and Installation

### Step 1: Download the Project

1. Click the green **Code** button at the top of this page
2. Click **Download ZIP**
3. Extract the ZIP file to a folder on your computer (e.g., `C:\Users\YourName\Downloads\AI-Stunt-Studio`)

### Step 2: Open Terminal/Command Prompt

**Windows:**
1. Open the extracted folder
2. Click in the address bar at the top
3. Type `cmd` and press Enter

**Mac:**
1. Open Terminal
2. Type `cd ` (with a space after)
3. Drag the extracted folder into Terminal
4. Press Enter

**Linux:**
1. Right-click in the extracted folder
2. Click "Open Terminal Here"

### Step 3: Install Dependencies

Run this command in your terminal:
```
pip install pillow requests google-genai
```

If that doesn't work, try:
```
pip3 install pillow requests google-genai
```

### Step 4: Launch the App

Run this command:
```
python main.py
```

If that doesn't work, try:
```
python3 main.py
```

---

## 🖥️ How to Use the App

### When the App Opens:

1. A random AI-generated face will automatically load in the center of the window

### To Select a Face:

- **Skip to Next Face** - Click this button to load a different random AI face
- **Upload Your Own Photo** - Click this to select an image from your computer

### To Generate a Video:

1. Make sure a face is displayed (either random or uploaded)
2. Type a stunt description in the text box (e.g., "Doing a backflip on a skateboard at sunset")
3. (Optional) Enter your Gemini API key in the API Key box at the top
4. Click the **Generate Stunt Video** button

---

## 🎯 Expected Results

### Demo Mode (No API Key):

If you **don't** enter an API key:

1. The app will save your request to a text file
2. A file like `generation_request_20250614_143022.txt` will appear in the app folder
3. Your folder will automatically open to show the saved file
4. The text file contains your prompt and image path

### Real Mode (With API Key):

If you **do** enter a valid Gemini API key:

1. The app will connect to Google's Veo 3 API
2. Status will show "Generating video (this may take 1-2 minutes)..."
3. A video file like `stunt_video_20250614_143022.mp4` will be saved to your folder
4. Your folder will automatically open to show the generated video

---

## 🔑 How to Get an API Key (Optional)

1. Go to: https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key
5. Paste it into the **API Key** box in the app

**Note:** The API key is optional. The app works in Demo Mode without it.

---

## 📁 Project Files

| File | Description |
|------|-------------|
| `main.py` | Main application code |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Ignores temp files |
| `README.md` | This file |

---

## ✅ Features

- Fetches random AI-generated faces from thispersondoesnotexist.com
- Upload your own photos
- Custom prompt input for Veo 3
- Secure API key input (hidden by default)
- Demo mode works without API key
- Real video generation with Veo 3 API
- Event logging with timestamps
- Dark theme UI

---

## 📋 Project Requirements Met

| Criteria | Implementation |
|----------|----------------|
| GUI with Tkinter | Full app with buttons, labels, text boxes, checkboxes |
| Custom Functions with kwargs | `log_event()` and `generate_video_with_veo()` |
| Does Something with Input | Fetches faces from web, generates videos or saves requests |
| Hosted on GitHub | ✓ |

---

## ❓ Troubleshooting

### "python is not recognized"
- Make sure Python is installed: https://www.python.org/downloads/
- During installation, check the box that says "Add Python to PATH"

### "No module named PIL" or "No module named requests"
- Run the install command again: `pip install pillow requests google-genai`

### App window doesn't open
- Make sure you're in the correct folder in terminal
- Try `python3 main.py` instead of `python main.py`

### Face doesn't load
- Check your internet connection
- The website thispersondoesnotexist.com may be temporarily down

---

## 👤 Author

Habib Jahshan - Adv App Dev Python Final Project
