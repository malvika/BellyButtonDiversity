# Flask (Server)
from flask import Flask, jsonify, render_template, request, flash, redirect

# Sql Alchemy (ORM)
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import exc

# Various
import datetime as dt
from random import *
import json
import sys

# Dependencies
import os
import pandas as pd
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("belly_button_biodiversity.sqlite")

# Reflect DB Contents using SQL ALchemy
Base = automap_base()
Base.prepare(engine, reflect=True)

# Store each table as a class
otu_table = Base.classes.otu
samples_table = Base.classes.samples
metadata_table = Base.classes.samples_metadata

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes (Web)
#################################################
session = Session(engine)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/names")
def names():

    stmt = session.query(samples_table).statement
    df = pd.read_sql_query(stmt, session.bind)
    df.set_index('otu_id', inplace=True)

    return jsonify(list(df.columns))

@app.route("/otu")
def otu():

    results = session.query(otu_table).lowest_taxonomic_unit_found.all()

    otu_list = list(np.ravel(results))

    return jsonify(otu_list)
    # results = results.all()

    # all_results =[]
    # for result in results:
    #     new ={}

    #     new["otu_id"]=result.otu_id
    #     new["lowest_taxonomic_unit_found"]= result.lowest_taxonomic_unit_found

    #     all_results.append(new)

    # return jsonify(all_results)

@app.route('/metadata/<sample>')
def sample_metadata(sample):
    results = session.query(metadata_table.SAMPLEID, metadata_table.ETHNICITY,metadata_table.GENDER, metadata_table.AGE, metadata_table.LOCATION, metadata_table.BBTYPE).\
        filter(metadata_table.SAMPLEID == sample[3:]).all()
    new_meta = {}
    for result in results:
        new_meta['SAMPLEID'] = result[0]
        new_meta['ETHNICITY'] = result[1]
        new_meta['GENDER'] = result[2]
        new_meta['AGE'] = result[3]
        new_meta['LOCATION'] = result[4]
        new_meta['BBTYPE'] = result[5]

    return jsonify(new_meta)

@app.route('/wfreq/<sample>')
def wfreq(sample):
    results = session.query(metadata_table.WFREQ).\
        filter(metadata_table.SAMPLEID == sample[3:]).all()
    wfreq = np.ravel(results)
    return jsonify(wfreq)

@app.route('/samples/<sample>')
def samples(sample):
    statement = session.query(samples_table).statement
    df = pd.read_sql_query(statement, session.bind)

    df = df[df[sample] > 1]

    df = df.sort_values(by=sample, ascending=0)[:10]

    data_dict = [{
        "otu_ids": df[sample].index.values.tolist(),
        "sample_values": df[sample].values.tolist()
    }]

    return jsonify(data_dict)
if __name__ == "__main__":
    app.run(debug=True)
