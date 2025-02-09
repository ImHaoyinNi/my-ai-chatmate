# my-ai-chatmate
### pipreqs . --force
Delete bark, whisper
### Build Image
docker build -t haoyinni/my-ai-chatmate:20250208-1 . 
### Connect to aws
ssh -i ~/.ssh/ai-chatbot.pem ec2-user@18.206.124.131
### Pull image
docker pull haoyinni/my-ai-chatmate:20250207
### Run image
docker run -d haoyinni/my-ai-chatmate:20250208-1
### Notes
Query (Q): Acts like a "search" vector. It asks: "Which tokens in the sequence are relevant to me?"

Key (K): Acts like a "retrieval" vector. It answers: "Here’s what I can contribute to other tokens."

Value (V): Contains the actual content to aggregate based on attention weights.
