# AI Stunt Studio

A Python GUI app for generating AI stunt images using Veo 3.

## Setup Instructions

1. Install Python 3.x
2. Install dependencies:
```
   pip install pillow requests
```
3. Run the app:
```
   python main.py
```
4. **Enter your Gemini API key** in the text box at the top of the app
   - Get a free key at: https://aistudio.google.com/apikey

## Project Files

| File | Description |
|------|-------------|
| `main.py` | Main application code |
| `.gitignore` | Ignores temp files |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

## App Layout

The app window contains:
- **API Key section** - Text box to enter your Gemini API key (hidden by default with show/hide toggle)
- **Face display** - Shows random AI-generated faces or your uploaded photo
- **Pass / Use buttons** - Skip the current face or select it for generation
- **Upload button** - Choose your own image file from your computer
- **Prompt box** - Describe what stunt you want the person doing
- **Generate button** - Sends request to Veo 3 API
- **Status bar** - Shows current app status and messages

## Features

- Fetches random AI-generated faces from thispersondoesnotexist.com
- Upload your own photos
- Custom prompt input for Veo 3
- Secure API key input (hidden by default)
- Event logging with timestamps

## Project Requirements Met

| Criteria | Implementation |
|----------|----------------|
| GUI with Tkinter | Full app with buttons, labels, text boxes, checkboxes |
| Custom Functions with kwargs | `log_event()` and `generate_image_with_veo()` |
| Does Something with Input | Fetches faces from web, processes user prompts |
| Hosted on GitHub | ✓ |
