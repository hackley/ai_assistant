import sys
import subprocess

description = {
  "action": "open_website",
  "description": "Opens a new tab in the user's browser with the given URL.",
  "arguments": {
    "url": "The URL of the website to open. Please include http:// or https://.",
  }
}

def open_website(args):
  url = args.get('url')
  if url:
    try:
      if sys.platform == 'darwin':  # macOS
        subprocess.Popen(['open', '-a', 'Google Chrome', url])
      elif sys.platform == 'win32':  # Windows
        subprocess.Popen(['start', 'chrome', url], shell=True)
      else:  # Linux
        subprocess.Popen(['google-chrome', url])

      return f"Opened a new tab with the website '{url}'."
    except Exception as e:
      return f"Couldn't open the website: {e}"
  else:
    return "Couldn't open the website. No URL provided."
