import pytz
import json
import pandas as pd
import os
import logging
import azure.functions as func
import config.mbr_config as mbr_cfg
import threading
from enum import Enum
from azure.storage.blob import BlobServiceClient,BlobClient,ContainerClient
from snowflake.snowpark import Session
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants and global variables
az_container_name = "mbr-landing-dev"
az_connection_string = os.getenv('AzureWebJobsStorage')
# Reuse the BlobServiceClient instance
blob_service_client = BlobServiceClient.from_connection_string(az_connection_string)
# Create and reuse Snowflake session globally
snowflake_session = None
# Variables - Count pages
countFinancial  = 0
countSeniority  = 0
countRevenue    = 0    
countBacklog    = 0
countProject    = 0

# Utility functions
def get_current_time():
    tz = pytz.timezone('Europe/Paris')
    current_time = datetime.now().astimezone(tz)
    return current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def create_snowflake_session():    
    global snowflake_session
    if not snowflake_session:
        # Create a snwoflake session
        connection_sf = 'creds.json'
        with open(connection_sf) as f:
          connection_parameters = json.load(f)
        snowflake_session = Session.builder.configs(connection_parameters).create()    
    #return snowflake_session

# Blob utility functions
def download_blob_data(myblob):
    blob_client_instance = blob_service_client.get_blob_client(az_container_name,myblob,snapshot=None)
    return blob_client_instance.download_blob().readall()

def delete_blob(myblob):
    blob_client_instance = blob_service_client.get_blob_client(az_container_name,myblob,snapshot=None)
    blob_client_instance.delete_blob()

# Error handling for Teams notifications
def handle_exception(blob_name, error_message):
    #Teams
    sent_teams_notification(blob_name,teams_notif_type.LOAD_ERROR, file_load_desc=error_message )
    logging.error(error_message)

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="mbr-landing-dev/{name}",
                               connection="ocean01_STORAGE") 
def fKAP_Loader(myblob: func.InputStream):

    # Main file processing function
    def process_blob_file():
        try:
            blob_name = myblob.name.split('/')[-1]
            blob_data = download_blob_data(blob_name)

            #Teams
            sent_teams_notification(blob_name,teams_notif_type.RECEIVED )

            # Determine the type of file and process accordingly
            if 'BUDGET' in blob_name.upper():
                process_mbr_budget_file(blob_data,blob_name)
            elif 'FPA' in blob_name.upper():
                process_adjustement_file(blob_data, blob_name)
            elif 'keyrus - exchange rates' in blob_name.lower():
                process_fx_file(blob_data,blob_name)
            elif 'ECOVADIS' in blob_name.upper():
                process_ecovadis_file(blob_data, blob_name)
            else:
                process_mbr_file(blob_data,blob_name)

            # Delete the blob after processing
            delete_blob(blob_name)
        
        except Exception as e:
            print('Execption')  
    
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")

    # Create a snowflake session
    create_snowflake_session()
    # Process the incoming blob file
    process_blob_file()
    
