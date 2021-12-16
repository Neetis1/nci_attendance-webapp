import React, { Component } from "react";
import axios from "axios";
import apiJson from './apiUrl.json'
import KPI from './components/KPI'
import BarChart from './components/BarChart'
import LineChart from './components/LineChart'
import {API} from 'aws-amplify'

export default class Analytics extends Component {

    // Declare state variables
    state = {
      datamodelResponse: undefined,
      attendanceList: undefined,
      errorMessage: undefined,
      absenteesList: undefined,
      durationList: undefined,
      leftEarlyList: undefined,
      attendanceLabel : [],
      attendanceValue : [],
      absenteesLabel : [],
      absenteesValue : [],
      durationLabel : [],
      durationValue : [],
      leftEarlyLabel : [],
      leftEarlyValue : [],
      error: undefined
  };

    // ReactJs function to fetch datamodel onload of page
    componentDidMount() {

      API
        // .get(apiJson.apiUrl+this.props.email,{
        .get('amplifynciapi','/attendance/'+this.props.email, {
          mode: 'cors',
          headers: {
            "Content-Type": "multipart/form-data"
          }
        })
        .then((response) => {
          console.log(response.data)
          this.setState({ error: response.data.error ? response.data.error : undefined});
          this.setState({ datamodelResponse: response.data.data ? response.data.data : response.data });

          this.setState({ attendanceList : response.data.attendance});

          for(var i in this.state.attendanceList) {
            console.log(i)
            this.state.attendanceLabel.push(this.state.attendanceList[i].date);
            this.state.attendanceValue.push(this.state.attendanceList[i].value);
          }

          this.setState({ absenteesList : response.data.absentees});

          for(var i in this.state.absenteesList) {
            console.log(i)
            this.state.absenteesLabel.push(this.state.absenteesList[i].date);
            this.state.absenteesValue.push(this.state.absenteesList[i].value);
          }

          this.setState({ durationList : response.data.duration});

          for(var i in this.state.durationList) {
            console.log(i)
            this.state.durationLabel.push(this.state.durationList[i].date);
            this.state.durationValue.push(this.state.durationList[i].value);
          }

          this.setState({ leftEarlyList : response.data.leftEarly});

          for(var i in this.state.leftEarlyList) {
            console.log(i)
            this.state.leftEarlyLabel.push(this.state.leftEarlyList[i].date);
            this.state.leftEarlyValue.push(this.state.leftEarlyList[i].value);
          }
          
          this.setState({ errorMessage: undefined });
        })
        .catch((error) => {
          console.log(error)
          this.setState({ errorMessage: `Failed to retrieve data for ${this.props.emailId}` });
        });
  
    }

  render() {
    return (
  <div>
    <div className="App-right">
      <a className="App-a active" href="#analytics">Analytics</a>
      <a onClick={() => this.props.onClick("Upload")} className="App-a" href="#upload">Upload Attendance</a>
    </div>
    <br/><br/><br/><br/>
    <div className="App-organizer">Organizer:&nbsp;{this.state.datamodelResponse ? this.state.datamodelResponse[4] : null}</div>
    <div className="App-center" >
      {this.state.error}
      <KPI email={this.state.datamodelResponse}/>
      <div>

      <div className="App-chart-left">Absentees over Meeting Date<LineChart date={this.state.absenteesLabel} value={this.state.absenteesValue}/></div>
      <div className="App-chart-right">Attendees over Meeting Date<BarChart date={this.state.attendanceLabel} value={this.state.attendanceValue}/></div>
      <div className="App-chart-left">Duration over Meeting Date<BarChart date={this.state.durationLabel} value={this.state.durationValue}/></div>
      <div className="App-chart-right">Student Left Early over Meeting Date<LineChart date={this.state.leftEarlyLabel} value={this.state.leftEarlyValue}/></div>
</div>
      <br/><br/><br/><br/><br/><br/><br/><br/>
    </div>
  </div>
        );
      }
  }