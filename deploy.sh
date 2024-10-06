echo "Updating fastapi_1..."
docker compose up -d --build fastapi_1
echo "Waiting for fastapi_1 to be ready..."
sleep 10

echo "Updating fastapi_2..."
docker compose up -d --build fastapi_2
echo "Waiting for fastapi_2 to be ready..."
sleep 10

echo "Restarting remaining containers..."
docker compose up -d --build nginx mongo redis prometheus grafana telebot cadvisor node_exporter

echo "Deployment completed."