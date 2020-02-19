import boto3
import time
import os
from datetime import datetime

def lambda_handler(event, context):
    currentTime = time.time()
    #setting duaration time log, for one month (31 days)
    logFromTime=int((currentTime - (currentTime % 3600) - 2678400) * 1000)
    logToTime=int((currentTime - (currentTime % 3600)) * 1000)
    
    #Setup client
    client = boto3.client('logs',region_name=os.environ['LOGS_REGION'])
    # list of logs group
    logGroups = ['test','/aws/lambda/func-export-logs-s3']
    # Create ExportTask for each logs group
    for nameGroup in logGroups:
        exportTaskResponse = client.create_export_task(
            taskName=nameGroup,
            logGroupName=nameGroup,
            fromTime=logFromTime,
            to=logToTime,
            destination=os.environ['LOGS_BUCKET'],
            destinationPrefix='cloudwatchlogs%s/%s'% (nameGroup,time.strftime('%Y-%d-%mT%H.%M.%SZ',  time.gmtime(logFromTime/1000)))
        )
        
        loopCondition = 1
        # Check condition for next Task
        while (loopCondition == 1):
            # Get TaskId of current ExportTask
            currentTaskId = exportTaskResponse['taskId']
            describeTaskResponse = client.describe_export_tasks(
                taskId = currentTaskId
            ) 
            # Get TaskExport Status
            responseTask = describeTaskResponse['exportTasks']
            responseTaskExport = responseTask[0]
            statusResponseTaskExport = responseTaskExport['status']
            statusFinal = statusResponseTaskExport['code']
            
            if (statusFinal == 'PENDING'):
                loopCondition = 1
                print ("Current status of Task:",statusFinal, "on:",datetime.now() )
                time.sleep(20)
            elif (statusFinal == 'RUNNING'):
                loopCondition = 1
                print ("Current status of Task:",statusFinal, "on:",datetime.now() )
                time.sleep(20)
            elif (statusFinal == 'COMPLETED'):
                loopCondition = 0
                print ("Current status of Task:",statusFinal, "on:",datetime.now() )
            else:
                loopCondition = 0
                print ("Error Task:",statusFinal, "on:",datetime.now() )
            
            
