import React, { Component } from "react";
import axios from "axios";
import apiJson from './apiUrl.json'
import Amplify, { API } from "aws-amplify";
import awsconfig from "./aws-exports";

export default class FileUpload extends Component {

    // Declare state variables
    state = {
        attendanceFile: undefined,
        error: undefined,
        responseSuccessMessage: undefined,
        responseErrorMessage: undefined,
        apiUrl: undefined,
        headApi: undefined
    };

    // Function to Upload Attendance File
    uploadFile() {

        const api_endpoint = awsconfig.aws_cloud_logic_custom[0].endpoint;
        const multiFormArray = new FormData();
        multiFormArray.append("emailUserName", this.props.email);
        multiFormArray.append("attendanceFile", this.state.attendanceFile);

        axios
            .post(api_endpoint + '/attendance', multiFormArray, {
                mode: 'cors',
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            })
            .then((response) => {
                console.log(response)
                response.data['error'] ? this.setState({ responseErrorMessage: response.data['error'] }) :
                    this.setState({ responseSuccessMessage: `Attendance File uploaded successfully for ${this.props.email}` });
            })
            .catch((error) => {
                console.log(error)
                this.setState({ responseErrorMessage: `Attendance File failed to upload for ${this.props.email}: Reason: File Already Uploaded` });
            });
    }
    render() {
        return (
            <div>
                <div className="App-right">
                    <a onClick={() => this.props.onClick("Analytics")} className="App-a" href="#analytics">Analytics</a>
                    <a className="App-a active" href="#upload">Upload Attendance</a>
                </div>
                <div className="App-center" >
                    <h1> Upload Attendance File </h1>
                    <p>Click on the "Choose File" button to upload Attendance file for Analysis:</p>
                    <form>
                        <input className="App-upload" type="file" onChange={e => {
                            this.setState({
                                attendanceFile: e.target.files[0]
                            });
                        }} />
                        {this.state.attendanceFile ? (<input className="App-submit" type="submit" value="Upload" onClick={e => {
                            this.uploadFile();
                        }} />) : null}
                    </form>
                    <br />
                    <br />
                    {this.state.responseErrorMessage ? (<h4 className="App-orange">{this.state.responseErrorMessage}</h4>) : null}
                    {this.state.responseSuccessMessage ? (<h4 className="App-green">{this.state.responseSuccessMessage}</h4>) : null}
                </div>
            </div>
        );
    }
}