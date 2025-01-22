from flask import Flask, request, jsonify
import requests
import pandas as pd


app = Flask(__name__)

 
def verify_dataframe(url):
    try:
        response = requests.get(url)

        if response.status_code != 200:
            return False, f"Error: Received status code {response.status_code}"

        try:
            data = response.json()
            df = pd.DataFrame(data)
            return True, df

        except Exception as e:
            return False, f"Error: Unable to parse data into DataFrame. {str(e)}"

    except Exception as e:
        return False, f"Request Error: {str(e)}"


@app.route('/verify_dataset', methods=['GET'])
def verify_dataset():
    dataset_url = request.args.get('url')

    if not dataset_url:
        return jsonify({"error": "URL parameter is required"}), 400

    success, result = verify_dataframe(dataset_url)

    if success:
        return jsonify(
            {
                "message": "Data successfully parsed into DataFrame",
                "columns": result.columns.tolist(),
                "rows": result.shape[0]
            })
    else:
        return jsonify({"error": result}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5001)
