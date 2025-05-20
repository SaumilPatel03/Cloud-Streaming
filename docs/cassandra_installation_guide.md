# 🐳 Cassandra Installation Using Docker on Linux

This guide walks you through installing and running **Apache Cassandra** using **Docker** on a Linux system.

> **Prerequisite:** Docker must be installed and running on your system.

## 📥 Step 1: Pull the Cassandra Docker Image
```bash
sudo docker pull cassandra
```

## 🚀 Step 2: Run the Cassandra Container
```bash
sudo docker run --name cassandra -d -p 9042:9042 cassandra
```

## ✅ Step 3: Verify the Running Container
```bash
sudo docker ps
```

If the container isn't running:
```bash
sudo docker start cassandra
```

## 🌀 (Optional) Run Another Cassandra Container
```bash
sudo docker run -d -p 9042:9042 cassandra
```

## 🛠️ Step 4: Access the Cassandra Shell (CQLSH)
```bash
sudo docker exec -it cassandra bash
cqlsh
```

## 🧹 Cleanup (Optional)
```bash
sudo docker stop cassandra
sudo docker rm cassandra
sudo docker rmi cassandra
```

## 📚 Resources
- [Apache Cassandra Documentation](https://cassandra.apache.org/doc/)
- [Cassandra Docker Image on Docker Hub](https://hub.docker.com/_/cassandra)
