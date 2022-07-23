import boto3

sc = boto3.client('servicecatalog')

NOT_READY = False
COMPLETED = True


def is_complete(event, context):
    
    request_type = event['RequestType'].lower()
    
    
    if request_type == 'create':
        create(event, context)
    elif request_type == 'update':
        update(event, context)
    elif request_type == 'delete':
        delete(event, context)
    else:
        raise ValueError('Unsupported Event Type')

def create(event, context):

    props = event['ResourceProperties']['ProvisioningProps']

    # Check to see if the account is already provisioned..  if it is return ready.
    # note scan_provisioned_products may be paginated, we we need potentially make multiple calls
    # there is no filter on this API call, so we need to filter them them using a list comprehension
    
    completed_check = sc.scan_provisioned_products(
        AcceptLanguage='string',
        AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
    )

    if [record for record in completed_check['ProvisionedProducts'] if (record['Type'] == 'CONTROL_TOWER_ACCOUNT' and record['Status'] == 'AVAILABLE' and record['Name'] == props['AccountName'])]:
        return { 'IsComplete': COMPLETED }

    while 'NextPageToken' in completed_check.keys():
    
        completed_check = sc.scan_provisioned_products(
            AcceptLanguage='string',
            AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
            PageToken= completed_check['NextPageToken']
        )

        if [record for record in completed_check['ProvisionedProducts'] if (record['Type'] == 'CONTROL_TOWER_ACCOUNT' and record['Status'] == 'AVAILABLE' and record['Name'] == props['AccountName'])]:
            return { 'IsComplete': COMPLETED }

    
    # Check to see if there was a provisioning Error and fail if it was anything other than a ResourceInUseException, which we'll just retry to get around the race condition
    
    error_check = sc.scan_provisioned_products(
        AcceptLanguage='string',
        AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
    )

    error_check_result = [record for record in error_check['ProvisionedProducts'] if (record['Type'] == 'CONTROL_TOWER_ACCOUNT' and record['Status'] == 'ERROR' and record['Name'] == props['AccountName'])]

    if len(error_check_result) != 0: 
        if 'ResourceInUseException' not in error_check_result[0]['StatusMessage']:
            print('Error:', error_check_result['StatusMessage'] )
            raise ValueError(error_check_result['StatusMessage'])  #force an error, so the Framework sends CF a Fail
    

    while 'NextPageToken' in error_check.keys():

        error_check = sc.scan_provisioned_products(
            AcceptLanguage='string',
            AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
            PageToken= error_check['NextPageToken']
        )

        error_check_result = [record for record in error_check['ProvisionedProducts'] if (record['Type'] == 'CONTROL_TOWER_ACCOUNT' and record['Status'] == 'ERROR' and record['Name'] == props['AccountName'])]

        if len(error_check_result) != 0: 
            if 'ResourceInUseException' not in error_check_result[0]['StatusMessage']:
                print('Error:', error_check_result[0]['StatusMessage'] )
                raise ValueError(error_check_result[0]['StatusMessage'])  #force an error, so the Framework sends CF a Fail
            

    # check to see if the Service Catalogue is busy, if it is, do nothing, return not ready
    # if it is quiet, provision the account

    busy_check = sc.scan_provisioned_products(
        AcceptLanguage='string',
        AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
    )

    if [record for record in busy_check['ProvisionedProducts'] if (record['Type'] == 'CONTROL_TOWER_ACCOUNT' and record['Status'] in ['UNDERCHANGE', 'PLAN_IN_PROGRESS'])]:
        return { 'IsComplete': NOT_READY }

    while 'NextPageToken' in busy_check.keys():
        
        busy_check = sc.scan_provisioned_products(
            AcceptLanguage='string',
            AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
            PageToken= busy_check['NextPageToken']
        )

        if [record for record in busy_check['ProvisionedProducts'] if (record['Type'] == 'CONTROL_TOWER_ACCOUNT' and record['Status'] in ['UNDERCHANGE', 'PLAN_IN_PROGRESS'])]:
            return { 'IsComplete': NOT_READY }



    ct_account_factory_sc_product = sc.describe_product_as_admin(
        Name='AWS Control Tower Account Factory'
    )
    ct_account_factory_sc_product_id = ct_account_factory_sc_product['ProductViewDetail']['ProductViewSummary']['ProductId']
    ct_account_factory_sc_provisioning_artifacts = sc.list_provisioning_artifacts(ProductId=ct_account_factory_sc_product_id)['ProvisioningArtifactDetails']
    active_provisioning_artifact_id = [provisioning_artifact for provisioning_artifact in ct_account_factory_sc_provisioning_artifacts if provisioning_artifact['Active']][0]['Id']

    provisioning_props = []
    for key, value in props.items():
        provisioning_props.append(
            {
                'Key': key,
                'Value': value    
            }
        )
      

    sc.provision_product( 
        ProductId = ct_account_factory_sc_product_id,
        ProvisionedProductName= props['AccountName'],
        ProvisioningArtifactId = active_provisioning_artifact_id,
        ProvisioningParameters = provisioning_props
    )

    return {'IsComplete': NOT_READY } # we return false because we know this takes ~35minutes or so.
        

def update(event, context):         # TODO. I think all we possibly could do is move OUs?
    return { 'IsComplete': COMPLETED }  
    
    
def delete(event, context):        # TODO Deleting an account.. This is kinda curious. ?  
    return { 'IsComplete': COMPLETED }