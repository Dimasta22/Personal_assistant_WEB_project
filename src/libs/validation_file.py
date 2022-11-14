ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'txt', 'doc', 'docx', 'pdf',
                      'mp4', '3gp', 'avi', 'mkv', 'mp3', 'wav', 'ogg', 'flac', 'm4a'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
