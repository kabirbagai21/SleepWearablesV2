from website import create_app
#from waitress import serve

app = create_app()

if __name__ == '__main__':
    #serve(app, host = '172.16.1.151', port=5000)
    app.run(debug=True)
