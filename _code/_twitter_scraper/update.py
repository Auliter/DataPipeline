from crontab import CronTab

cron = CronTab(user="DE4QF")

job = cron.new(command='/parallel_search_with_limit.py')
job.setall('0 6 *')  # Run at 6:00 AM every day

cron.write()