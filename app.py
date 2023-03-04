import numpy as np
import os
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect,func
import pandas as pd
import datetime as dt
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

#weather app
app = Flask(__name__)

engine.execute('SELECT * FROM measurement LIMIT 5').fetchall()

# inspector = inspect(engine)
# columns = inspector.get_columns('measurement')
# for c in columns:
#     print(c['name'], c["type"])

recent_date = session.query(func.max(measurement.date)).all()[0][0]
start_datest= datetime.strptime(recent_date, '%Y-%m-%d')
start_datest
start_date= start_datest - relativedelta(months =12)
#print(start_date)

# Design a query to retrieve the last 12 months of precipitation data and plot the results. 
# Perform a query to retrieve the data and precipitation scores
result_12months = session.query(measurement.date, measurement.prcp).filter(measurement.date>=start_date).all()

# Design a query to find the most active stations (i.e. what stations have the most rows?)
# List the stations and the counts in descending order.
results_Stations = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
#print(results_Stations)

# Using the most active station id
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
result_mostactive = session.query(measurement.date, measurement.prcp).filter(measurement.date>=start_date,measurement.station == "USC00519281").all()

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available Hawai Climate API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end>"
     )
@app.route("/api/v1.0/precipitaton")   

def precipitation():
    result_12months2 = session.query(measurement.date, measurement.prcp).filter(measurement.date>=start_date).all()

    precipData = []
    for result in result_12months2:
        precipDict = {result.date: result.prcp, "Station": result.station}
        precipData.append(precipDict)

    precipData_list=list(np.ravel(precipData))

    return jsonify(precipData_list)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    result_mostactive2 = session.query(measurement.date, measurement.prcp).filter(measurement.date>=start_date,measurement.station == "USC00519281").all()
    temp = []
    for result in result_mostactive2:
        tempDict = {result.date: result.prcp, "Station": result.station}
        temp.append(tempDict)

    templist=list(np.ravel(temp))

    return jsonify(templist)


if __name__ == '__main__':
    app.run(debug=True)    
