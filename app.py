from flask import Flask, render_template, request
import pandas as pd
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    n_recc = request.form['No.of Recommendations']
    ind_type = request.form['Industry']


    df = pd.read_csv("data.csv")

    llm = OpenAI(api_token="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")
    pandas_ai = PandasAI(llm, verbose=True)
    response = pandas_ai(df, f"give me {n_recc} companies from {ind_type} Industry from the above dataframe")
   
    print(response)
    return render_template('result.html', prediction=response.to_dict())

if __name__ == '__main__':
    app.run()
