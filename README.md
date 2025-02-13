# my-ai-chatmate
### Export packages
cd /d D:\Development\Projects\my-ai-chatmate
pipreqs . --force
Include: python-telegram-bot[job-queue]==21.10
Delete bark, whisper
### Build Image
Change .env values
docker build -t haoyinni/my-ai-chatmate:20250208-1 . 
### Connect to aws
ssh -i ~/.ssh/ai-chatbot.pem ec2-user@18.206.124.131
### Pull image
docker pull haoyinni/my-ai-chatmate:20250208-1
### Run image
docker kill <container-id>
docker run -d haoyinni/my-ai-chatmate:20250208-1
