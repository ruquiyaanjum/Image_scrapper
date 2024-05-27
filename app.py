from flask import Flask, request, render_template, redirect, url_for, flash
import requests
from bs4 import BeautifulSoup
import os
import pymongo

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessary for flash messages

# Directory to save images
save_dir = "static/images/"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# MongoDB setup (uncomment if using MongoDB)
# client = pymongo.MongoClient("mongodb+srv://pwskills:pwskills@cluster0.vwmjzqx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# mydb = client["image_scrapper"]
# mycoll = mydb["data"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    query = request.form['query']
    if not query:
        flash("Please enter a query.", "error")
        return redirect(url_for('index'))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    response = requests.get(
        f"https://www.google.com/search?sca_esv=7b1f93cccdc9738a&sca_upv=1&sxsrf=ADLYWIIHlRHp1swj9-lBVYCp6e4mK7WfTw:1716829248425&q={query}&uds=ADvngMhKBgPYoDMPCXzTfPsZm7Znj9xqGpU273-zZq-afJ1Ym8W8B7GMwffAvqnYFys143pxRDqaQIhImglGm6hPnW8FxrBCZEjCmL4K4toT1HSf1oDJp9-xP3KUS-_nUegj6wiSr8QU-142Xw9RqXFcbxbloN8sIktY-B-ArYImeigCmp1rZtUSgRWIam8PUr4Vsr4ZbSPUMQiPY4awjEBzqmD4Z39PrCE_A5G6C4ceB52UjlSWMD9XoaQtiyadwRKINFEsm5zAl6R0wQI6iojZgJlRBrQEcYsKMU9hPA2KiJrcOkHEE248ERYJwOdB-pgNMUGSUTeL&udm=2&prmd=ivnsmbtz&sa=X&ved=2ahUKEwja7_erp66GAxUnXGwGHbjCCT0QtKgLegQIFhAB&biw=1366&bih=599&dpr=1",
        headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    images_tags = soup.find_all("img")
    img_data_mongo = []

    for index, i in enumerate(images_tags[1:]):  # Skip the first image tag
        image_url = i.get("src")
        if image_url:
            try:
                image_data = requests.get(image_url).content
                img_path = os.path.join(save_dir, f"{query}_{index}.jpg")
                with open(img_path, "wb") as f:
                    f.write(image_data)
                img_data_mongo.append({"index": image_url, "image_path": img_path})
            except Exception as e:
                print(f"Could not download {image_url}: {e}")

    # Uncomment if using MongoDB
    # if img_data_mongo:
    #     mycoll.insert_many(img_data_mongo)

    return render_template('results.html', images=img_data_mongo, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