# Modular handling of different types of files
def process_mbr_file(blob_data, blob_name):
    # Variables
    BU_Code = BU_Name = Currency_Code = None    
    #Create lock 
    lock = threading.Lock()

    def get_freeze_period_status(mbr_scope, mbr_month):   
        MBRscopeNo_ = str.replace(MBRScope,'_',' ')        
        #Connect to Snowflake // Retrieve the status of the MBR Scope (DEV or PROD) in FreezePeriod
        mbr_scope_state = snowflake_session.sql(f''' SELECT * FROM OCEAN_ADM.MBR_FREEZE_PERIODS WHERE "MBR Scope" = '{mbr_scope}' AND "MBR Month"= '{mbr_month}' ''').collect() 
        return mbr_scope_state[0][3]
    
    def process_sheet(sheet_name, config, bu_code=None,bu_name = None, currency_code = None, dropna=None):
        global countFinancial, countSeniority, countRevenue, countBacklog, countProject

        if sheet_name in xls.sheet_names:
            columns, new_columns, skiprows, table_prefix = config
            table_name = f'TEST_{table_prefix}_{MBRScope.upper()}_{bu_code or ""}'.strip('_')
            
            # Load and process the sheet
            load_and_process_sheet(xls, sheet_name, skiprows,columns, new_columns, table_name,
                                          mbr_filename=blob_name, mbr_month=MBRmonth,mbr_scope=MBRScope, dropna=dropna, currency_code=currency_code,
                                          bu_code=bu_code, bu_name=bu_name)            
            
            # Update the count for various sheets with thread safety
            with lock: 
                if 'P&L FI_BU' in sheet_name or 'IC declaration' == sheet_name : countFinancial +=  1
                if 'KPI Pyramid' == sheet_name : countSeniority += 1
                if sheet_name in ('License & Maintenance','Clients','Revenue distribution') : countRevenue += 1
                if 'Backlog and WP input' == sheet_name : countBacklog += 1
                if 'Project_' in sheet_name : countProject += 1

    # Main execution
    try:
        # Retrieve MBR parameters and send initial notification
        MBRScope, MBRmonth, MBRparams, xls = get_excel_params(blob_data, "MBR Parameters")
        MBRScope_w_ = MBRScope.replace(' ','_')
        #IsAllowed_FP = get_freeze_period_status(MBRScope,MBRmonth)

        # Parallel sheet processing using a ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            futures = []
            # Process P&L sheets
            if 'P&L FI_BU01' in xls.sheet_names :            
                for index, row in MBRparams.iterrows():
                    BU_Code = row['BU_Code']
                    BU_Name = row['BU_Name']
                    Currency_Code = row['Currency_Code']
                    
                    # Submit tasks for each matching sheet
                    for sheet_name in xls.sheet_names:
                        if(sheet_name.endswith(f'FI_{BU_Code}')):
                            futures.append(executor.submit(process_sheet,sheet_name,mbr_cfg.config_pnl,BU_Code, BU_Name, Currency_Code))    

                # Reset after processing each BU     
                BU_Code = BU_Name = Currency_Code = None       

            # Add other sheet processing tasks
            futures.extend([
                executor.submit(process_sheet,'IC declaration',mbr_cfg.config_ic,dropna=['INDEX','IC_PARTNER']), 
                executor.submit(process_sheet,'KPI Pyramid',mbr_cfg.config_kpi_pyramid),
                executor.submit(process_sheet,'License & Maintenance',mbr_cfg.config_license_maint,dropna=['SOFTWARE_PARTNERS']),
                executor.submit(process_sheet,'Clients',mbr_cfg.config_client, dropna=['CLIENT_NAME']),
                executor.submit(process_sheet,'Revenue distribution',mbr_cfg.config_revenue_dist),
                executor.submit(process_sheet,'Backlog and WP input',mbr_cfg.config_backlog),
                executor.submit(process_sheet,'Project_PRO',mbr_cfg.config_project_pro, dropna=['PROJECT_NAME']),
                executor.submit(process_sheet,'Project_PL',mbr_cfg.config_project_pl, dropna=['PROJECT_NAME']),
                executor.submit(process_sheet,'Project_CC',mbr_cfg.config_project_cc, dropna=['PROJECT_NAME']), 
            ])
        
        # Wait for all threads to complete
        for future in as_completed(futures):
            future.result()  # Ensure all tasks are completed
        
        # Send Teams notification upon raw data load completion
        sent_teams_notification(blob_name, teams_notif_type.LOAD_RAW)  

        # Run the paradime schedule
        if countFinancial > 0 :            
            schedule_status, schedule_name = run_paradime_schedule(MBRScope_w_,schedule_file_type.FINANCIAL)  
        if countSeniority > 0 : 
            schedule_status, schedule_name = run_paradime_schedule(MBRScope_w_, schedule_file_type.SENIORITY)
        if countRevenue > 0 :
            schedule_status, schedule_name = run_paradime_schedule(MBRScope_w_, schedule_file_type.REVENUE)    
        if countBacklog > 0 : 
            schedule_status, schedule_name = run_paradime_schedule(MBRScope_w_, schedule_file_type.BACKLOG)
        
        # Send notification based on the scheduling result
        if schedule_status == 'SUCCESS':
            sent_teams_notification(blob_name, teams_notif_type.LOAD_DWH)
            sent_mail_notification(MBRScope,blob_name, mail_notif_type.LOAD_SUCCESS, MBRmonth)
        #else:
        #    sent_teams_notification(blob_name, teams_notif_type.LOAD_ERROR)

    except Exception as e:
        handle_exception(blob_name, str(e))
        sent_mail_notification(MBRScope,blob_name, mail_notif_type.LOAD_ERROR)
     
