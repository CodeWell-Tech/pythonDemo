# pictureDownload
图片下载器。

## 运行
1. 安装依赖
    ```
    pip install requests
    ```
2. 运行
    ```
    python ./main.py
    ```

## 说明
- 由于百度的限制，每次请求最多返回`60`张图片显示。
- `quality`参数对应到`GET`请求中的`z`字段。