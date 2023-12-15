import numpy as np
from flask import Flask, jsonify
from sqlalchemy import create_engine, func, Column, Integer, String, Float, Date, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, declarative_base
import pandas as pd

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.db")

Base = declarative_base()

class Measurement(Base):
    __tablename__ = 'measurement'
    id = Column(Integer, primary_key=True)
    station = Column(String)
    date = Column(Date)
    prcp = Column(Float)
    tobs = Column(Integer)

class Station(Base):
    __tablename__ = 'station'
    id = Column(Integer, primary_key=True)
    station = Column(String)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)

Base.metadata.create_all(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    latest_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = pd.to_datetime(latest_date) - pd.DateOffset(years=1)

    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago)\
        .filter(Measurement.date <= latest_date)\
        .all()

    session.close()

    precipitation_df = pd.DataFrame(precipitation_data, columns=['Date', 'Precipitation'])
    precipitation_df.set_index('Date', inplace=True)

    return jsonify(precipitation_df.to_dict(orient='index'))

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    station_data = session.query(Station.station, Station.name).all()

    session.close()

    station_list = [{'Station': station, 'Name': name} for station, name in station_data]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]

    tobs_data = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago)\
        .filter(Measurement.date <= latest_date)\
        .all()

    session.close()

    tobs_list = [{'Date': date, 'Temperature': tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)

if __name__ == '__main__':
    app.run(debug=True)
