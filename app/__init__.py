import os  
from datetime import datetime

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, url_for, render_template, request, flash, send_file, redirect

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy()
db.init_app(app)
db.app = app

from app.models.dl_models import DL_Model
from app.views.dl_models import DLModelsForm

from app.utils.table_utils import GetTableHeader, getTableRecords, initTableRecords
from app.utils.download_utils import getFullPath
from app.utils.models_utils import save_model_h5

# ####################################################################################################
#
#                                           MAIN PAGE CONTROLLER
#
# ####################################################################################################
@app.route("/")
def index():
    return render_template("index.html")



# ####################################################################################################
#
#                                          MODEL PAGE CONTROLLER
#
# ####################################################################################################
@app.route("/models", methods=["GET", "POST"])
def models():
    # define initial variable
    page, per_page, table_search, search_key, _col, _type, sort_type = initTableRecords()

    # Create Table Record
    filters = ['name', 'file_name']
    tableRecords, min_page, max_page, count = getTableRecords(DL_Model, search_key, filters, sort_type, _col, page, per_page)

    # Create Table Header
    col_exclude = ['file_type']
    sort_exclude = ['id', 'is_used']
    overide_label = dict(
        id = 'No'
    )
    tableHeader = GetTableHeader(DL_Model, col_exclude, sort_exclude, overide_label)

    # Create Header Control
    headerCtrl = dict(
        name = 'Model',
        is_search = True,
        search_act = 'models',
        table_search = table_search,
        is_export = False,
        export_act = 'models_download',
        export_filename = 'Export - Model.csv',
        sort_act = 'models',
        delete_act = 'model_delete',
        detail_act = 'model_detail',
        is_add_new = True
    )

    # Create Footer Control
    footerCtrl = dict(
        min_page=min_page, 
        max_page=max_page, 
        count=count,
        _type=_type,
        _col=_col,
        pagination_act = 'models'
    )
    return render_template("models.html", 
                        tableRecords=tableRecords, 
                        tableHeader=tableHeader,
                        headerCtrl=headerCtrl,
                        footerCtrl=footerCtrl
                    )

@app.route("/models/download/<filename>")
def models_download( filename):
    model_path = getFullPath(filename, 'static/csv-download')
    return send_file(model_path, 
                    attachment_filename=filename, 
                    as_attachment=True, 
                    mimetype='application/octet-stream')

@app.route("/model/detail/<int:_id>", methods=["GET", "POST"])
def model_detail( _id):
    form = DLModelsForm()
    getDLModelById = DL_Model.query.get(_id)
    
    model_name = 'model.h5' # default model name

    # Update record
    if form.is_submitted() and getDLModelById:
        if form.file_model.data.filename != "" :
            file_model = form.file_model.data
            model_file_name = save_model_h5(file_model, form.name.data + ".h5")
            model_name = model_file_name
            getDLModelById.file_name = model_file_name
        getDLModelById.name = form.name.data
        getDLModelById.upload_by = "Admin"
        getDLModelById.is_used = form.is_used.data
        db.session.commit()
        flash('Model ' + getDLModelById.name + ' has been uploaded!', 'success')
        return redirect(url_for('models'))
    
    # Add new record
    if form.is_submitted() and form.validate_on_submit():
        file_model = form.file_model.data
        model_file_name = save_model_h5(file_model, form.name.data + ".h5")
        model_name = model_file_name
        dl_model = DL_Model(
            name = form.name.data,
            file_name = model_file_name,
            upload_by = "Admin",
            is_used = form.is_used.data
        )
        db.session.add(dl_model)
        db.session.commit()
        flash('Model ' + dl_model.name + ' has been uploaded!', 'success')
        return redirect(url_for('models'))

    elif request.method == 'GET' and getDLModelById:
        form.name.data = getDLModelById.name
        form.is_used.data = getDLModelById.is_used
        model_name = getDLModelById.file_name

    inputField = ['name', 'is_used', 'file_model']
    submitField = ['submit']
    indexField = ['id']

    formCtrl = dict(
        _id=_id,
        inputField = inputField,
        submitField = submitField,
        indexField=indexField,
        form_act = "model_detail",
        cancel_act = "models",
        download_act = "model_download",
        download_name = model_name,
        delete_act = "model_delete",
        form_name = 'Model Form', 
        is_multipart = True
    )
    return render_template("model_detail.html",
                        form=form,
                        formCtrl=formCtrl)

@app.route("/model/download/<filename>")
def model_download( filename):
    model_path = getFullPath(filename, 'static/model-upload')
    return send_file(model_path, 
                    attachment_filename=filename, 
                    as_attachment=True, 
                    mimetype='application/octet-stream')

@app.route("/model/delete/<int:_id>")
def model_delete( _id):
    getDLModelById = DL_Model.query.get(_id)
    db.session.delete(getDLModelById)
    db.session.commit()
    flash('Model ' + getDLModelById.name + ' has been deleted!', 'success')
    return redirect(url_for('models'))


# ####################################################################################################
#
#                                          ABOUT PAGE CONTROLLER
#
# ####################################################################################################
@app.route("/about")
def about():
    return render_template("about.html")





# ####################################################################################################
#
#                                          INITIALIZATION
#
# ####################################################################################################

# @app.cli.command()
def build_sample_db():
    """
    Populate a small db with some example entries.
    """
    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        db.session.commit()
    return