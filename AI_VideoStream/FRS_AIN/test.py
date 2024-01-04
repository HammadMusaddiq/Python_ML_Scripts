from flask import Flask
from flask import request
from ftp_stream import Ftp_Stream

app = Flask('AIN-FRS')

ftp_class = Ftp_Stream()
base_url = ftp_class.getBaseURL()
ftp_cursor = ftp_class.getFTP()

def imageToFTP(path, file_name, image_bytes):
    import pdb; pdb.set_trace()

    if not ftp_class.is_connected():
        ftp_class.retry_ftp_connection()
        ftp_class.change_ftp_present_working_dir(path)
    else:
        ftp_class.change_ftp_present_working_dir(path)
    
    try:
        baseurl = base_url # ('str' object has no attribute 'copy')

        for p in path.split('/')[1:]:
            baseurl = baseurl + str(p) + "/"
        
        ftp_file_url = baseurl + file_name
        
        ftp_cursor.storbinary("STOR " + file_name , image_bytes)
        # ftp_cursor.quit()
        return ftp_file_url

    except Exception as E:
        print(E)
        return False

@app.route("/insert",methods=['POST'])
def insert_embeddings():
    if request.method == "POST":
        try:
            image = request.files['image_path']
            person_name = request.form['person_name']

            try:
                import pdb; pdb.set_trace()
                imageToFTP("/AI_Video_Analytics/Image_Upload/Images", "imran_test.jpg", image)
                

            except Exception as E:
                error = "An Exception Occured: {}".format(E)
                return error,500
            
        except:
            return "Error 400: Bad Input", 400
                
    else:
        error = "Error 405: Method Not Allowed"
        return error, 405

if __name__ == "__main__":
    app.run(debug=True)
