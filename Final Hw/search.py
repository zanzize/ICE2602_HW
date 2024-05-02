import matplotlib
matplotlib.use('Agg')

import os
import sqlite3

import cv2
import numpy as np
from matplotlib import pyplot as plt


def search_database(label, keyword='', use_date_sort=False, min_relevance=2):
    if keyword == '':
        return []
    
    try:
        connection = sqlite3.connect('crawled_data.db')
        cursor = connection.cursor()

        # 根据标签选择正确的表
        if label == "sports":
            table = "sports_pages"
        elif label == "finance":
            table = "finance_pages"
        else:
            print("Invalid label")
            return

        if use_date_sort:
            order_by = "published_date DESC"
        else:
            # 示例的相关性排序方式（简化版）
            order_by = f"(CASE WHEN title LIKE '%{keyword}%' THEN 1 ELSE 0 END + CASE WHEN content LIKE '%{keyword}%' THEN 1 ELSE 0 END) DESC"

        # 构造SQL查询语句
        query = f'''SELECT DISTINCT url, title, content FROM {table} 
                    WHERE (CASE WHEN title LIKE '%{keyword}%' THEN 1 ELSE 0 END+ 
                          CASE WHEN content LIKE '%{keyword}%' THEN 1 ELSE 0 END) >= {min_relevance}
                    ORDER BY {order_by}
                    LIMIT 50'''

        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()

        return results

    except Exception as e:
        print(f"Error in search_database: {str(e)}")


# 使用示例
#connection = sqlite3.connect('crawled_data.db')
#search_database("sports", "篮球")

# new add
def decode_photo(conn, id):
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM images WHERE id = ?", (id,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        # 解码图像数据
        image_data = np.frombuffer(result[0], dtype=np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.savefig('result.jpg')
    else:
        print("No image found with the given ID")


def compair(image0):
    ## 图片格式转换
    img1 = cv2.imread('result.jpg')
    # 删除result.jpg

    ##sift算子计算匹配点个数
    sift = cv2.SIFT_create()
    keypoints_0, descriptors_0 = sift.detectAndCompute(image0, None)
    keypoints_1, descriptors_1 = sift.detectAndCompute(img1, None)

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptors_0, descriptors_1, k=2)

    good_matches = []

    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    os.remove('result.jpg')

    # 返回匹配点的数量
    return len(good_matches)


def output(conn, img0):
    img_list = []

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM images")
    num_images = cursor.fetchone()[0]

    for i in range(1, num_images + 1):
        # print(i)
        decode_photo(conn, i)
        result = compair(img0)
        if (result > 2):
            img_list.append(i)
    # print(img_list)
    return img_list


def getname(conn, id):
    # 实现从数据库中由id获取name
    try:
        cursor = conn.cursor()
        # Perform a SELECT query to get the name for the given id
        cursor.execute("SELECT name FROM images WHERE id = ?", (id,))
        # Fetch the result
        result = cursor.fetchone()
        if result:
            # print(result)
            return result[0].replace('.jpg', '')  # Return the name
        else:
            return None  # No result found for the given id
    except Exception as e:
        print(f"Error in getname: {str(e)}")
        return None
    finally:
        if cursor:
            cursor.close()


def search_photos(img0):
    conn = sqlite3.connect('crawled_data.db')
    result_list = output(conn, img0)
    result = []
    count = 0
    for i in result_list:
        if count >= 3:  
            break
        name = getname(conn, i)
        r = search_database("sports", name, True)
        for j in r:
            result.append(j)
        count += 1
    return result
