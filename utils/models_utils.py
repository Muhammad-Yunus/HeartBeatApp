import os


def save_model_h5(file_model, name):
        model_fn = name.lower().replace(" ", "_")
        root_path = os.path.dirname(os.path.dirname(__file__))
        full_path = os.path.join(root_path, 'static/model-upload', model_fn)

        file_model.save(full_path)
        return model_fn