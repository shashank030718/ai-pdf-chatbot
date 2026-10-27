AI PDF Chatbot — RAG-Based Document Question Answering
An AI-powered web application that lets users upload PDF documents and ask questions about their contents in natural language. The application retrieves relevant text from the uploaded document and uses Google's Gemini API to generate context-aware answers.

Live demo: http://13.126.40.198
The demo is hosted on AWS EC2. Availability depends on the instance being running, and the public IP may change after a stop/start unless a stable address is configured. The current demo uses HTTP; do not upload confidential documents.

Features
- Upload PDF documents through a web interface.
- Extract text from PDFs with PyMuPDF.
- Split extracted text into smaller chunks for retrieval.
- Generate semantic embeddings with Sentence Transformers.
- Retrieve relevant chunks using FAISS similarity search.
- Generate answers using the Gemini API and retrieved document context.
- React frontend with a FastAPI backend.
- Dockerized frontend and backend for deployment.
- GitHub Actions workflow to build Docker images and publish them to Amazon ECR on pushes to master.
How it works
1. Upload: The user uploads a PDF in the React frontend.
2. Extract: The FastAPI backend uses PyMuPDF to extract document text.
3. Chunk: The text is divided into smaller sections.
4. Embed: Sentence Transformers converts text chunks into vector embeddings.
5. Index and retrieve: FAISS searches for chunks most relevant to the user's question.
6. Generate: The backend sends the question and retrieved context to Gemini.
7. Answer: The generated response is returned to the frontend and displayed to the user.
This workflow is called Retrieval-Augmented Generation (RAG). It helps ground responses in the uploaded document, but answers should still be checked for accuracy.
Architecture
User
 |
 v
React Frontend (Nginx, port 80)
 |
 | /api requests
 v
FastAPI Backend (port 8000, internal/local access)
 |
 +--> PyMuPDF: PDF text extraction
 +--> Sentence Transformers: text embeddings
 +--> FAISS: similarity search
 +--> Gemini API: answer generation
For the AWS deployment, the frontend and backend run in separate Docker containers on an EC2 instance. Nginx serves the frontend and proxies API requests to the backend over a Docker network. Docker images are stored in Amazon Elastic Container Registry (ECR).
Tech stack
Component	Technology	Purpose
Language	Python	Backend and RAG pipeline
Backend API	FastAPI	API endpoints and request handling
Frontend	React	User interface
PDF processing	PyMuPDF	Extract PDF text
Embeddings	Sentence Transformers (all-MiniLM-L6-v2)	Convert text into vectors
Vector search	FAISS	Find relevant text chunks
LLM	Google Gemini API (google-genai)	Generate natural-language answers
Containers	Docker	Package application services
Web server / proxy	Nginx	Serve frontend and proxy API requests
Cloud deployment	AWS EC2	Host the application
Image registry	Amazon ECR	Store Docker images
CI/CD	GitHub Actions	Build and push images on master pushes


Run locally
Prerequisites
- Python 3.10
- Node.js and npm (Node.js 22 is used in the current setup)
- Docker Desktop and Docker Compose (for the containerized option)
- A Gemini API key
1. Clone the repository
git clone https://github.com/shashank030718/ai-pdf-chatbot.git
cd ai-pdf-chatbot
2. Configure the Gemini API key
Create a .env file in the project root:
GEMINI_API_KEY=your_gemini_api_key_here
Replace the placeholder with your own key. Never commit .env or publish your API key. Ensure .env is listed in .gitignore.
3. Start with Docker Compose
If the repository includes a docker-compose.yml file, build and start the services from the project root:
docker compose up --build -d
Open the frontend at:
- http://localhost:3000
Check running containers:
docker compose ps
docker compose logs -f
Stop the services:
docker compose down
The current EC2 deployment runs the frontend on port 80. Local ports depend on the repository's Compose configuration.

Running without Docker
The exact commands depend on the current backend and frontend configuration. In general, create and activate a Python virtual environment, install the packages in requirements.txt, configure the Gemini API key, run the FastAPI application, and install/start the React frontend using npm. Refer to the source files and package scripts for the exact commands.
AWS deployment overview
The deployed version uses:
- Amazon EC2 to run the application.
- Amazon ECR repositories ai-pdf-backend and ai-pdf-frontend to store Docker images.
- An EC2 IAM role with ECR read permissions so the instance can pull images.
- Separate Docker containers for the frontend and backend.
- An Nginx reverse proxy to route /api/ requests to the backend.
The current public demo is http://13.126.40.198.

The address is an EC2 public IPv4 address and may change after stopping and starting the instance unless a stable address, such as an Elastic IP or domain, is configured. The application is currently served over HTTP; configure HTTPS before using it for sensitive information or wider public use.
CI/CD workflow
The GitHub Actions workflow in .github/workflows/ci.yml:
1. Runs on pushes and pull requests targeting master.
2. Builds the backend and frontend Docker images.
3. On pushes to master, authenticates to AWS using GitHub OIDC and the configured AWS_ROLE_ARN repository secret.
4. Pushes the images to Amazon ECR with the commit SHA and latest tags.
Important: The current workflow builds and pushes images; it does not yet automatically update the running EC2 containers. After a new image is published, deployment to EC2 still needs to be performed separately until an automatic deployment step is configured.
Security notes
- Keep Gemini API keys in environment variables or a secret manager; never commit secrets to Git.
- Do not upload sensitive or confidential PDFs to the public demo.
- Avoid exposing backend port 8000 directly to the public internet. In the current setup it is bound to localhost on the EC2 host and accessed through the frontend proxy.
- The demo uses HTTP, so traffic is not encrypted in transit. Configure HTTPS and a domain for a production-ready public application.
- Public access can result in API usage and AWS charges. Monitor Gemini API usage and AWS billing.
- Stop or remove AWS resources when they are no longer needed, keeping in mind that storage and public IPv4 charges may still apply in some circumstances.
Possible future improvements
- Configure a domain name and HTTPS.
- Add automatic deployment to EC2 after a successful GitHub Actions build.
- Add authentication, rate limiting, and upload-size controls.
- Improve error handling for scanned PDFs that need OCR.
- Add tests, logging, and monitoring.
- Improve answer citations so users can identify the source pages or passages.
Author
Shashank M P

