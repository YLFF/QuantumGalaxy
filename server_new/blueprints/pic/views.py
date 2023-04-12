from . import pic
from flask import redirect,render_template,make_response,request,jsonify,session,Response
from .models import *
import os
@pic.route('/example')
def example():
    return render_template('example.html')
@pic.route('/test')
def test():
    file_token='bascnzsAjUXwr4gUkaIpqi8BBaf'
    table_token='tbl0Ko7cxJaGwUnh'
    record_id="recV96vgmB"
    file_dir,file_name=find_file(file_token,record_id)
    if file_name:
        out=os.path.join(file_dir,file_name)
        fsize = os.path.getsize(out)

        def send_file_fp():
            store_path = out
            send_size = 0
            with open(store_path, "rb") as target_file:
                while 1:
                    data = target_file.read(2 * 1024 * 1024)  # 每次读取2M
                    if not data:
                        break
                    yield data
        #content_type='multipart/form-data; boundary=something'
        content_type='image/'+out.split('.')[1]
        response = Response(send_file_fp(),content_type=content_type )
        response.headers["Content-disposition"] = 'attachment; filename={}'.format(file_name)
        response.headers["Content-length"] = fsize
        return response
    else :return None
@pic.route('/get_pic')
def get_pic():
    file_token=request.args.get('file_token','bascnzsAjUXwr4gUkaIpqi8BBaf')
    table_token='tbl0Ko7cxJaGwUnh'
    record_id=request.args.get('record_id',"recV96vgmB")
    try:
        file_dir,file_name=find_file(file_token,record_id)
    except:
        return jsonify(code=-1,msg='找不到路径，确认filetoken是否正确')
    if file_name:
        out=os.path.join(file_dir,file_name)
        fsize = os.path.getsize(out)

        def send_file_fp():
            store_path = out
            send_size = 0
            with open(store_path, "rb") as target_file:
                while 1:
                    data = target_file.read(2 * 1024 * 1024)  # 每次读取2M
                    if not data:
                        break
                    yield data
        #content_type='multipart/form-data; boundary=something'
        content_type='image/'+out.split('.')[1]
        response = Response(send_file_fp(),content_type=content_type )
        response.headers["Content-disposition"] = 'attachment; filename={}'.format(file_name)
        response.headers["Content-length"] = fsize
        return response
    else :return jsonify(code=-2,msg='找不到文件，确认recordid是否正确')
