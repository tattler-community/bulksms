# 1.1.1 -- 2024-12-03

- Optimize encoding as TEXT whenever possible to minimize delivery cost

# 1.1.0 -- 2024-12-03

- Use BulkSMS.com's default routing group unless it's explicitly customized by user in code or envvar. This means `STANDARD` is now the default routingGroup instead of `ECONOMY`.

# 1.0.0 -- 2024-12-01

- Initial release: Add python library with tests
