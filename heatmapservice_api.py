from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import json
from sqlalchemy import create_engine, text
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)


def polygonfilter(df, polyp):
    df['point'] = df.apply(lambda row: Point(row['x'], row['y']), axis=1)
    polygon = Polygon(polyp)
    df_1 = df[df['point'].apply(polygon.contains)].copy()
    ids = set(df_1['id'].to_list())
    df_f = df.loc[df['id'].isin(ids)]
    df2 = df_f.copy()
    data = df2.drop(['id', 'point'], axis=1).to_numpy()
    l = ["{ x: "+str(i[0])+", y: "+str(i[1]) +
         ",value: 0.8 }" for i in data.tolist()]
    out = "[ "+",".join(l)+" ]"
    return out


def get_random_data():
    data = np.random.randint(low=0, high=[720, 480, 20], size=[400, 3])
    df = pd.DataFrame(data, columns=['x', 'y', 'id'])
    return df


def get_db(dbname='POS', user="postgres", password='dummy', host='localhost', port=5432, date=None, stime=None, etime=None):
    engine = create_engine(
        'postgresql://{}:{}@{}:{}/{}'.format(user, password, host, port, dbname))
    txt = '"Heatmapstore"'
    with engine.connect() as conn:
        query = text(
            'SELECT * FROM public.{} WHERE date = {} AND time >= {} AND time <= {}'.format(txt, date, stime, etime))
        df = pd.read_sql_query(query, conn)
    return df


def get_data():
    df2 = pd.read_csv("testdata.csv")
    df = pd.DataFrame()
    df['x'] = df2['X']
    df['y'] = df2['Y']
    df['id'] = df2['Object id']
    return df


@app.route('/api/heatmaps')
@cross_origin(origins='*')
# @cross_origin(origins='http://localhost:3002')
def data_retiver():
    data = request.args.get('polygon')
    # data = json.loads(data)
    date = request.args.get('date')
    stime = json.loads(request.args.get('stime'))
    etime = json.loads(request.args.get('etime'))
    # out = polygonfilter(get_db(date, stime, etime), data)
    print('data recieved', date, data, stime, etime)
    jsonreturn = jsonify(
        {'polygon_coords': data, 'date': date, 'start_time': stime, 'end_time': etime})
    print(jsonreturn)
    return jsonreturn


if __name__ == "__main__":
    app.run(host="localhost", debug=True)
