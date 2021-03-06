from flask import render_template, request, redirect, flash
from app import app
from werkzeug.utils import secure_filename
from prediction_api import get_prediction
import os
import cv2
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def submit_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # im =np.array(cv2.imread(filename), dtype=float)
            # plt.imshow(im)
            label, acc = get_prediction(filename)
            flash(label)
            flash(acc)
            flash(filename)
            return redirect('/')


@app.route('/takepic', methods=['POST'])
def submit_shoot():
    filename = take_pic()

    if filename:
        label, acc = get_prediction(filename)
        flash(label)
        flash(acc)
        flash(filename)
        return redirect('/')

    else:
        return redirect('/')


def take_pic():
    cam = cv2.VideoCapture(0)

    # cv2.namedWindow("Hit Space-Bar to take a bird's picture!")

    img_counter = len(os.listdir(app.config['UPLOAD_FOLDER']))
    img_name = None

    while True:

        ret, frame = cam.read()

        if not ret:
            print("Failed to grab a frame")
            break

        cv2.imshow("Hit Space-Bar to take a bird's picture!", frame)
        k = cv2.waitKey(1)

        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing camera!")
            break

        elif k % 256 == 32:
            # SPACE pressed
            img_name = f"bird_img_{img_counter}.png"
            cv2.imwrite(app.config['UPLOAD_FOLDER']+'/'+img_name, frame)
            print(f"{img_name} written!")

            break
    cv2.destroyAllWindows()
    cam.release()
    return img_name


if __name__ == "__main__":
    app.run()
