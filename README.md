# my-ai-chatmate
### Export packages
cd /d D:\Development\Projects\my-ai-chatmate
pipreqs . --force
Include: python-telegram-bot[job-queue]==21.10
Delete bark, whisper
### Build Image and push it
docker build -t haoyinni/my-ai-chatmate:20250208-1 . 
### Connect to aws
```bash

ssh -i ~/.ssh/ai-chatbot.pem ec2-user@18.206.124.131
```

### Redis Port fowarding
docker run --name redis-server --network ai-chatbot -d -p 6379:6379 redis

```bash

ssh -i ~/.ssh/ai-chatbot.pem -L 6379:localhost:6379 ec2-user@18.206.124.131
```

### PostGre SQL Port forwarding
```bash

docker run --name postgres-db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=aichatbot \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  --network ai-chatbot \
  -d postgres:latest
```
```bash 

ssh -i ~/.ssh/ai-chatbot.pem -L 5432:localhost:5432 ec2-user@18.206.124.131
```

### Pull image
docker pull haoyinni/my-ai-chatmate:20250208-1
### Run image
docker kill <container-id>
docker run -d haoyinni/my-ai-chatmate:20250208-1
