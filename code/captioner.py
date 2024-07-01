import requests
import google.generativeai as genai
import os
import dotenv

dotenv.load_dotenv()

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

history = []

def generate_caption(image_path):
    GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    imageObj = genai.upload_file(path=image_path)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest",
                                  safety_settings=safety_settings)
    question = "generation only one caption for this image"
    response = model.generate_content([question, imageObj])
    ans = response.text
    history.append(ans)
    return ans

def query_on_image(image_path, query):
    GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    imageObj = genai.upload_file(path=image_path)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest",
                                  safety_settings=safety_settings)
    response = model.generate_content([query, imageObj])
    history.append(response.text)
    return response.text

if __name__ == "__main__":
    print(generate_caption("G:\work\interactive-image-caption-generator\code\static\img\post-portrait-7.jpg"))
    print(query_on_image("G:\work\interactive-image-caption-generator\code\static\img\post-portrait-7.jpg", "What is this she holding?"))