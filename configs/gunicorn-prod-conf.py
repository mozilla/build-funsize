import multiprocessing

bind = ":5000"
workers = multiprocessing.cpu_count() * 2
accesslog = "/var/log/funsize/frontend_access_log.log"
user = "daemon"
