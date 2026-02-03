# Reactive Resume - Setup Guide

This guide provides step-by-step instructions for setting up Reactive Resume in a local development environment.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
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

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres

# Authentication
# ⚠️ IMPORTANT: Change this in production!
AUTH_SECRET=development-secret-change-in-production

# Storage Configuration (SeaweedFS - S3-compatible)
S3_ACCESS_KEY_ID=seaweedfs
S3_SECRET_ACCESS_KEY=seaweedfs
S3_ENDPOINT=http://localhost:8333
S3_BUCKET=reactive-resume
S3_FORCE_PATH_STYLE=true

# Email Configuration (Mailpit for local development)
SMTP_HOST=localhost
SMTP_PORT=1025
```

### Environment Variables Explained

- **APP_URL**: The base URL where your application will be accessible
- **PRINTER_APP_URL**: Required when running the app outside Docker while printer is in Docker. Uses `host.docker.internal` to allow Docker containers to reach your host machine
- **PRINTER_ENDPOINT**: WebSocket endpoint for the PDF generation service (Browserless)
- **DATABASE_URL**: PostgreSQL connection string
- **AUTH_SECRET**: Secret key for authentication (generate a secure random string for production)
- **S3_***: SeaweedFS storage configuration (S3-compatible object storage)
- **SMTP_***: Email server configuration (Mailpit captures emails for testing)

---

## Database Setup

### Step 4: Start Infrastructure Services

Start all required infrastructure services using Docker Compose:

```bash
docker compose -f compose.dev.yml up -d
```

This command starts the following services:

| Service | Port | Purpose |
|---------|------|---------|
| **PostgreSQL** | 5432 | Database |
| **SeaweedFS** | 8333 | S3-compatible storage |
| **Browserless** | 4000 | PDF/screenshot generation |
| **Mailpit** | 1025 (SMTP), 8025 (UI) | Email testing |
| **Adminer** | 8080 | Database administration UI |

### Step 5: Verify Services are Running

Check that all services are healthy:

```bash
docker compose -f compose.dev.yml ps
```

All services should show as "healthy" or "running". Wait for all services to be ready before proceeding.

### Step 6: Run Database Migrations

Apply the database schema:

```bash
pnpm run db:migrate
```

This will create all necessary database tables and schema.

---

## Running the Application

### Step 7: Start the Development Server

Start the development server with hot reload:

```bash
pnpm run dev
```

The application will be available at **http://localhost:3002**

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

| Command | Description |
|---------|-------------|
| `pnpm run db:generate` | Generate migration files from schema changes |
| `pnpm run db:migrate` | Apply pending migrations |
| `pnpm run db:studio` | Open Drizzle Studio (database GUI) |
| `pnpm run db:push` | Push schema changes directly to database |
| `pnpm run db:pull` | Pull schema from database |

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

## Access Points

Once everything is running, you can access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Reactive Resume App** | http://localhost:3002 | N/A (create account) |
| **Database Admin (Adminer)** | http://localhost:8080 | System: PostgreSQL<br>Server: postgres<br>Username: postgres<br>Password: postgres<br>Database: postgres |
| **Email Testing (Mailpit)** | http://localhost:8025 | N/A |
| **Drizzle Studio** | https://local.drizzle.studio | (Opens automatically when running `pnpm run db:studio`) |

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

### Database Connection Refused

**Error**: Cannot connect to PostgreSQL database.

**Solutions**:
1. Verify Docker containers are running:
   ```bash
   docker compose -f compose.dev.yml ps
   ```

2. Check PostgreSQL logs:
   ```bash
   docker compose -f compose.dev.yml logs postgres
   ```

3. Restart services if needed:
   ```bash
   docker compose -f compose.dev.yml restart postgres
   ```

4. Verify `DATABASE_URL` in `.env` matches the Docker Compose configuration

### S3/Storage Errors

**Error**: Storage operations failing.

**Solutions**:
1. Check SeaweedFS is running:
   ```bash
   docker compose -f compose.dev.yml logs seaweedfs
   ```

2. Verify bucket was created:
   ```bash
   docker compose -f compose.dev.yml logs seaweedfs-create-bucket
   ```

3. Restart bucket creation if needed:
   ```bash
   docker compose -f compose.dev.yml restart seaweedfs-create-bucket
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

### Database Management

1. **Use Drizzle Studio**: Run `pnpm run db:studio` for a visual database interface
2. **View Data**: Use Adminer at http://localhost:8080
3. **Make Schema Changes**: Edit schema, generate migrations, and apply them

### Email Testing

- All emails sent by the application are captured by Mailpit
- View emails at http://localhost:8025
- No real emails are sent during development

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

---

**Happy coding! 🚀**
