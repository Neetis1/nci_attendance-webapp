from pymysql import err
import json
import json
import logging
import sys
import pymysql
import boto3
import datetime
import base64
import email
import os
from botocore.exceptions import ClientError

sys.path.insert(0, '../layers/msteams/python/lib/python3.8/site-packages/')

from MSTeamsdataretrieval import TeamsDataRetrival

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
current_time = datetime.datetime.now()


def handler(event, context):
    """Processes Attendance Report uploaded using API Gateway.
    Args:
        event (dict) : Lambda dictionary of event parameters. The event keys must include httpMethod, resource, path, body etc.,
        context (Context): This contains Lambda runtime information
    """

    # body = {
    #     "message": "Go Serverless v1.0! Your function executed successfully!",
    #     "input": event["body"]
    # }
    
    logger.info(event)
    httpMethod = event["httpMethod"]

    if (httpMethod == 'POST'):

        response = uploadAttendance(event)

    elif (httpMethod == 'GET'):

        response = retrieveDataModel(event)

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """


def uploadAttendance(event):

    """Uploads MS Team Attendance to RDS
    Args:
        event (dict) : Lambda dictionary of event parameters. The event keys must include httpMethod, resource, path, body etc.,
    """

    RDS_SECRETID = os.environ['RDS_SECRETID']
    errorMessage = ''
    successMessage = ''

    decodedData = decodeEvent(event)

    fileDecodedData = decodedData["attendanceFile"].decode('utf8')
    meetingTitle = ''
    meetingId = ''
    meetingPeopleList = []
    S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]

    try:

        teamsDataProcessed = TeamsDataRetrival.MSTeamsAttendanceProcessor(fileDecodedData)
        attendanceList = teamsDataProcessed.getAttendeesDetailsAsList()
        masterData = teamsDataProcessed.getAttendeesforMasterData()

        s3Client = boto3.client("s3")
        s3Client.put_object(
            Bucket=S3_BUCKET_NAME, Key=decodedData["emailUserName"].decode('utf-8')+'/'+masterData[1], Body=decodedData["attendanceFile"]
            )

        if len(attendanceList) > 1:

            try:
                secretManagerResp = get_secretinfo(RDS_SECRETID)
                secrets = json.loads(secretManagerResp['SecretString'])

                conn = pymysql.connect(host=secrets['host'].replace(':3306', ''), user=secrets['username'],
                                       passwd=secrets['password'], db=secrets['dbname'], connect_timeout=5)

                with conn.cursor() as cursor:
                    cursor.execute("create table if not exists ATTENDANCE \
                        ( full_name varchar(255), join_time varchar(255),\
                            leave_time varchar(255), duration varchar(255), \
                                email varchar(255), role varchar(255), \
                                    participant_id varchar(255), meeting_title varchar(255), \
                                        meeting_id varchar(255))")

                    cursor.execute("create table if not exists ATTENDANCE_MASTER \
                        ( meeting_id varchar(255), organiser varchar(255), duration varchar(255))")

                    # Check for Meeting Id already exists
                    cursor.execute('select count(distinct meeting_id) as count_meeting_id from ATTENDANCE_MASTER where meeting_id="{0}"'.format(masterData[1]))
                    
                    meetingExists = cursor.fetchone()
                    
                    if int(meetingExists[0]) > 0:
                        
                        errorMessage = "Attendance File already uploaded"
                    
                    else:
                        cursor.execute("insert into ATTENDANCE_MASTER (meeting_id, organiser, duration) values(\"{0}\",\"{1}\",\"{2}\")".format(
                                masterData[1], masterData[2], masterData[3]))
                        conn.commit()
                        
                        for meetingPeople in attendanceList:
                            logger.info("insert into ATTENDANCE (full_name, join_time, leave_time, duration, email, role, participant_id, meeting_title, meeting_id) values(\"{0}\",\"{1}\",\"{2}\",\"{3}\",\"{4}\",\"{5}\",\"{6}\",\"{7}\",\"{8}\")".format(
                                meetingPeople[0], meetingPeople[1], meetingPeople[2], meetingPeople[3], meetingPeople[4], meetingPeople[5], meetingPeople[8], meetingPeople[6], meetingPeople[7]))
                            cursor.execute("insert into ATTENDANCE (full_name, join_time, leave_time, duration, email, role, participant_id, meeting_title, meeting_id) values(\"{0}\",\"{1}\",\"{2}\",\"{3}\",\"{4}\",\"{5}\",\"{6}\",\"{7}\",\"{8}\")".format(
                                meetingPeople[0], meetingPeople[1], meetingPeople[2], meetingPeople[3], meetingPeople[4], meetingPeople[5], meetingPeople[8], meetingPeople[6], meetingPeople[7]))
                            conn.commit()
    
                    conn.commit
                    successMessage = "Attendance Records Updated"
                    logger.info('Inserted Students Attendance Records')



            except pymysql.MySQLError as e:
                logger.error(
                    "ERROR: Unexpected error: Could not connect to MySQL instance.")
                logger.error(e)
                sys.exit()

        else:
            raise Exception("Meeting Title and Meeting Id is not present")

    except Exception as ex:
        logger.info("Failed to process multi-part/form data")
        logger.error(ex)
        sys.exit(1)

    response = {
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "statusCode": 200,
        "body": json.dumps({
            "sucess": successMessage,
            "error" : errorMessage
        })
    }

    return response


def retrieveDataModel(event):

    """Retrieves DataModel
    Args:
        event (dict) : Lambda dictionary of event parameters. The event keys must include httpMethod, resource, path, body etc.,
    """

    RDS_SECRETID = os.environ['RDS_SECRETID']
    emailPath = event["path"]
    email = emailPath.rsplit('/', 1)[-1]

    datamodel = []


    try:

        secretManagerResp = get_secretinfo(RDS_SECRETID)
        secrets = json.loads(secretManagerResp['SecretString'])

        conn = pymysql.connect(host=secrets['host'].replace(':3306', ''), user=secrets['username'],
                                passwd=secrets['password'], db=secrets['dbname'], connect_timeout=5)

        logger.info(email)

        with conn.cursor() as cursor:

            cursor.execute("select count(a.meeting_id) as number_of_attendees, (60 - count(a.meeting_id)) as absentees,\
                            STR_TO_DATE(a.join_time, '%m-%d-%Y') as meeting_date, \
                            b.duration, b.organiser, b.meeting_id, COALESCE(l.left_early,0) as left_early \
                            from nci_app.ATTENDANCE a join nci_app.ATTENDANCE_MASTER b on a.meeting_id = b.meeting_id \
                            left join \
                            (select count(a.left_early) left_early, a.meeting_date, a.meeting_id from\
                            (select substring(a.duration,1,2),\
                            if(substring(a.duration,1,2) < b.duration/2 , TRUE, FALSE) as left_early,\
                            STR_TO_DATE(a.join_time, '%m-%d-%Y') as meeting_date, a.meeting_id\
                            from nci_app.ATTENDANCE a join nci_app.ATTENDANCE_MASTER b where a.meeting_id = b.meeting_id) a \
                            where a.left_early > 0 group by meeting_date) l\
                            on a.meeting_id = l.meeting_id\
                            group by b.meeting_id\
                            order by meeting_date")

        datamodelRecords = cursor.fetchall()

        attendanceList = []
        attendance = {}

        length = len(datamodelRecords) - 1 

        for data in datamodelRecords:
            attendance = {}
            attendance["date"] = data[2].strftime("%Y-%m-%d")
            attendance["value"] = data[0]
            attendanceList.append(attendance)

        absenteesList = []
        absentees = {}

        for data in datamodelRecords:
            absentees = {}
            absentees["date"] = data[2].strftime("%Y-%m-%d")
            absentees["value"] = data[1]
            absenteesList.append(absentees)

        
        durationList = []
        duration = {}

        for data in datamodelRecords:
            duration = {}
            duration["date"] = data[2].strftime("%Y-%m-%d")
            duration["value"] = data[3]
            durationList.append(duration)

        leftEarlyList = []
        leftEarly = {}


        for data in datamodelRecords:
            leftEarly = {}
            leftEarly["date"] = data[2].strftime("%Y-%m-%d")
            leftEarly["value"] = data[6]
            leftEarlyList.append(leftEarly)

        kpi = [datamodelRecords[length][0],datamodelRecords[length][1],datamodelRecords[length][2].strftime("%Y-%m-%d"),datamodelRecords[length][3],datamodelRecords[length][4],datamodelRecords[length][5]]

        response = {
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "statusCode": 200,
        "body": json.dumps({
            'data': kpi,
            'attendance': attendanceList,
            'absentees': absenteesList,
            'duration': durationList,
            'leftEarly': leftEarlyList,
            })
        }

        return response

    except Exception as ex:
        logger.info("Failed to retrieve datamodel")
        logger.error(ex)
        sys.exit(1)


def get_secretinfo(secretId):
    """Gets the secrets stored in the Secrets Manager.
    Args:
        secretsId (String) : Secret Id of the secrets stored in the secrets manager.
    Raises:
        Exception: If the Secret not found.
    """

    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        resp = client.get_secret_value(SecretId=secretId)
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'ARN' in resp:
            logger.info("Found Secret String")
            return resp
        else:
            logger.info("ARN not found")
            raise Exception("Error retrieving secrets " + secretId +
                            " : " + current_time.strftime("%m/%d/%Y, %H:%M:%S"))
    except ClientError as err:
        logger.info('Error Talking to SecretsManager: ' +
                    err.response['Error']['Code'] + ', Message: ' + str(err))
        raise Exception("Error retrieving secrets " + secretId +
                        " : " + current_time.strftime("%m/%d/%Y, %H:%M:%S"))

def decodeEvent(event):

    """Parses Multipart/Form-Data from the NCI Attendance Webapp.
    Args:
        event (dict) : Lambda dictionary of event parameters.
    """

    encoded = base64.b64encode(bytes(event["body"], 'utf-8'))
    # logger.info(encoded)
    reponseBody = base64.b64decode(encoded)
    decodedFormData = {}
    
    try:

        ctBoundary = "Content-Type: " + event["headers"]["Content-Type"] + "\n"
        
    except:
        raise Exception("Content-Type in not available in the request")

    # Parse multipart/form-data payload from Event-Request data
    parsedFormData = email.parser.BytesParser().parsebytes(ctBoundary.encode() + reponseBody)

    # logger.info(parsedFormData)

    try:
        if len(parsedFormData.get_payload()) > 1 and parsedFormData.is_multipart() :  # Check the request data contains Multipart
            
            for encodedData in parsedFormData.get_payload():
                
                decodedFormData[encodedData.get_param("name", header="content-disposition")] = encodedData.get_payload(decode=True)

        return decodedFormData
    
    except Exception as ex:
        logger.info("Failed to process multi-part/form data")    
        logger.error(ex)
        sys.exit(1)
