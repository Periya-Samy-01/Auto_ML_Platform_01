# NodeForge AutoML Platform

A production-grade, node-based Machine Learning model builder and end-to-end ML platform. NodeForge empowers users to visually design, train, and evaluate machine learning models through an intuitive drag-and-drop interface, backed by a highly scalable, secure, and cost-efficient architecture.

## 🌟 Key Features

- **Node-Based Visual Builder**: Construct complex ML workflows without writing code. Drag, drop, and connect nodes for data preprocessing, feature engineering, model training, and evaluation.
- **Enterprise-Grade Scalability**: Built to handle 10,000+ concurrent users with a reliable microservices architecture, automated Celery worker scaling, and Redis-backed rate limiting.
- **Robust Security & Anti-Fraud**: Integrated device fingerprinting, IP intelligence, and velocity checks to ensure platform integrity and fair usage.
- **Tiered Cost Controls**: Fair queue scheduling and job cost tracking that balances Free, Pro, and Enterprise workloads dynamically while enforcing hard cost caps.

## 📊 Dashboard Sections

The NodeForge dashboard provides a streamlined, professional experience divided into key functional areas:

- **Overview**: Your central hub. View high-level metrics, recent job statuses, credit balances, resource usage, and quick links to your most active projects.
- **Playground (Visual Canvas)**: The core node-based ML builder. Visually assemble your ML pipelines by connecting data source nodes to preprocessing operators, selecting algorithms, configuring hyperparameters, and initiating training jobs.
- **Datasets**: Your secure data repository. Upload, preview, and manage datasets. Includes automated exploratory data analysis (EDA), data profiling, and summary statistics.
- **Models**: The model registry. Review completed training runs, evaluate performance metrics (including SHAP explainability, feature importance, and confusion matrices), and manage model versions.
- **Learn**: The educational center. Access interactive tutorials, ML best practices, workflow templates, and guides to help you maximize the potential of the node-based builder.

## 🏗️ System Architecture

The platform is designed with a risk-reduced, global architecture ensuring a 99.9% uptime SLA and <200ms API response times:

- **Client Layer**: Responsive Next.js/React application using TypeScript and Tailwind CSS, featuring optimistic UI updates and real-time WebSocket connectivity.
- **API & Edge Layer**: Stateless FastAPI instances protected by Cloudflare CDN (DDoS/Bot protection) and an NGINX load balancer.
- **Compute Workers**: Celery workers powered by a Redis message broker, utilizing a custom scheduling algorithm to guarantee fair processing time across all user tiers.
- **Data Persistence**: PostgreSQL (Neon Serverless) with read-replicas for lightning-fast dashboard queries, and Cloudflare R2 object storage for highly cost-effective dataset and model artifact persistence.

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.11+)
- Docker & Docker Compose (for local backend infrastructure)

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Auto_ML_Platform_01
   ```

2. **Start Backend Infrastructure**:
   Navigate to the `docker` folder to spin up Redis, PostgreSQL, and backend services.
   ```bash
   cd docker
   docker-compose up -d
   ```

3. **Start the Web Client**:
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

4. Access the platform at `http://localhost:3000`.

## 🛡️ Security & Compliance
- **Compliance**: Designed following GDPR data minimization principles and COPPA age verification.
- **Encryption**: End-to-end TLS 1.3 encryption in transit, with database and storage AES-256 encryption at rest.
- **Abuse Prevention**: Comprehensive automated systems to detect excessive cancellations, bot patterns, and VPN abuse.
