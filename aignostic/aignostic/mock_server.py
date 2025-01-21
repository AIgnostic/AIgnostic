from flask import Flask, jsonify
from folktables import ACSDataSource
from pydantic import BaseModel, ValidationError
from typing import List, Dict


class DataSet(BaseModel):
    data: List[Dict]


app = Flask(__name__)


# Fetch ACS data from Alabama in 2018 using Folktables
data_source = ACSDataSource(survey_year="2018", horizon="1-Year", survey="person")
acs_data = data_source.get_data(states=["AL"], download=True)


# Takes 30 seconds to run
@app.route('/acs-dataframe', methods=['GET'])
def get_dataframe():
    try:
        # Convert DataFrame to a list of dictionaries (one dictionary per row)
        acs_dict = acs_data.iloc[0].to_dict()

        return jsonify({'datapoint': acs_dict})

    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route('/invalid-data', methods=['GET'])
def get_invalid_data():
    invalid_data = "This is not a valid JSON or tabular data"
    return jsonify({"error": "Invalid data format. Cannot be parsed into DataFrame.", "data": invalid_data}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
