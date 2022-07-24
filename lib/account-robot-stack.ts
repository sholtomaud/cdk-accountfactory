import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

import { AccountRobot } from '../lib/constructs/robot';

export class AccountRobotStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const account1 = new AccountRobot(this, 'accountone', {
      SSOUserEmail: 'standuptest2@domain.com',
      SSOUserFirstName: 'User',
      SSOUserLastName: 'Name',
      ManagedOrganizationalUnit: 'applications (ou-qme3-3c9x1v1i)', // this format is important!
      AccountName: 'standuptest2',
      AccountEmail: 'standuptest2@aws.domain.com'
    })

    
    const account2 =  new AccountRobot(this, 'accounttwo', {
      SSOUserEmail: 'standuptest2@domain.com',
      SSOUserFirstName: 'User',
      SSOUserLastName: 'Name',
      ManagedOrganizationalUnit: 'applications (ou-qme3-3c9x1v1i)', // this format is important!
      AccountName: 'standuptest2',
      AccountEmail: 'standuptest2@aws.domain.com'
    })

    account2.node.addDependency(account1) // account 2 will not start to build till account1 is complete. 

  }
}
