# SJTU EE208
import traceback
import uuid

import cv2
from flask import Flask, redirect, render_template, request, url_for
import os

app = Flask(__name__)
import search as SearchFiles


# 页面
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    # 获取前端参数
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'relevance')
    
    use_date_sort = False
    if sort_by == 'time':
        use_date_sort = True

    # 从数据库中查询数据
    finances = SearchFiles.search_database('finance', search,use_date_sort)

    # 返回查询结果
    result = []
    for i in finances:
        result.append({
            'url': i[0],
            'title': i[1],
            'content': i[2]
        })

    return render_template("about.html", result=result)


@app.route('/service')
def service():
    # 获取前端参数
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'relevance')
    
    use_date_sort = False
    if sort_by == 'time':
        use_date_sort = True

    # 从数据库中查询数据
    finances = SearchFiles.search_database('sports', search,use_date_sort)

    # 返回查询结果
    result = []
    for i in finances:
        result.append({
            'url': i[0],
            'title': i[1],
            'content': i[2]
        })
    return render_template("service.html", result=result)


@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    if request.method == 'GET':
        return render_template("portfolio.html")
    else:
        try:
            # 获取图片
            img = request.files.get('file')

            result = []
            if img:
                # 保存视频
                img_name = 'static/upload/' + str(uuid.uuid4()) + '_' + img.filename
                img.save(img_name)
                img0 = cv2.imread(img_name)
                r = SearchFiles.search_photos(img0)
                for i in r:
                    result.append({
                        'url': i[0],
                        'title': i[1],
                        'content': i[2]
                    })

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            # 捕获到异常
            return render_template("portfolio.html", result=[])

        else:
            # 正常返回
            return render_template("portfolio.html", result=result)


@app.route('/game')
def game():
    return render_template("game.html")


@app.route('/snake')
def snake():
    return render_template("snake.html")


@app.route('/jump')
def jump():
    return render_template("jump.html")


if __name__ == '__main__':
    app.run(debug=True, port=11451)
