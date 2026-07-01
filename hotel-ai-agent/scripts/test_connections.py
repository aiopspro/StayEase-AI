import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


def test_mongodb():
    print("\n--- MongoDB Atlas ---")
    try:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            print("FAIL: MONGO_URI is not set in .env")
            return False

        from pymongo import MongoClient
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

        client.admin.command("ping")
        print("Ping:         OK")

        db = client["hotel_modernization"]
        print(f"Database:     {db.name}")

        collections = db.list_collection_names()
        print(f"Collections:  {collections if collections else '[] (empty - run seed scripts)'}")

        print(f"Rooms:        {db['rooms'].count_documents({})}")
        print(f"Vectors:      {db['room_vectors'].count_documents({})}")
        print(f"Bookings:     {db['bookings'].count_documents({})}")
        print("Result:       CONNECTED")
        return True

    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_bedrock():
    print("\n--- AWS Bedrock ---")
    try:
        aws_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        region = os.getenv("AWS_REGION", "us-east-1")
        model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")

        if not aws_key or not aws_secret:
            print("FAIL: AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY is not set in .env")
            return False

        import boto3, json
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region,
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
        )

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "messages": [{"role": "user", "content": "Say OK"}]
        })

        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
        )

        response_body = json.loads(response["body"].read())
        reply = response_body["content"][0]["text"].strip()
        print(f"Region:       {region}")
        print(f"Model:        {model_id}")
        print(f"Response:     {reply}")
        print("Result:       CONNECTED")
        return True

    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_voyageai():
    print("\n--- VoyageAI ---")
    try:
        api_key = os.getenv("VOYAGE_API_KEY")
        if not api_key:
            print("FAIL: VOYAGE_API_KEY is not set in .env")
            return False

        import voyageai
        vo = voyageai.Client(api_key=api_key)
        result = vo.embed(["test hotel room"], model="voyage-3", input_type="document")
        dims = len(result.embeddings[0])
        print(f"Model:        voyage-3")
        print(f"Dimensions:   {dims}")
        print("Result:       CONNECTED")
        return True

    except Exception as e:
        print(f"FAIL: {e}")
        return False


if __name__ == "__main__":
    print("=" * 40)
    print("  StayEase AI - Connection Tests")
    print("=" * 40)

    results = {
        "MongoDB Atlas": test_mongodb(),
        "AWS Bedrock":   test_bedrock(),
        "VoyageAI":      test_voyageai(),
    }

    print("\n" + "=" * 40)
    print("  Summary")
    print("=" * 40)
    all_passed = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name:<20} {status}")
        if not passed:
            all_passed = False

    print("=" * 40)
    if all_passed:
        print("  All connections OK. Ready to run.")
    else:
        print("  Fix the FAIL items above before running.")
    print("=" * 40)

    sys.exit(0 if all_passed else 1)
