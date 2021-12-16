import React, { Component } from "react";
import { Bar, Pie, Doughnut } from 'react-chartjs-2'
import { CategoryScale } from 'chart.js';
import { Chart, ArcElement } from 'chart.js'
import { BarController, BarElement, Tooltip, Legend, LineController, LineElement, PointElement, LinearScale, Title } from 'chart.js'
Chart.register(BarController, BarElement, Tooltip, Legend, LineController, LineElement, PointElement, LinearScale, Title)
Chart.register(ArcElement);
Chart.register(CategoryScale)

export default class BarChart extends Component {

  retrieveData(date, value){
  return {
    labels: date,
    datasets: [{
      data: value,
      backgroundColor: [
        'rgba(255, 99, 132, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(255, 206, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(153, 102, 255, 0.2)',
        'rgba(255, 159, 64, 0.2)',
      ],
      borderColor: [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)',
      ],
    }]
  }
}
  render() {
    return (
      <div style={{ width: "500px", margin: "0 auto" }}>
        <Bar data={this.retrieveData(this.props.date, this.props.value)}
        />
      </div>
    )
  }
}