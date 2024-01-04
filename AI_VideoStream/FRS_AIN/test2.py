import sys
from flask import Flask

app = Flask(__name__)


# @app.route("/")     # This 
# def hello():
#     return "Hello, World!"


# def hello():      # and This is equal
#     return "Hello, World!"
# app.add_url_rule('/', 'hello', hello)


def create_app(arg1, arg2):
    """Create and configure an instance of the Flask application."""

    print(arg1)  
    print(arg2)

    def hello():
        return "Hello, World!"

    app.add_url_rule('/', 'hello', hello)
    return app


# flask --app test2 --debug run
# flask --app 'test2.py:create_app("Hammad", 5)' run
# flask --app 'test2.py:create_app("Hammad", 5)' --debug run  # (for Debug True)


# gunicorn --bind 0.0.0.0:5000 test2:app
# gunicorn test2:create_app'("Hammad", 1)'
# gunicorn 'test2:create_app("H",1)'


# running code with flask api (tested)
# def create_app(arg1):
#     print(arg1)

#     model = ZeroShotApp(arg1)

#     @app.route("/",methods=['POST'])
#     def cat():
#         if request.method == "POST":    
#             target_text = request.json["text"]
#             platform = request.json["platform"] 
#             print(target_text, platform)

#             if type(target_text) != str:
#                 logger.error("(target_text -> %s) , Error 400:Bad Input",target_text)
#                 return "Error 400: Bad Input",400

#             elif type(platform) != str:
#                 logger.error("(target_text -> %s) , Error 400:Bad Input",platform)
#                 return "Error 400: Bad Input",400
         
#             else:
#                 return model.predict(target_text,platform)
#         else:
#             logger.error("Error 405: Method Not Allowed")
#             return "Error 405: Method Not Allowed", 405
    
#     # app.add_url_rule('/', 'cat', cat)
#     return app

# # if __name__ == "__main__":
# #     app.run(debug=True)