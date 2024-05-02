from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from joblib import dump

import jieba
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import urllib.request
from bs4 import BeautifulSoup
import jieba

# 加载停用词列表
with open('stopwords.txt', 'r', encoding='utf-8') as f:
    stopwords = set([w.strip() for w in f.readlines()])

# 初始化TF-IDF向量化器
# 假设这是您用于模型训练的相同向量化器
tfidf_vectorizer = TfidfVectorizer()


def preprocess_content(content):
    # 清洗文本
    content = re.sub(r'[^\u4e00-\u9fa5]', '', content)

    # 分词
    words = jieba.cut(content)

    # 去除停用词
    filtered_words = [word for word in words if word not in stopwords]

    # 返回处理后的文本
    return ' '.join(filtered_words)


def get_page(page):
    try:
        req = urllib.request.Request(page)
        req.add_header('User-Agent', "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0")
        content = urllib.request.urlopen(req).read()
        
        with open('temp.txt', 'wb') as file:
            file.write(content)
        
        with open('temp.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        
        return content
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

urls = ["https://finance.sina.com.cn/",
        "https://finance.sina.com.cn/stock/marketresearch/2023-12-07/doc-imzxcsie9690240.shtml",
        "https://finance.sina.com.cn/zt_d/subject-1701908780/",
        "https://finance.sina.com.cn/jjxw/2023-12-07/doc-imzxeiey1657042.shtml",
        "https://finance.sina.com.cn/stock/usstock/c/2023-12-07/doc-imzxcwre1821731.shtml",
        "https://finance.sina.com.cn/jjxw/2023-12-06/doc-imzxavct9117540.shtml",
        "https://finance.sina.com.cn/tech/internet/2023-12-07/doc-imzxcftp8912045.shtml",
        "https://finance.sina.com.cn/jjxw/2023-12-07/doc-imzxcftn2133792.shtml",
        "https://sports.sina.com.cn/",
        "https://sports.sina.com.cn/basketball/nba/2023-12-07/doc-imzxeiez8445189.shtml",
        "https://sports.sina.com.cn/basketball/nba/2023-12-07/doc-imzxeieu4864900.shtml",
        "https://sports.sina.com.cn/basketball/cba/2023-12-06/doc-imzxavcr0151611.shtml",
        "https://sports.sina.com.cn/others/volleyball/2023-12-07/doc-imzxcwrf8588915.shtml",
        "https://sports.sina.com.cn/g/pl/2023-12-07/doc-imzxcwra9582584.shtml",
        "https://sports.sina.com.cn/g/pl/2023-12-07/doc-imzxcwre1814664.shtml",
        "https://sports.sina.com.cn/g/pl/2023-12-07/doc-imzxcwra9586902.shtml",
        "https://sports.sina.com.cn/china/afccl/2023-12-06/doc-imzxavcn5598849.shtml",
        "https://auto.sina.com.cn/",
        "https://db.auto.sina.com.cn/5227/?c=spr_auto_trackid_9237989dda2d0373",
        "https://ent.sina.com.cn/",
        "http://slide.ent.sina.com.cn/star/slide_4_704_389586.html",
        "https://tech.sina.com.cn/",
        "https://finance.sina.com.cn/tech/2023-12-07/doc-imzxcwre1824844.shtml",
        "https://blog.sina.com.cn/s/blog_4d94c2b70102z9jm.html"]
data=[]
labels = []
for url in urls:
    content = get_page(url)
    processed_content = preprocess_content(content)
    print(processed_content)
    data.append(processed_content)
    label = input("请输入这段内容的标签: ")
    labels.append(str( label))

# 分割数据集
X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2)

# 创建一个管道，包括TF-IDF向量化和朴素贝叶斯分类器
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

# 训练模型
model.fit(X_train, y_train)

# 评估模型
predictions = model.predict(X_test)
print(classification_report(y_test, predictions))

# 假设 'model' 是您的训练好的模型
dump(model, 'model.joblib')