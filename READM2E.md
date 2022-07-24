# CDK and Control Tower

This is a cdk project that is attempting to use cdk to create accounts programatically using CDK. 
Control Tower has a so called 'Account Factory' which creates and prepares aws accounts so that they are (partially) ready to use in an organisation.   Account tower appears to be a Service Catalog Product, and can be invoked by calling the service catalog. 

Account Factory has some quirks.  The primary thing is that Accoutn factory can only be creating one account at at time.  If another accoutn is being created, service catalog will return an error.   This does not fit the normal pattern for resource creating with Cloudformation and so needs special treatment. 

The basic design for this cdk construct..

The stack described in ./lib/account-robot-stack.ts imports and uses 'n' instances of the the construct AccountRobot.  Because account factory can only build one account at a time, we add a dependancy, so they are built in order.  

The construct AccountRobot creates a custom resource using the cdk custom resources framework.   This custom resource makes use of of the aync call back, as the creation of the accounts takes approximately 35 minutes, and that will exceed the the maximum timeout of a lambda.   The onEventHandler does nothing in this case. 

looking at ./lib/constructs/robot.ts

There are two lambdas created, kick ( for kick the process off) and wait..   The lambdas are written in python for simplicty. Most of the other resources are to support the lambda.  There is the creation of a role,  and adding permisssions to the role. 

The role needs to be given access to the the service catalog portfolio.  (note that the import of the account_factory_portfoilio needs to be replaced with a lookup, as this wont' travel well across differnet environments.

```account_factory_portfoilo.giveAccessToRole(wait_role)```

The bulk of the work is being done by the wait.py lambda.  Please check the codes' comments which describe its operation.  
In summary,  each time the iscompelte handler calls it; 

1. there is a check to see if the account has been provisioned.   It determines if the accoutn is completed by checking to see if it has reached 'AVAILABLE' status. It will return complete if it is, otherwise the lambda continues.

2. There is a check to see if there has been any errors, while deploying. This could occur if the props were incorrect, for example if you provided an OU that did not exisit..  If the the Error is a 'ResourceInUse' this means that Account Factory was busy. ( perhaps someone started a creation of an account with clickops manually ).  If this is the case, it will try to recreate it again later.  If it is any other end, we'll return a FAILURE back to cloudformation,. Otherwise continue.

3. Check to see if if accoutn factory is busy. If it is, return 'NOT_READY'.  ( We'll come back later)..  If it is not busy, create an account.   The lambda calls list_provisiong_artificact to that the active_provisioning_artifact_id for control tower.   This is then used to provision the account, by calling service catalog.provision_product.




==Problem==:   no matter what permissions are granted to the lambda, it fails to be able to call the service catalog

❌  AccountRobotStack failed: Error: The stack named AccountRobotStack failed to deploy: CREATE_FAILED (The following resource(s) failed to create: [acounttwoAccountFactoryInvokerB910141F]. ): Received response status [FAILED] from custom resource. Message returned: Error: AccessDeniedException  User: arn:aws:sts::4xx7:assumed-role/AccountRobotStack-acounttwowaitrole3F380C4F-BHNP3DW3KLZD/AccountRobotStack-SingletonLambda39d06e46362f49eab-1khcTmMHFdfS is not authorized to perform: controltower:CreateManagedAccount because no identity-based policy allows the controltower:CreateManagedAccount action

It is possible to create an account by calling the account factory service catalog artificat directly.. either in a stack oras an administrator via CLI.   

What deeper magic?