def process_mbr_budget_file(blob_data, blob_name):
    # Variables
    BU_Code = None
    BU_Name = None
    Currency_Code = None
    # Retrieve MBR info
    def get_excel_mbr_data():
        # Load parameters from the "MBR Parameters" worksheet
        df_Period = pd.read_excel(blob_data,"Settings",skiprows=2,usecols="C",nrows=1, header=None,names=["Value"]).iloc[0]["Value"]
        df_Period = df_Period.strftime("%Y-%m-%d")
        df_BU = pd.read_excel(blob_data, "Settings", skiprows=5, usecols="C", nrows=1, header=None, names=["Value"] ).iloc[0]["Value"]
        df_Currency_Code =pd.read_excel(blob_data, "Settings", skiprows=9, usecols="C", nrows=1, header=None, names=["Value"] ).iloc[0]["Value"]

        # Load the entire MBR excel file so we can iterate over the different worksheet that we need
        df_xls = pd.ExcelFile(blob_data)

        return  df_BU, df_Period, df_Currency_Code, df_xls
    
    def process_sheet(sheet_name, config, dropna=None):
        if sheet_name in xls.sheet_names:
            columns, new_columns, skiprows, table_prefix = config
            table_name = f'TEST_{table_prefix}_{BU_w_.upper()}'
            return load_and_process_sheet(xls, sheet_name, skiprows,columns, new_columns, table_name,
                                          mbr_filename=blob_name, dropna=dropna, currency_code=Currency_Code, bu_name=BU,period=Period)

    try:
        # Send teams notification
        BU, Period, Currency_Code, xls = get_excel_mbr_data()        
        BU_w_ = BU.replace(' ','_')

        with ThreadPoolExecutor() as executor:
            futures = []
            futures.append(executor.submit(process_sheet,'P&L FI_BU01',mbr_cfg.config_budget_pl))        
            futures.append(executor.submit(process_sheet,'IC declaration',mbr_cfg.config_budget_ic,dropna=['IC_PARTNER'])) 
            futures.append(executor.submit(process_sheet,'KPI Pyramid',mbr_cfg.config_budget_kpi_pyramid)) 
            futures.append(executor.submit(process_sheet,'License & Maintenance',mbr_cfg.config_budget_license_maint,dropna=['SOFTWARE_PARTNERS']))
            futures.append(executor.submit(process_sheet,'Clients',mbr_cfg.config_budget_client, dropna=['CLIENT_NAME']))
            futures.append(executor.submit(process_sheet,'Revenue distribution',mbr_cfg.config_budget_revenue_dist))
            futures.append(executor.submit(process_sheet,'Signing & Pipeline',mbr_cfg.config_budget_signing_pipeline))    
        
        # Wait for all threads to complete
        for future in as_completed(futures):
            future.result()  # Ensure all tasks are completed
        
        sent_teams_notification(blob_name, teams_notif_type.LOAD_RAW)
        
    except Exception as e:
        handle_exception(blob_name, str(e))
     
def process_adjustement_file(blob_data, blob_name):
    try:
        columns, new_columns, skiprows, table_prefix = mbr_cfg.config_adjustement
        df_adj = pd.read_excel(blob_data,'KAP', skiprows=skiprows,usecols=columns,converters={k: str for k in range(len(columns))})

        #Apply new columns
        df_adj.columns = new_columns
        
        #Add additional columns
        df_adj['CREATED_ON'] = get_current_time()
        df_adj['MBR_FILENAME'] = str(blob_name)

        # Compose a new valid tablename + scenario
        scenario_type = df_adj['SCENARIO'].values[0].upper()
        if scenario_type == 'CORPORATE BUDGET':
            table_prefix = f'TEST_{table_prefix}_CORPORATE_BUDGET'
        elif scenario_type == 'WORKING FCT':
            table_prefix = f'TEST_{table_prefix}_FORECAST'
        else:
            table_prefix = f'TEST_{table_prefix}_{scenario_type}'

        load_data_to_snowflake(df_adj, table_prefix)

    except Exception as e:
        handle_exception(blob_name, str(e))

