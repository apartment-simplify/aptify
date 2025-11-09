# aptify

## Deployment

Merges to `main` automatically trigger a GitHub Actions workflow that deploys the React app in `ui` to Vercel.

Add these repository secrets so the workflow can authenticate with Vercel:

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
