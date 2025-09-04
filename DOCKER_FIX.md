# Docker Network Fix

## The Problem
Your frontend is running in Docker but trying to connect to a backend running on your host machine at `localhost:8001`. Docker containers can't reach `localhost` on the host.

## Solution Options

### Option 1: Continue with Manual Backend (Simplest)

Change the Next.js config back to use `host.docker.internal`:

```javascript
// frontend/next.config.js
{
  source: '/api/v1/:path*',
  destination: 'http://host.docker.internal:8001/api/v1/:path*',
}
```

Keep running the backend manually:
```bash
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Option 2: Use Full Docker Compose (Current setup)

The config is already set to use `http://backend:8000`. Now you need to:

1. **Stop any manual backend processes**
2. **Update the backend Docker service** to use our fixes
3. **Run the full Docker stack**

```bash
# Stop any manual backends
pkill -f "uvicorn main:app"

# Run full Docker stack
docker-compose up --build
```

## Current Status

✅ **Backend fixes applied**: Authentication disabled, OpenAI client updated, PM generation working
✅ **Frontend config updated**: Points to Docker service name `backend:8000`

## Recommendation

Use **Option 1** for now since the manual backend is working perfectly. Later you can migrate to Docker when needed.

To switch back to Option 1:
1. Change next.config.js to use `host.docker.internal:8001`
2. Restart your manual backend on port 8001
3. Restart your frontend Docker container