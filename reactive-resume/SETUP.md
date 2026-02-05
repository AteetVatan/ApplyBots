# Reactive Resume - Setup Guide

This guide provides step-by-step instructions for setting up Reactive Resume in a local development environment.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Environment Configuration](#environment-configuration)
4. [Infrastructure Setup](#infrastructure-setup)
5. [Running the Application](#running-the-application)
6. [Useful Commands](#useful-commands)
7. [Access Points](#access-points)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps](#next-steps)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Node.js** | v20 or higher | JavaScript runtime |
| **pnpm** | v10.28.0 or higher | Package manager |
| **Docker** | Latest | Container services |
| **Docker Compose** | v2+ | Service orchestration |
| **Git** | Latest | Version control |

### Installation Links

- [Node.js](https://nodejs.org/)
- [pnpm](https://pnpm.io/installation)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

---

## Installation

### Step 1: Install pnpm

If you haven't installed pnpm yet:

```bash
npm install -g pnpm
```

Verify installation:

```bash
pnpm --version
```

### Step 2: Install Project Dependencies

Navigate to the reactive-resume directory and install dependencies:

```bash
cd reactive-resume
pnpm install
```

This will install all required packages defined in `package.json`.

---

## Environment Configuration

### Step 3: Create `.env` File

Create a `.env` file in the `reactive-resume` directory root with the following configuration:

```bash
# Server Configuration
APP_URL=http://localhost:3002

# Printer Configuration (required for PDF generation)
# Note: PRINTER_APP_URL uses host.docker.internal to allow Docker containers
# to access services running on your host machine
PRINTER_APP_URL=http://host.docker.internal:3002
PRINTER_ENDPOINT=ws://localhost:4000?token=1234567890


# Note: File storage (profile pictures, screenshots, PDFs) is handled by the backend API.
# No S3 configuration is needed in reactive-resume. The backend manages all storage operations.
```

### Environment Variables Explained

- **APP_URL**: The base URL where your application will be accessible
- **PRINTER_APP_URL**: Required when running the app outside Docker while printer is in Docker. Uses `host.docker.internal` to allow Docker containers to reach your host machine
- **PRINTER_ENDPOINT**: WebSocket endpoint for the PDF generation service (Browserless)
- **Note**: This application uses FastAPI backend for data storage. No local database setup is required.
- **Storage**: File storage (profile pictures, screenshots, PDFs) is handled by the backend API. No S3 configuration needed in reactive-resume.

---

## Infrastructure Setup

### Step 4: Start Infrastructure Services (Optional)

Start optional infrastructure services using Docker Compose if needed:

```bash
docker compose -f compose.dev.yml up -d
```

This command starts the following services:

| Service | Port | Purpose |
|---------|------|---------|
| **Browserless** | 4000 | PDF/screenshot generation |

**Note**: File storage is handled by the backend API. The backend manages S3/SeaweedFS storage operations.

**Note**: This application uses the FastAPI backend for data storage. No local database setup is required. The FastAPI backend handles all database operations.

### Step 5: Verify Services are Running (Optional)

If you started infrastructure services, check that they are healthy:

```bash
docker compose -f compose.dev.yml ps
```

---

## Running the Application

### Step 6: Start the Development Server

Start the development server with hot reload:

```bash
pnpm run dev
```

The application will be available at **http://localhost:3002**

**Important**: Make sure your FastAPI backend is running and accessible. The application will communicate with the FastAPI backend for all data operations.

You should see output indicating the server is running and ready.

---

## Useful Commands

### Development

| Command | Description |
|---------|-------------|
| `pnpm run dev` | Start development server with hot reload |
| `pnpm run build` | Build the application for production |
| `pnpm run start` | Start the production server |
| `pnpm run preview` | Preview the production build locally |

### Code Quality

| Command | Description |
|---------|-------------|
| `pnpm run lint` | Run Biome linter and formatter |
| `pnpm run typecheck` | Run TypeScript type checking |

### Database

**Note**: Database commands are not available as this application uses the FastAPI backend for data storage. All database operations are handled by the backend.

### Internationalization

| Command | Description |
|---------|-------------|
| `pnpm run lingui:extract` | Extract translatable strings from code |

### Docker Services

| Command | Description |
|---------|-------------|
| `docker compose -f compose.dev.yml up -d` | Start all services in background |
| `docker compose -f compose.dev.yml down` | Stop all services |
| `docker compose -f compose.dev.yml ps` | Check service status |
| `docker compose -f compose.dev.yml logs` | View service logs |
| `docker compose -f compose.dev.yml logs -f <service>` | Follow logs for specific service |

---

## Port Configuration

### Service Ports

All services in the ApplyBots ecosystem use unique ports to avoid conflicts:

| Service | Port | Purpose | Configuration File |
|---------|------|---------|-------------------|
| **Frontend (Next.js)** | 3000 | Main application UI | `frontend/package.json` (Next.js default) |
| **Reactive Resume** | 3002 | Resume builder application | `reactive-resume/vite.config.ts` |
| **Backend (FastAPI)** | 8080 | API server | `backend/debug.py` |
| **Browserless** | 4000 | PDF/screenshot generation | `reactive-resume/compose.dev.yml` |

### Port Overrides

You can override the Reactive Resume URL in the frontend using environment variables:

- **Frontend**: Set `NEXT_PUBLIC_REACTIVE_RESUME_URL` in `frontend/.env.local`
  - Default: `http://localhost:3002`
  - Example: `NEXT_PUBLIC_REACTIVE_RESUME_URL=http://localhost:3002`

- **Reactive Resume**: Change port in `vite.config.ts` and update:
  - `APP_URL` in `reactive-resume/.env`
  - `PRINTER_APP_URL` in `reactive-resume/.env` (if using Docker)

### Port Verification

To verify ports are unique and not in use:

```bash
# Windows PowerShell
Get-NetTCPConnection -LocalPort 3000,3002,8080,4000 | Select-Object LocalPort,OwningProcess

# Linux/Mac
lsof -i :3000 -i :3002 -i :8080 -i :4000
```

---

## Access Points

Once everything is running, you can access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Reactive Resume App** | http://localhost:3002 | N/A (uses FastAPI backend) |
| **Frontend (Next.js)** | http://localhost:3000 | N/A |
| **FastAPI Backend** | http://localhost:8080 (default) | Configure via `NEXT_PUBLIC_API_URL` |

---

## Troubleshooting

### Port Already in Use

**Error**: Port 3002 (or another port) is already in use.

**Solution**: 
- Stop the process using the port, or
- Change the port in `vite.config.ts`:
  ```typescript
  server: {
    port: 3003, // Change to available port
    // ...
  }
  ```
- Update `APP_URL` and `PRINTER_APP_URL` in `.env` accordingly

### FastAPI Backend Connection Issues

**Error**: Cannot connect to FastAPI backend.

**Solutions**:
1. Verify FastAPI backend is running and accessible
2. Check `NEXT_PUBLIC_API_URL` environment variable is set correctly
3. Verify network connectivity to the backend URL
4. Check backend logs for errors

### Storage Errors

**Error**: Storage operations failing.

**Solutions**:
1. Verify backend is running and accessible
2. Check backend storage health endpoint:
   ```bash
   curl http://localhost:8080/api/v1/storage/health
   ```
3. Ensure backend S3 configuration is correct (check backend `.env` file)
4. Check backend logs for storage-related errors

### Peer Dependency Warnings

**Error**: Warnings about unmet peer dependencies (e.g., `zod@^3.23.8` or `rollup@^4`).

**Note**: These warnings have been resolved using pnpm overrides in `package.json`. The project uses:
- `zod@^4.3.6` (with zod v4 features like `z.looseObject()` and `flattenError()`)
- `rolldown-vite@latest` (which provides rollup 2.x)

The overrides ensure compatibility between packages that have different peer dependency requirements.

**Solutions**:
1. If you see peer dependency warnings after pulling changes, ensure `package.json` contains the pnpm overrides section
2. Reinstall dependencies:
   ```bash
   pnpm install
   ```

### Type Errors After Pulling Changes

**Error**: TypeScript errors after updating code.

**Solutions**:
1. The route tree may need regeneration. Start the dev server (auto-generates routes):
   ```bash
   pnpm run dev
   ```

2. Run type checking to see specific errors:
   ```bash
   pnpm run typecheck
   ```

3. Reinstall dependencies if needed:
   ```bash
   pnpm install
   ```

### Printer/PDF Generation Not Working

**Error**: PDF export fails or times out.

**Solutions**:
1. Verify Browserless is running:
   ```bash
   docker compose -f compose.dev.yml ps browserless
   ```

2. Check `PRINTER_ENDPOINT` in `.env` matches the Browserless configuration
3. Ensure `PRINTER_APP_URL` is set correctly (use `host.docker.internal` for local dev)
4. Check Browserless logs:
   ```bash
   docker compose -f compose.dev.yml logs browserless
   ```

### Docker Services Not Starting

**Error**: Services fail to start or become unhealthy.

**Solutions**:
1. Check Docker is running:
   ```bash
   docker ps
   ```

2. View all service logs:
   ```bash
   docker compose -f compose.dev.yml logs
   ```

3. Restart all services:
   ```bash
   docker compose -f compose.dev.yml down
   docker compose -f compose.dev.yml up -d
   ```

4. Check for port conflicts (each service needs its ports available)

---

## Next Steps

### Explore the Application

1. **Create an Account**: Visit http://localhost:3002 and sign up
2. **Create Your First Resume**: Use the resume builder to create a resume
3. **Explore Templates**: Try different resume templates
4. **Export to PDF**: Test the PDF export functionality

### Development

1. **Read the Architecture Docs**: Check `docs/contributing/architecture.mdx`
2. **Explore the Codebase**: Familiarize yourself with the project structure
3. **Run Tests**: Set up and run the test suite
4. **Contribute**: Check the contributing guidelines

### Backend Integration

1. **Data Storage**: All resume data is stored in the FastAPI backend database
2. **API Endpoints**: The application communicates with `/api/v1/resume-builder/drafts` endpoints
3. **Authentication**: Uses JWT tokens from the FastAPI backend

---

## Additional Resources

- **Official Documentation**: https://docs.rxresu.me
- **GitHub Repository**: https://github.com/amruthpillai/reactive-resume
- **Development Guide**: `docs/contributing/development.mdx`
- **Architecture Guide**: `docs/contributing/architecture.mdx`

---

## Support

If you encounter issues not covered in this guide:

1. Check the [official documentation](https://docs.rxresu.me)
2. Search existing [GitHub issues](https://github.com/amruthpillai/reactive-resume/issues)
3. Ask for help in the [Discord community](https://discord.gg/EE8yFqW4)
4. Create a new issue with detailed error information
.\free-port.ps1 -Port 3002 -Force
---

**Happy coding! 🚀**
