# Deployment Configuration Files

This directory contains configuration files and scripts for deploying the Task Dashboard application.

## Files Included

1. `nginx.conf` - Nginx configuration for reverse proxy and SSL termination
2. `task-dashboard.service` - Systemd service file for running the application as a service
3. `deploy.sh` - Automated deployment script that replaces placeholders with environment variables
4. `README.md` - This file with deployment instructions

## Automated Deployment (Recommended)

The easiest way to deploy is using the `deploy.sh` script which automatically replaces placeholders with your actual configuration:

1. Set the required environment variables:
   ```bash
   export DOMAIN_NAME=your-domain.com
   export SSL_CERT_PATH=/path/to/certificate.crt
   export SSL_KEY_PATH=/path/to/private.key
   export APP_PATH=/path/to/task-dashboard
   export VENV_PATH=/path/to/venv
   export SERVICE_USER=www-data
   ```

2. Run the deployment script:
   ```bash
   # Deploy both nginx and service
   ./deploy.sh all
   
   # Or deploy individually
   ./deploy.sh nginx
   ./deploy.sh service
   ```

3. Start the service:
   ```bash
   sudo systemctl start task-dashboard
   ```

## Manual Deployment Instructions

### 1. Nginx Configuration

1. Copy `nginx.conf` to `/etc/nginx/sites-available/task-dashboard`
2. Update the SSL certificate paths in the configuration file
3. Create a symbolic link to enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/task-dashboard /etc/nginx/sites-enabled/
   ```
4. Test the nginx configuration:
   ```bash
   sudo nginx -t
   ```
5. Reload nginx:
   ```bash
   sudo systemctl reload nginx
   ```

### 2. Systemd Service

1. Copy `task-dashboard.service` to `/etc/systemd/system/task-dashboard.service`
2. Update the `WorkingDirectory` and `ExecStart` paths to match your installation
3. Ensure the `www-data` user exists or change to an appropriate user
4. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable task-dashboard
   sudo systemctl start task-dashboard
   ```

### 3. SSL Certificates

For production deployment, you should obtain SSL certificates. You can use Let's Encrypt with Certbot:

```bash
sudo certbot --nginx -d your-domain.com
```

## Important Notes

- Update all paths in the configuration files to match your actual installation
- Ensure proper file permissions for security
- Test configurations in a staging environment before deploying to production
- Monitor logs for any issues after deployment