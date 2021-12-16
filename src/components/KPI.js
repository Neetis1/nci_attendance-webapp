import React from 'react'

function KPI({ email }) {
  return (
    <div class='parent'>
      <div class='child float-left-child'>Number of Attendees <h1>{email ? email[0] : null}</h1></div>
      <div class='child float-left-child'>Number of Absentees <h1>{email ? email[1] : null}</h1></div>
      <div class='child float-left-child'>Meeting Date <br/><br/><h2>{email ? email[2] : null}</h2></div>
      <div class='child float-left-child'>Meeting Duration<br/><h1>{email ? email[3] : null}</h1></div>
    </div>


  )
}

export default KPI