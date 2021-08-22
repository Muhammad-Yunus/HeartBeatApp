from . import np 
from . import pd  
from . import os
from . import load_model


class Detection():
    def __init__(self, feature_label_list, fs = 250, sample_size = 6, pad_size = 15, label_name = ['AF', 'N'], path="static\model-upload"):
        self.fs = fs
        self.sample_size = sample_size
        self.label_name = label_name
        self.pad_size = pad_size
        self.prediction_proba = []
        self.prediction_label = []
        self.models = {}

        for feature_label in feature_label_list :
            filename = "%s_model.h5" % feature_label
            root_path = os.path.dirname(os.path.dirname(__file__))
            if not os.path.exists(os.path.join(root_path, path, filename)):
                raise Exception('\n\n[ERROR] Cant find %s in %s, please upload your classification model for feature %s with name `%s`!\n\n' % (filename, path, feature_label, filename))

            print("\n\n[INFO] Load classification model %s...\n\n" % filename)
            self.models[feature_label] = load_model(os.path.join(root_path, path, filename))

    def transform(self, X, feature_label):
        print("[INFO] transforming data using model %s_model.h5..." % feature_label)
        y_pred = self.models[feature_label].predict(X)
        print("[INFO] find label & probability result...")
        prediction_index = y_pred.argmax(axis=1)
        self.prediction_proba = y_pred.max(axis=1)
        self.prediction_label = [ self.label_name[idx] for idx in prediction_index]

