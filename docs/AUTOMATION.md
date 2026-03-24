# Automation

This document outlines the automation processes for ButtsStudios web games.

## Deployment Pipeline

1. **Development** - Local development with hot reload
2. **Staging** - Deployed to staging environment for testing
3. **Production** - Live deployment

## Web Game Automation

### Build & Deploy

```bash
# Build game
npm run build

# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production
```

### Testing

- Unit tests run on every push
- Integration tests on staging deploy
- Performance benchmarks for game loops

### CI/CD

GitHub Actions or similar for:
- Linting and type checking
- Running tests
- Building games
- Deploying to appropriate environments

## Client Projects

Each client project should have its own:
- Repository or subfolder in `clients/`
- Deployment pipeline
- Documentation in `clients/<project>/docs/`
