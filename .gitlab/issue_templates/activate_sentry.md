# Activate Sentry

Project information for Sentry integration:
* Client name (team name in Sentry): 
* Project Slack channel: 

Sysop activities:
* [ ] Create new Team in Sentry. Use client name as the Team name.
* [ ] Create new Project in Sentry. Use repository name as the Project name.
* [ ] Project configuration: Set alert subject template to `[${tag:environment}] $shortID - $title`.
* [ ] Project configuration: Slack integration. Set Webhook URL and destination channel.
* [ ] Project configuration: GitLab integration.
* [ ] Project configuration: Create saved searches:
  * Production (set as Team default): `is:unresolved environment:production`
  * Staging: `is:unresolved environment:staging`
* [ ] Salt: Configure Sentry DSN in local settings (found from Sentry UI at `[Project Name] -> Project Settings -> Client Keys (DSN)`)
* [ ] Salt: Configure Sentry `environment` tag in local settings.
* [ ] Salt: Configure Sentry `site` tag in local settings.
* [ ] Salt: Configure Sentry `release` data in local settings for production configuration. This should be `'release': raven.fetch_git_sha(os.path.abspath('.'))`
