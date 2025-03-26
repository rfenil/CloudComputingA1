import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("songs")

def lambda_handler(event, context):
    headers = {"Content-Type": "application/json"}
    route_key = event["routeKey"]
    #Deletion Operation
    if route_key == "DELETE /songs/{id}":
        music_id = event["pathParameters"]["id"]
        table.delete_item(Key={"id": music_id})
        body = "Deleted music item with id " + music_id
        statusCode = 200
    #Getting music by ID
    elif route_key == "GET /songs/{id}":
        music_id = event["pathParameters"]["id"]
        result = table.get_item(Key={"id": music_id})
        body = result["Item"]
        statusCode = 200
    #Getting all Items
    elif route_key == "GET /songs":
        result = table.scan()
        body = result["Items"]
        statusCode = 200
    #Updating the element in the table
    elif route_key == "PUT /songs":
        requestJSON = json.loads(event["body"])
        music_id = requestJSON["id"]
        update_expression = "set " + ", ".join([f"{key} = :{key}" for key in requestJSON if key != "id"])
        expression_values = {f":{key}": requestJSON[key] for key in requestJSON if key != "id"}
        response = table.update_item(
            Key={"id": music_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
        body = {"message": "Music item updated", "attributes": response["Attributes"]}
        statusCode = 200
    #Insertion of a new element into the table
    elif route_key == "POST /songs":
        requestJSON = json.loads(event["body"])
        table.put_item(
            Item={
                "id": requestJSON["id"],
                "title": requestJSON.get("title", ""),
                "artist": requestJSON.get("artist", ""),
                "album": requestJSON.get("album", ""),
                "year": requestJSON.get("year", ""),
                "s3_url": requestJSON.get("s3_url", "")
            }
        )
        body = "Created music item with id " + requestJSON["id"]
        statusCode = 200

    else:
        body = "Unsupported route: " + route_key
        statusCode = 400

    response = {
        "statusCode": statusCode,
        "headers": headers,
        "body": json.dumps(body)
    }
    return response

    """
    Reference:
    Amazon.com. (2025). Tutorial: Create a CRUD HTTP API with Lambda and DynamoDB - Amazon API Gateway. [online] Available at: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-dynamo-db.html#http-api-dynamo-db-create-function [Accessed 25 Mar. 2025].
     """