def process_fx_file(blob_data, blob_name):
    # Retrieve MBR info
    try:
        columns, new_columns, skiprows, table_prefix = mbr_cfg.config_fx_rate

        df_FX = pd.read_excel(blob_data,'IMPORT_Kap', skiprows=skiprows,usecols=columns,converters={k: str for k in range(len(columns))})
        mbr_month = df_FX.iat[0,2]
        df_FX = df_FX.drop([0,1,2,3,4,5])
        
        #Apply the new columns
        df_FX.columns = new_columns
        
        #Add additional columns
        df_FX['MBR_MONTH'] = mbr_month
        df_FX['CREATED_ON'] = get_current_time()
        df_FX['FX_FILENAME'] = blob_name

        load_data_to_snowflake(df_FX, table_prefix)

    except Exception as e:
        handle_exception(blob_name, str(e))
    
def process_ecovadis_file(blob_data, blob_name):
    # Variables
    BU_Code = None
    BU_Name = None
    Currency_Code = None
    
    def process_sheet(sheet_name, config, bu_code=None,bu_name = None, currency_code = None, dropna=None):
        if sheet_name in xls.sheet_names:
            columns, new_columns, skiprows, table_prefix = config
            table_name = f'TEST_{table_prefix}_{MBRScope_w_.upper()}_{bu_code}'

            load_and_process_sheet(xls, sheet_name, skiprows,columns, new_columns, table_name,
                                          mbr_filename=blob_name, mbr_month=MBRmonth,mbr_scope=MBRScope, dropna=dropna, currency_code=currency_code,
                                          bu_code=bu_code, bu_name=bu_name)            

    try:
        # Send teams notification
        MBRScope, MBRmonth, MBRparams, xls = get_excel_params(blob_data, "Parameters")
        MBRScope_w_ = MBRScope.replace(' ','_')

        # P&L
        with ThreadPoolExecutor() as executor:          
            for index, row in MBRparams.iterrows():
                BU_Code = row['BU_Code']
                BU_Name = row['BU_Name']
                Currency_Code = row['Currency_Code']

                for sheet_name in xls.sheet_names:
                    if(sheet_name == (f'Ecovadis_{BU_Code}')):
                        executor.submit(process_sheet,sheet_name,mbr_cfg.config_ecovadis,BU_Code, BU_Name, Currency_Code)         
                BU_Code = None
                BU_Name = None
                Currency_Code = None            

    except Exception as e:
        handle_exception(blob_name, str(e))

# Process & load file in Snowflake
def load_data_to_snowflake(dataframe, table_name):    
    # Write data to snowflake table
    return snowflake_session.write_pandas(dataframe,table_name,auto_create_table = True, overwrite = True)

def load_and_process_sheet(xls_data, sheet_name, skiprows, columns, new_columns,table_name, mbr_filename,
                           mbr_month=None,mbr_scope=None, bu_code=None,bu_name=None,currency_code=None,dropna = None, period = None):
    df_sheet = pd.read_excel(xls_data,
                             sheet_name=sheet_name,
                             skiprows=skiprows,
                             usecols=columns,
                             converters={k: str for k in range(len(columns))})
    df_sheet.columns = new_columns

    # Additional info
    if bu_code : df_sheet['BU_CODE'] = bu_code
    if bu_name : df_sheet['BU_NAME'] = bu_name
    if currency_code : df_sheet['CURRENCY_CODE'] = currency_code
    if mbr_scope : df_sheet['MBR_SCOPE'] = mbr_scope
    if mbr_month : df_sheet['MBR_MONTH'] = mbr_month
    if period : df_sheet['BUD_PERIOD'] = period
    df_sheet['CREATED_ON'] = get_current_time()
    df_sheet['MBR_FILENAME'] = mbr_filename

    # Remove Empty rows based on column in dropna parameter
    if dropna : df_sheet = df_sheet.dropna(subset=dropna) 

    result = load_data_to_snowflake(df_sheet, table_name)

def get_excel_params(blob_data, param_sheet_name):
        # Load parameters from the "MBR Parameters" worksheet
        df_Params   = pd.read_excel(blob_data, param_sheet_name)
        df_MBRscope = df_Params.iloc[0,2]
        df_MBRmonth = df_Params.iloc[2,2].strftime("%Y-%m-%d")

        # Load the table with BU's from "MBR Parameters" worksheet
        df_MBRparams = df_Params.iloc[6:16,5:8]
        df_MBRparams.columns = ["BU_Code","BU_Name","Currency_Code"]
        df_MBRparams.dropna(subset=['BU_Code','BU_Name','Currency_Code'], inplace=True)

        # Load the entire MBR excel file so we can iterate over the different worksheet that we need
        df_xls = pd.ExcelFile(blob_data)

        return df_MBRscope, df_MBRmonth, df_MBRparams, df_xls

