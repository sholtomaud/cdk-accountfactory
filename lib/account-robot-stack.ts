import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

import { AccountRobot } from '../lib/constructs/robot';

export class AccountRobotStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    new AccountRobot(this, 'acounttwo', {
      SSOUserEmail: 'standuptest2@aws.education.govt.nz',
      SSOUserFirstName: 'User',
      SSOUserLastName: 'Name',
      ManagedOrganizationalUnit: 'applications (ou-qme3-3c9x1v1i)',
      AccountName: 'standuptest2',
      AccountEmail: 'standuptest2@aws.education.govt.nz'
    })
  }
}
