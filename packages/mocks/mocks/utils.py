import pickle
import os


def load_scikit_model():
    """
    Load the mocke scikit-learn model from the pickle file
    """
    model = pickle.load(
        open(
            os.path.join(
                os.path.dirname(__file__),
                '../scikit_model.sav'
            ),
            'rb'
        )
    )
    return model
