import pickle
import os


def load_scikit_model(name: str):
    """
    Load the mocke scikit-learn model from the pickle file
    """
    model = pickle.load(
        open(
            os.path.join(
                os.path.dirname(__file__),
                f'../{name}'
            ),
            'rb'
        )
    )
    return model
