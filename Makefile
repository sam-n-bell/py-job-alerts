UV := $(shell which uv)

.PHONY: run cron

run:
	$(UV) run job-alerts

# Idempotent — removes any existing py-job-alerts cron entry before adding the current one.
cron:
	( crontab -l 2>/dev/null | grep -v 'py-job-alerts'; \
	  echo "0 */4 * * * cd $(PWD) && $(UV) run job-alerts >> /tmp/py-job-alerts.log 2>&1" \
	) | crontab -
	@echo "Cron scheduled — runs every 4 hours. Logs: /tmp/py-job-alerts.log"
