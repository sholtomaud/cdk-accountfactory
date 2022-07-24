import * as cdk from 'aws-cdk-lib'
import * as construct from 'constructs';
import { 
  aws_iam as iam, 
  aws_lambda as lambda,
  custom_resources as cr,
  aws_servicecatalog as sc,
}
from 'aws-cdk-lib';
import * as fs from 'fs';


export interface AccountRobotProps {
	SSOUserEmail: string;
	SSOUserFirstName: string;
	SSOUserLastName: string;
	ManagedOrganizationalUnit: string; //'name (ou-xxxx)',
	AccountName: string;
	AccountEmail: string
}

export class AccountRobot extends construct.Construct {
  constructor(scope: construct.Construct, id: string, props: AccountRobotProps) {
    super(scope, id);

  // create the lambdas kick and wait 👉️ These lambdas dont have any dependancys and are small so can be inline
	const kick = new lambda.SingletonFunction(this, 'KickLambda', {
		uuid: '5d94a63f-ba6b-4141-8e6c-63b7f48b1ac9',
		code: lambda.Code.fromInline(fs.readFileSync('./lib/lambda/kick.py','utf-8')),  
		handler: 'index.on_event',
		runtime: lambda.Runtime.PYTHON_3_9,
		timeout: cdk.Duration.seconds(300)
	})

	const wait_role = new iam.Role(this,'waitrole', {
		assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
		roleName: `${props.AccountName}AcctFactoryStart`
	})

	wait_role.addManagedPolicy(
		iam.ManagedPolicy.fromManagedPolicyArn(this, 'lambdapolicy',
		  'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
		)
	)

	wait_role.addManagedPolicy(
		iam.ManagedPolicy.fromManagedPolicyArn(this, 'AdministratorPolicy',
		  'arn:aws:iam::aws:policy/AdministratorAccess'
		)
	)
	
	wait_role.addToPolicy(
		new iam.PolicyStatement({
			effect: iam.Effect.ALLOW,
			actions: [
				'servicecatalog:ScanProvisionedProducts',
				'servicecatalog:DescribeProductAsAdmin',
				'servicecatalog:ProvisionProduct',
				'servicecatalog:ListProvisioningArtifacts',
				'controltower:CreateManagedAccount',
				//'*'
			],
			resources: ['*']
		})
	)

	const wait = new lambda.SingletonFunction(this, 'WaitLambda', {
		uuid: '39d06e46-362f-49ea-b2d6-2124687df8bb',
		code: lambda.Code.fromInline(fs.readFileSync('./lib/lambda/wait.py','utf-8')),
		handler: 'index.is_complete',
		runtime: lambda.Runtime.PYTHON_3_9,
		timeout: cdk.Duration.seconds(300),
		role: wait_role
	})

	// we need to give access to account_factory_portfolio.. This needs to be a look

	const account_factory_portfoilo = sc.Portfolio.fromPortfolioArn(this, 'accountfactoryportfolio',
		'arn:aws:catalog:ap-southeast-2:4xxxxxxx7:portfolio/port-c7od7gkls7sva'
	);
	

	account_factory_portfoilo.giveAccessToRole(wait_role)

	const RobotProvider = new cr.Provider(this, 'RobotProvider', {
		onEventHandler: kick,
		isCompleteHandler: wait,        // optional async "waiter"
		queryInterval: cdk.Duration.minutes(2),
		totalTimeout: cdk.Duration.hours(12)
	 });

	new cdk.CustomResource(this, 'AccountFactoryInvoker', {
		serviceToken: RobotProvider.serviceToken,
		properties: {
			'PhysicalResourceId': `AccountFactory${props.AccountName}`,
			'ProvisioningProps': props
		}
	})
 }
}