class schedule_file_type(Enum):
    FINANCIAL = 'operations_run_pl_'
    SENIORITY = 'operations_run_kp_'
    REVENUE   = 'operations_run_lm_'
    BACKLOG   = 'operations_run_bl_'

def run_paradime_schedule(mbr_scope, schedule_type = schedule_file_type):
    import requests
    import time

    def _extract_gql_response(request: requests.Response, query_name: str, field: str) -> str:
        response_json = request.json()
        if "errors" in response_json:
            raise Exception(f"{response_json['errors']}")
        try:
            return response_json["data"][query_name][field]
        except (TypeError, KeyError) as e:
            raise ValueError(f"{e}: {response_json}")


    # The URL, key, and secret would need to be obtained from Paradime
    #url = os.getenv('paradime_url')
    url = 'https://api.paradime.io/api/v1/sha8vppvucjfvxwa/graphql'
    headers = {
            "Content-Type": "application/json",
            "X-API-KEY": 'dq47d74m6kwkgg37r7gk2zyvghfyw6zu',
            "X-API-SECRET": 'gv7ajlg4ga50vl2e95620g33fieh1ahlkpkdpj2iw75phuwntmi1ca26amji61qph4dqywtl4zwplqfdt26vjybu5qcq05an',
    }

    #bolt_schedule_name = f'{schedule_type.value}{str(mbr_scope).lower()}'
    bolt_schedule_name = 'operations_run_FX_fx'

    # Define the GraphQL query for triggering a Bolt run
    query = """
        mutation trigger($scheduleName: String!) {
        triggerBoltRun(scheduleName: $scheduleName){
            runId
        }
        }
    """
    variables = {"scheduleName": bolt_schedule_name}  # Replace with your actual schedule name

    data = {"query": query, "variables": variables}
    response = requests.post(url, headers=headers, json=data) # make the request to start the Bolt job

    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Request failed with status code {response.status_code}")

    # Parse the response to get the Bolt run ID
    run_id = _extract_gql_response(response, "triggerBoltRun", "runId")

    # Now we can use this ID to get the status of the Bolt run
    bolt_run_status_query = """
        query Status($runId: Int!) {
        boltRunStatus(runId: $runId) {
            state
        }
    }
    """

     # Keep checking the status until the run is complete
    while True:
        response = requests.post(
            url, json={"query": bolt_run_status_query, "variables": {"runId": int(run_id)}}, headers=headers
        )
        status = response.json()["data"]["boltRunStatus"]["state"]
        #st.write(status)
        if status in ["SUCCESS", "FAILED"]:
            break        
        # Sleep for a while before checking again
        time.sleep(10)
    
    # Now you can do something with the status
    if status == "SUCCESS":        
        print("Snowflake DWH refreshed! Start the PowerBI refresh")
        return "SUCCESS", bolt_schedule_name
    else:
        return "ERROR", bolt_schedule_name
        print("Snowflake DWH refresh failed!")     

# Notifications
class teams_notif_type(Enum):
    RECEIVED = '1 - File received'
    LOAD_ERROR = '0 - Error on file'
    LOAD_RAW = '2 - File loaded in raw schema'
    LOAD_DWH = '3 - File loaded in DWH'
class mail_notif_type(Enum):
    LOAD_SUCCESS = 'Load success'
    LOAD_ERROR = 'Load Error'
    LOAD_FREEZE = 'Freeze'

def sent_teams_notification(file_name, notif_type = teams_notif_type, mbr_scope=None, mbr_month=None, file_load_desc=None):
    import requests    
    urlTeams = "https://keyrusgroup.webhook.office.com/webhookb2/68b15510-2653-4855-be23-14cd5190e969@168e48b2-81f0-4aac-bc77-d58d07d205e2/IncomingWebhook/1217263db75b4b1ea586455578c14fef/7d069be0-a9ad-4d5d-9109-8a307e57a11d"
    headerTeams = {'Content-Type':'application/json'}

    if notif_type == teams_notif_type.RECEIVED :
        mess = teams_notif_type.RECEIVED.value
    elif notif_type == teams_notif_type.LOAD_RAW :
        mess = teams_notif_type.LOAD_RAW.value
    elif notif_type == teams_notif_type.LOAD_DWH :
        mess = teams_notif_type.LOAD_DWH.value
    elif notif_type == teams_notif_type.LOAD_ERROR :
        mess = teams_notif_type.LOAD_ERROR.value

    mess = f'{mess} at {get_current_time()} : <b>{file_name}</b>'
    
    if file_load_desc:
        mess += f'<p>{file_load_desc}</p>'

    message = {"text":mess}

    response = requests.post(urlTeams, headers=headerTeams, data = json.dumps(message))

