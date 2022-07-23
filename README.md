# CDK and Control Tower

This is a cdk project that is attempting to use cdk to create accounts programatically using CDK. 
Control Tower has a so called 'Account Factory' which creates and prepares aws accounts so that they are (partially) ready to use in an organisation.   Account tower appears to be a Service Catalog Product, and can be invoked by calling the service catalog. 

Account Factory has some quirks.  The primary thing is that Accoutn factory can only be creating one account at at time.  If another accoutn is being created, service catalog will return an error.   This does not fit the normal pattern for resource creating with Cloudformation and so needs special treatment. 

The basic design for this cdk construct is as follows