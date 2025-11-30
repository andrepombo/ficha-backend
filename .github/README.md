# Backend CI/CD with GitHub Actions

This directory contains GitHub Actions workflows for automated deployment.

## Workflow: `deploy.yml`

Automatically deploys the Django backend to EC2 when code is pushed to the `main` branch.

### What it does:

1. ✅ Pulls latest code from GitHub
2. ✅ Installs Python dependencies
3. ✅ Runs database migrations
4. ✅ Collects static files
5. ✅ Restarts Gunicorn service
6. ✅ Verifies deployment success

### Required GitHub Secrets:

Set these in **Settings → Secrets and variables → Actions**:

- `EC2_HOST` - Your EC2 IP address or domain
- `EC2_USERNAME` - SSH username (e.g., `ubuntu`)
- `EC2_SSH_KEY` - Private SSH key for EC2 access

### Manual Deployment:

1. Go to **Actions** tab in GitHub
2. Select "Deploy Backend to EC2"
3. Click **Run workflow**
4. Choose branch and click **Run workflow**

### Monitoring:

View deployment logs in the **Actions** tab of your repository.

### Troubleshooting:

If deployment fails:
1. Check the Actions log for error messages
2. Verify GitHub secrets are correctly set
3. Ensure EC2 SSH key has proper permissions
4. Check that the EC2 user has sudo access for systemctl

For detailed setup instructions, see `GITHUB_ACTIONS_SETUP.md` in the root directory.
