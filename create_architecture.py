from diagrams import Diagram, Cluster, Edge
from diagrams.aws.security import WAF, Cognito
from diagrams.aws.management import SystemsManagerParameterStore as SSM, Cloudwatch
from diagrams.aws.network import CloudFront, APIGateway
from diagrams.aws.storage import S3
from diagrams.aws.integration import SQS, SNS, Appsync
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.generic.device import Mobile
from diagrams.generic.network import Router

with Diagram("architecture_final", outformat="png", show=False, direction="LR"):
    with Cluster("External Ecosystem"):
        sensors = Router("IoT \nSensors")
        admin = Mobile("Dashboard \nClient")
    
    with Cluster("GLOBAL: Edge & Identity"):
        waf_global = WAF("AWS WAF \n(Global)")
        cf = CloudFront("CloudFront")
        s3 = S3("Frontend App OAC")
        cognito = Cognito("Cognito \nUser Pool")
        
        # global front
        waf_global >> cf >> s3
        cognito >> Edge(style="dashed") >> admin

    with Cluster("REGION: London (eu-west-2)"):
        waf_regional = WAF("AWS WAF \n(Regional)")
        ssm = SSM("SecureString \n(x-api-token)")
        apig = APIGateway("API Gateway \nv2")
        lambda_auth = Lambda("Auth \nLambda")
        sqs = SQS("SQS Ingest \nBuffer")
        lambda_ingest = Lambda("Ingest \nLambda")
        ddb = Dynamodb("DynamoDB \nClusters")
        ddb_stream = Dynamodb("DynamoDB \nStreams")
        appsync = Appsync("AWS AppSync")
        lambda_notify = Lambda("Notifier \nLambda")
        lambda_read = Lambda("Read \nLambda")
        cw = Cloudwatch("CloudWatch")
        sns = SNS("SNS (Alerts)")

    # Client to Global
    admin >> Edge(label="UI Request", color="blue") >> waf_global
    admin << Edge(label="Auth JWT cycle", color="blue", style="dashed") >> cognito
    
    # Telemetry flow
    sensors >> Edge(label="1. Telemetry", color="darkgreen") >> waf_regional
    waf_regional >> Edge(label="2. Validated", color="darkgreen") >> apig
    apig << Edge(label="3. Validate Req/Res", style="dashed") >> lambda_auth
    lambda_auth << Edge(style="dashed") >> ssm
    apig >> Edge(label="4. Buffering", color="darkgreen") >> sqs
    sqs >> Edge(label="5. Batch Invoke", color="darkgreen") >> lambda_ingest
    lambda_ingest >> Edge(label="6. Write State", color="darkgreen") >> ddb
    
    # WebSockets / Events
    ddb >> Edge(label="7. CDC feed", color="purple") >> ddb_stream
    ddb_stream >> Edge(label="8. Trigger", color="purple") >> lambda_notify >> Edge(label="9. Mutate", color="purple") >> appsync
    appsync >> Edge(label="10. Real-time Pub", color="purple") >> admin

    # Query flow
    admin >> Edge(label="11. Query", color="blue") >> appsync
    appsync >> Edge(label="12. Invoke", color="blue") >> lambda_read >> Edge(label="13. Read Data", color="blue") >> ddb

    # CloudWatch
    apig - Edge(style="dotted", color="red") - cw
    sqs - Edge(style="dotted", color="red") - cw
    ddb - Edge(style="dotted", color="red") - cw
    lambda_ingest - Edge(style="dotted", color="red") - cw
    lambda_read - Edge(style="dotted", color="red") - cw
    cw >> Edge(label="Alert", color="red") >> sns