def sent_mail_notification(mbr_scope, file_name, mail_type = mail_notif_type ,mbr_month=None):
    import smtplib
    from email.mime.text import MIMEText

    # Connect to Snowflake // Fetch the contact information from OCEAN_ADM.MBR_CONTACT_INFO
    try:
        mbr_scope_mail = snowflake_session.sql(f'''
        SELECT * FROM OCEAN_ADM.MBR_CONTACT_INFO WHERE MBR_SCOPE = '{ mbr_scope}'  ''').collect()

        receiver_mails = mbr_scope_mail[0][3]
        receiver_first_name = mbr_scope_mail[0][1]
    except Exception as e :
        logging.warning(f"Failed to retrieve email for MBR scope {mbr_scope}. Using fallback email. Error: {str(e)}")        
        receiver_mails =  'eric.dilu@keyrus.com'
        receiver_first_name = 'Eric'

    # SMTP Configuratin
    port = 25
    smtp_server = 'mxa-00604b01.gslb.pphosted.com'
    sender_email ='kap.notifications@keyrus.com'

    # Define content and subject for different mail types
    mail_content = {
        mail_type.LOAD_SUCCESS : {
             'Subject' : 'KAP Notification - MBR File Successfully Loaded',
             'html_content' : f'''
                <p>Dear {receiver_first_name},</p>
                <p>We are pleased to inform you that the MBR file <strong>{file_name}</strong> has been successfully loaded for the month of <strong>{mbr_month}</strong>.</p>
                <p>The data is now available for further processing and reporting.</p>
                <p>If you have any questions or require further assistance, please do not hesitate to contact us.</p>
                <p>Best regards,<br/>
                The KAP Team</p>
                '''
        },
        mail_type.LOAD_ERROR : {
             'Subject' : 'KAP Notification -Error Loading MBR File',
             'html_content' :  f'''
                <p>Dear {receiver_first_name},</p>
                <p>Unfortunately, an error occurred while processing the MBR file <strong>{file_name}</strong> for the month of <strong>{mbr_month}</strong>.</p>
                <p>Our team is looking into the issue, and we will keep you updated on the status. In the meantime, you may want to verify the file’s format and content for any potential issues.</p>
                <p>If this issue persists or you need further assistance, please contact our support team at <a href="mailto:dev.kap@keyrus.com">dev.kap@keyrus.com</a>.</p>
                <p>Best regards,<br/>
                The KAP Team</p>
                '''
        },
        mail_type.LOAD_FREEZE : {
             'Subject' : 'KAP Notification - MBR File in Freeze Period',
             'html_content' : f'''
                <p>Dear {receiver_first_name},</p>
                <p>We would like to inform you that the MBR file <strong>{file_name}</strong> for the month of <strong>{mbr_month}</strong> is currently in a <strong>freeze period</strong>.</p>
                <p>During this time, no further modifications or processing of the file are allowed.</p>
                <p>If you believe this is an error or require more information, please contact our support team at <a href="mailto:dev.kap@keyrus.com">dev.kap@keyrus.com</a>.</p>
                <p>Best regards,<br/>
                The KAP Team</p>
                '''
        }
    }

    # Get contant and subject based on mail_type
    email_data = mail_content.get(mail_type,{})
    if not email_data:
        logging.error(f"Invalid mail_type provided: {mail_type}")
        return 
    
    receiver_mails = ['eric.dilu@keyrus.com']
    
    # Create MIMEHtml object
    message = MIMEText(email_data['html_content'],'html')    
    message['Subject'] = email_data['Subject']
    message['From'] = sender_email
    message['To'] = ', '.join(receiver_mails)

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls() # Secure the connection
            server.send_message(message, sender_email, receiver_mails)
            logging.info(f"Notification email sent to {receiver_mails} for file {file_name}.")
    except Exception as e :
        logging.error(f"Failed to send email notification for file {file_name}. Error: {str(e)}")
        pass