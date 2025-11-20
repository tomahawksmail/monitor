#####################################################
    ### Designed by Maksym Tsybulskyi, 2025 ###
#####################################################

from server import app

host = '0.0.0.0'
port = 5566

# run the app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host=host, port=port)
