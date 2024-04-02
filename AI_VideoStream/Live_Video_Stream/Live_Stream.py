import Generate_Frames
import boxPlot
from flask import Flask, Response

frame_gen = Generate_Frames.Generate_frames()
plot = boxPlot.Plot()

app = Flask(__name__)

@app.route('/vid')
def vid():
    return Response(frame_gen.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
