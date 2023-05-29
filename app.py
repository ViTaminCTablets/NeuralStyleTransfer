from flask import Flask, render_template, request
import os
import subprocess

app = Flask(__name__, template_folder='templates')
#app.jinja_loader = FileSystemLoader(['D:\work\workspace\新建文件夹\Fast-Neural-Style-Transfer', 'D:\work\workspace\新建文件夹\Fast-Neural-Style-Transfer\index.html'])
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image = request.files.get('image')
        video = request.files.get('video')
        model = request.form.get('model')
        if image or video:
            
            if image:
                image_path = os.path.join('images/content', image.filename)
                image.save(image_path)
                output_filename = 'stylized-' + image.filename
                command = f'python test_on_image.py --image_path {image_path} --checkpoint_model {model}'
                os.system(command)
                styled_image = '/' + output_filename
                return render_template('index.html', image=styled_image)
            else:
                video_path = os.path.join('images/content', video.filename)
                video.save(video_path)
                output_filename = 'stylized-' + os.path.splitext(video.filename)[0] + '.gif'
                print(output_filename)
                command = f'python test_on_video.py --video_path "{video_path}" --checkpoint_model {model}'
                subprocess.run(command, shell=True)
                styled_gif = '/' + output_filename
                return render_template('index.html', gif=styled_gif)

                
    return render_template('index.html')

if __name__ == '__main__':
    app.run()