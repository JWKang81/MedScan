from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True 在開發環境下會自動偵測程式碼變更並重啟
    app.run(host='0.0.0.0', port=3000, debug=True)


